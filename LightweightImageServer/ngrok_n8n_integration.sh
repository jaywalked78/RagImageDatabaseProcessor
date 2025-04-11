#!/bin/bash
# ngrok_n8n_integration.sh - Stable integration of ngrok with LightweightImageServer
# This script replaces localtunnel with ngrok for more reliable public URLs

# Configuration
MAX_LOG_SIZE=10000000  # 10MB max log size
MAX_RESTART_ATTEMPTS=3
MAX_CHILD_PROCESSES=3
LOCK_FILE="/tmp/ngrok_lock"
PID_DIR="/tmp/ngrok_pids"
PORT=7779
MAX_RUNTIME=43200  # 12 hours max runtime
KEEPALIVE_INTERVAL=300  # 5 minutes between health checks

# Create PID directory
mkdir -p $PID_DIR

# Check for existing lock to prevent multiple instances
if [ -f "$LOCK_FILE" ]; then
  LOCK_PID=$(cat "$LOCK_FILE")
  if ps -p $LOCK_PID > /dev/null; then
    echo "Another ngrok script is already running with PID $LOCK_PID"
    exit 1
  else
    echo "Removing stale lock file"
    rm -f "$LOCK_FILE"
  fi
fi

# Create lock file
echo $$ > "$LOCK_FILE"

# Setup cleanup trap for graceful exit
cleanup() {
  echo "Cleaning up processes and files..."
  # Kill all child processes
  for pid_file in $PID_DIR/*.pid; do
    if [ -f "$pid_file" ]; then
      PID=$(cat "$pid_file")
      kill $PID 2>/dev/null || true
      rm -f "$pid_file"
    fi
  done
  
  # Kill ngrok
  pkill -f "ngrok http $PORT" || true
  
  # Remove lock file
  rm -f "$LOCK_FILE"
  exit 0
}
trap cleanup EXIT INT TERM

# Log rotation function
rotate_log() {
  local log_file=$1
  if [ -f "$log_file" ] && [ $(stat -c%s "$log_file") -gt $MAX_LOG_SIZE ]; then
    mv "$log_file" "${log_file}.old"
    touch "$log_file"
  fi
}

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
  echo "ERROR: ngrok is not installed"
  echo "Please install ngrok from https://ngrok.com/download"
  echo "Then authenticate with: ngrok config add-authtoken YOUR_TOKEN"
  exit 1
fi

# Check if the image server is already running
check_server() {
  if curl -s http://localhost:$PORT &> /dev/null; then
    return 0  # Server is running
  else
    return 1  # Server is not running
  fi
}

# Start the LightweightImageServer
echo "Starting image server..."
cd /home/jason/Documents/DatabaseAdvancedTokenizer/LightweightImageServer

if check_server; then
  echo "Image server is already running on port $PORT"
else
  echo "Starting image server..."
  ./persistent_run.sh &
  SERVER_PID=$!
  echo $SERVER_PID > "$PID_DIR/server.pid"
  echo "Server started with PID: $SERVER_PID"
  
  # Wait for server to initialize
  echo "Waiting for server to initialize..."
  for i in {1..10}; do
    if check_server; then
      echo "Server initialized successfully"
      break
    fi
    echo "Waiting... ($i/10)"
    sleep 1
    
    if [ $i -eq 10 ]; then
      echo "Failed to start server. Check logs for details."
      cleanup
      exit 1
    fi
  done
fi

# Start ngrok monitor script
cat > /tmp/ngrok_monitor.sh << 'EOL'
#!/bin/bash
PORT="$1"
LOG_FILE="/tmp/ngrok_monitor.log"
PID_DIR="/tmp/ngrok_pids"
RESTART_COUNT=0
MAX_RESTARTS=3
MAX_LOG_SIZE=5000000  # 5MB
KEEPALIVE_INTERVAL=300  # 5 minutes
MAX_RUNTIME=43200  # 12 hours

# Rotate log if needed
if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
  mv "$LOG_FILE" "${LOG_FILE}.old"
fi

echo "=== Starting ngrok monitor at $(date) ===" > $LOG_FILE

start_ngrok() {
  # Check restart limit
  if [ $RESTART_COUNT -ge $MAX_RESTARTS ]; then
    echo "$(date): Maximum restart attempts reached ($RESTART_COUNT). Exiting." | tee -a $LOG_FILE
    exit 1
  fi
  
  # Kill any existing ngrok for this port
  pkill -f "ngrok http $PORT" || true
  sleep 2
  
  # Start ngrok
  echo "$(date): Starting ngrok for port $PORT" | tee -a $LOG_FILE
  ngrok http $PORT --log=stdout > /tmp/ngrok_log.txt 2>&1 &
  NGROK_PID=$!
  echo $NGROK_PID > "$PID_DIR/ngrok.pid"
  
  # Increment restart counter
  RESTART_COUNT=$((RESTART_COUNT + 1))
  
  # Give ngrok time to establish connection
  sleep 5
  
  # Extract the URL using the ngrok API
  NGROK_URL=""
  for i in {1..5}; do
    NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*"' | head -n 1 | cut -d'"' -f4)
    if [ -n "$NGROK_URL" ]; then
      break
    fi
    sleep 2
  done
  
  if [ -z "$NGROK_URL" ]; then
    echo "$(date): Failed to get ngrok URL after multiple attempts" | tee -a $LOG_FILE
    return 1
  fi
  
  echo "$(date): Ngrok started with PID: $NGROK_PID" | tee -a $LOG_FILE
  echo "$(date): Tunnel URL: $NGROK_URL" | tee -a $LOG_FILE
  echo "$NGROK_URL" > /tmp/current_ngrok_url.txt
  
  return 0
}

# Cleanup function
cleanup() {
  echo "$(date): Monitor shutting down, cleaning up processes" | tee -a $LOG_FILE
  pkill -f "ngrok http $PORT" || true
  rm -f $PID_DIR/ngrok.pid
  exit 0
}
trap cleanup EXIT INT TERM

# Start initial ngrok tunnel
start_ngrok
RUNTIME=0

# Health check loop
while [ $RUNTIME -lt $MAX_RUNTIME ]; do
  # Check log file size and rotate if needed
  if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
    mv "$LOG_FILE" "${LOG_FILE}.old"
    echo "=== Log rotated at $(date) ===" > $LOG_FILE
  fi
  
  # Check if ngrok is still running
  if [ -f "$PID_DIR/ngrok.pid" ]; then
    NGROK_PID=$(cat "$PID_DIR/ngrok.pid")
    if ! ps -p $NGROK_PID > /dev/null; then
      echo "$(date): Ngrok process died, restarting..." | tee -a $LOG_FILE
      start_ngrok
    fi
  else
    echo "$(date): Ngrok PID file missing, restarting..." | tee -a $LOG_FILE
    start_ngrok
  fi
  
  # Check if ngrok tunnel is still working by checking the API
  TUNNEL_COUNT=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url"' | wc -l)
  if [ "$TUNNEL_COUNT" -eq 0 ]; then
    echo "$(date): No active tunnels found, restarting ngrok..." | tee -a $LOG_FILE
    start_ngrok
  fi
  
  # Check memory usage
  if [ -f "$PID_DIR/ngrok.pid" ]; then
    NGROK_PID=$(cat "$PID_DIR/ngrok.pid")
    if ps -p $NGROK_PID > /dev/null; then
      MEM_USAGE=$(ps -o rss= -p $NGROK_PID)
      # If using more than 200MB, restart it
      if [ $MEM_USAGE -gt 204800 ]; then
        echo "$(date): Ngrok using excessive memory ($MEM_USAGE KB), restarting" | tee -a $LOG_FILE
        start_ngrok
      fi
    fi
  fi
  
  # Send health check request to keep tunnel active
  if [ -f "/tmp/current_ngrok_url.txt" ]; then
    NGROK_URL=$(cat /tmp/current_ngrok_url.txt)
    if [ -n "$NGROK_URL" ]; then
      echo "$(date): Sending health check to $NGROK_URL" >> $LOG_FILE
      curl -s -m 10 "$NGROK_URL" -o /dev/null || echo "$(date): Health check failed" >> $LOG_FILE
    fi
  fi
  
  # Sleep for interval
  sleep $KEEPALIVE_INTERVAL
  
  # Increment runtime
  RUNTIME=$((RUNTIME + KEEPALIVE_INTERVAL))
done

echo "$(date): Maximum runtime reached, exiting monitor" | tee -a $LOG_FILE
cleanup
EOL

chmod +x /tmp/ngrok_monitor.sh

# Start ngrok with monitor
echo "Starting ngrok with monitoring..."
nohup /tmp/ngrok_monitor.sh "$PORT" > /tmp/ngrok_startup.log 2>&1 &
MONITOR_PID=$!
echo $MONITOR_PID > "$PID_DIR/main_monitor.pid"

echo "Waiting for ngrok to establish..."
sleep 8

# Get the URL from the monitor's output
if [ -f "/tmp/current_ngrok_url.txt" ]; then
  NGROK_URL=$(cat /tmp/current_ngrok_url.txt)
  echo "Ngrok URL: $NGROK_URL"
else
  echo "ERROR: Could not get ngrok URL"
  cat /tmp/ngrok_startup.log
  cleanup
  exit 1
fi

# Verify ngrok is working
echo "Verifying ngrok connection..."
VERIFY_RESULT=$(curl -s -L -m 10 -o /dev/null -w "%{http_code}" "$NGROK_URL")
if [ "$VERIFY_RESULT" = "200" ] || [ "$VERIFY_RESULT" = "404" ]; then
  echo "NGROK_VERIFIED=YES"
  echo "HTTP Status: $VERIFY_RESULT"
else
  echo "NGROK_VERIFIED=NO"
  echo "HTTP Status: $VERIFY_RESULT"
  
  # Try to diagnose
  echo "Trying to diagnose issues..."
  curl -s -v "$NGROK_URL" > /tmp/ngrok_debug.log 2>&1
  echo "Debug log saved to /tmp/ngrok_debug.log"
fi

# Check ngrok web interface
NGROK_DASHBOARD=$(curl -s http://localhost:4040/api/tunnels | grep -o '"web_addr":[^,}]*' | cut -d'"' -f3)
echo "Ngrok Web Interface: $NGROK_DASHBOARD"

# Output for n8n to parse
echo "NGROK_URL=$NGROK_URL"
echo "SERVER_PID=$(cat $PID_DIR/server.pid 2>/dev/null || echo 'unknown')"
echo "MONITOR_PID=$MONITOR_PID"
echo "NGROK_PID=$(cat $PID_DIR/ngrok.pid 2>/dev/null || echo 'unknown')"
echo "NGROK_WEB_INTERFACE=http://localhost:4040"

# Important usage notes
echo ""
echo "=================== USAGE NOTES ==================="
echo "1. The ngrok URL is: $NGROK_URL"
echo "2. To stop all services: kill $MONITOR_PID"
echo "3. To view ngrok status: http://localhost:4040"
echo "4. This tunnel will automatically renew if disconnected"
echo "5. Total maximum runtime: 12 hours"
echo "6. Logs can be found at:"
echo "   - /tmp/ngrok_monitor.log (monitor logs)"
echo "   - /tmp/ngrok_log.txt (ngrok process logs)"
echo "=================================================="

# Release lock when done
# (Lock will be released by cleanup trap when process exits) 