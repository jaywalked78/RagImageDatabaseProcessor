#!/bin/bash
# ngrok_n8n_integration.sh - Stable integration of ngrok with LightweightImageServer
# This script replaces localtunnel with ngrok for more reliable public URLs

# Check if running from n8n
if [[ "$1" == "--n8n" ]]; then
  # Run the script in background and poll for URL file
  nohup bash "$0" > /tmp/ngrok_complete_output.log 2>&1 &
  BG_PID=$!
  
  # Wait for URL file with timeout
  MAX_WAIT=30
  for i in $(seq 1 $MAX_WAIT); do
    if [ -f "/tmp/current_ngrok_url.txt" ]; then
      NGROK_URL=$(cat /tmp/current_ngrok_url.txt)
      echo "NGROK_URL=$NGROK_URL"
      echo "MONITOR_PID=$BG_PID"
      echo "Success=true"
      exit 0
    fi
    sleep 1
    echo "Waiting for ngrok to initialize ($i/$MAX_WAIT)..." >&2
  done
  
  echo "Error: Timed out waiting for ngrok URL" >&2
  echo "Success=false"
  exit 1
fi

# Configuration
MAX_LOG_SIZE=10000000  # 10MB max log size
MAX_RESTART_ATTEMPTS=3
MAX_CHILD_PROCESSES=3
LOCK_FILE="/tmp/ngrok_lock"
PID_DIR="/tmp/ngrok_pids"
PORT=7779
MAX_RUNTIME=43200  # 12 hours max runtime
KEEPALIVE_INTERVAL=300  # 5 minutes between health checks

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create PID directory
mkdir -p $PID_DIR

# Check for existing lock to prevent multiple instances
if [ -f "$LOCK_FILE" ]; then
  LOCK_PID=$(cat "$LOCK_FILE")
  if ps -p $LOCK_PID > /dev/null; then
    echo -e "${RED}Another ngrok script is already running with PID $LOCK_PID${NC}"
    
    # If lock exists but we can get the URL, just return it (for n8n integration)
    if [ -f "/tmp/current_ngrok_url.txt" ]; then
      NGROK_URL=$(cat /tmp/current_ngrok_url.txt)
      if [ -n "$NGROK_URL" ]; then
        echo -e "${GREEN}Using existing ngrok tunnel${NC}"
        echo "NGROK_URL=$NGROK_URL"
        echo "SERVER_PID=$(cat $PID_DIR/server.pid 2>/dev/null || echo 'unknown')"
        echo "MONITOR_PID=$LOCK_PID"
        echo "NGROK_WEB_INTERFACE=http://localhost:4040"
        exit 0
      fi
    fi
    
    exit 1
  else
    echo -e "${YELLOW}Removing stale lock file${NC}"
    rm -f "$LOCK_FILE"
  fi
fi

# Create lock file
echo $$ > "$LOCK_FILE"

# Setup cleanup trap for graceful exit
cleanup() {
  echo -e "${BLUE}Cleaning up processes and files...${NC}"
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
  echo -e "${RED}ERROR: ngrok is not installed${NC}"
  echo -e "${YELLOW}Please install ngrok from https://ngrok.com/download${NC}"
  echo -e "${YELLOW}Then use ./setup_ngrok.sh to authenticate${NC}"
  exit 1
fi

# Check if ngrok is authenticated
AUTH_CHECK=$(ngrok config check 2>&1)
if echo "$AUTH_CHECK" | grep -q "error"; then
  echo -e "${RED}ERROR: ngrok is not properly authenticated${NC}"
  echo -e "${YELLOW}Please run ./setup_ngrok.sh to authenticate ngrok${NC}"
  echo -e "${BLUE}Or manually run: ngrok config add-authtoken YOUR_TOKEN${NC}"
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
echo -e "${BLUE}Starting image server...${NC}"
cd /home/jason/Documents/DatabaseAdvancedTokenizer/LightweightImageServer

if check_server; then
  echo -e "${GREEN}Image server is already running on port $PORT${NC}"
else
  echo -e "${BLUE}Starting image server...${NC}"
  ./persistent_run.sh &
  SERVER_PID=$!
  echo $SERVER_PID > "$PID_DIR/server.pid"
  echo -e "${GREEN}Server started with PID: $SERVER_PID${NC}"
  
  # Wait for server to initialize
  echo -e "${BLUE}Waiting for server to initialize...${NC}"
  for i in {1..10}; do
    if check_server; then
      echo -e "${GREEN}Server initialized successfully${NC}"
      break
    fi
    echo -e "${YELLOW}Waiting... ($i/10)${NC}"
    sleep 1
    
    if [ $i -eq 10 ]; then
      echo -e "${RED}Failed to start server. Check logs for details.${NC}"
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

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Rotate log if needed
if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
  mv "$LOG_FILE" "${LOG_FILE}.old"
fi

echo -e "${BLUE}=== Starting ngrok monitor at $(date) ===${NC}" > $LOG_FILE

start_ngrok() {
  # Check restart limit
  if [ $RESTART_COUNT -ge $MAX_RESTARTS ]; then
    echo -e "$(date): ${RED}Maximum restart attempts reached ($RESTART_COUNT). Exiting.${NC}" | tee -a $LOG_FILE
    exit 1
  fi
  
  # Kill any existing ngrok for this port
  pkill -f "ngrok http $PORT" || true
  sleep 2
  
  # Start ngrok
  echo -e "$(date): ${BLUE}Starting ngrok for port $PORT${NC}" | tee -a $LOG_FILE
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
    echo -e "$(date): ${RED}Failed to get ngrok URL after multiple attempts${NC}" | tee -a $LOG_FILE
    return 1
  fi
  
  echo -e "$(date): ${GREEN}Ngrok started with PID: $NGROK_PID${NC}" | tee -a $LOG_FILE
  echo -e "$(date): ${GREEN}Tunnel URL: $NGROK_URL${NC}" | tee -a $LOG_FILE
  echo "$NGROK_URL" > /tmp/current_ngrok_url.txt
  
  return 0
}

# Cleanup function
cleanup() {
  echo -e "$(date): ${BLUE}Monitor shutting down, cleaning up processes${NC}" | tee -a $LOG_FILE
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
    echo -e "${BLUE}=== Log rotated at $(date) ===${NC}" > $LOG_FILE
  fi
  
  # Check if ngrok is still running
  if [ -f "$PID_DIR/ngrok.pid" ]; then
    NGROK_PID=$(cat "$PID_DIR/ngrok.pid")
    if ! ps -p $NGROK_PID > /dev/null; then
      echo -e "$(date): ${YELLOW}Ngrok process died, restarting...${NC}" | tee -a $LOG_FILE
      start_ngrok
    fi
  else
    echo -e "$(date): ${YELLOW}Ngrok PID file missing, restarting...${NC}" | tee -a $LOG_FILE
    start_ngrok
  fi
  
  # Check if ngrok tunnel is still working by checking the API
  TUNNEL_COUNT=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url"' | wc -l)
  if [ "$TUNNEL_COUNT" -eq 0 ]; then
    echo -e "$(date): ${YELLOW}No active tunnels found, restarting ngrok...${NC}" | tee -a $LOG_FILE
    start_ngrok
  fi
  
  # Check memory usage
  if [ -f "$PID_DIR/ngrok.pid" ]; then
    NGROK_PID=$(cat "$PID_DIR/ngrok.pid")
    if ps -p $NGROK_PID > /dev/null; then
      MEM_USAGE=$(ps -o rss= -p $NGROK_PID)
      # If using more than 200MB, restart it
      if [ $MEM_USAGE -gt 204800 ]; then
        echo -e "$(date): ${YELLOW}Ngrok using excessive memory ($MEM_USAGE KB), restarting${NC}" | tee -a $LOG_FILE
        start_ngrok
      fi
    fi
  fi
  
  # Send health check request to keep tunnel active
  if [ -f "/tmp/current_ngrok_url.txt" ]; then
    NGROK_URL=$(cat /tmp/current_ngrok_url.txt)
    if [ -n "$NGROK_URL" ]; then
      echo -e "$(date): ${BLUE}Sending health check to $NGROK_URL${NC}" >> $LOG_FILE
      curl -s -m 10 "$NGROK_URL" -o /dev/null || echo -e "$(date): ${RED}Health check failed${NC}" >> $LOG_FILE
    fi
  fi
  
  # Sleep for interval
  sleep $KEEPALIVE_INTERVAL
  
  # Increment runtime
  RUNTIME=$((RUNTIME + KEEPALIVE_INTERVAL))
done

echo -e "$(date): ${YELLOW}Maximum runtime reached, exiting monitor${NC}" | tee -a $LOG_FILE
cleanup
EOL

chmod +x /tmp/ngrok_monitor.sh

# Start ngrok with monitor
echo -e "${BLUE}Starting ngrok with monitoring...${NC}"
nohup /tmp/ngrok_monitor.sh "$PORT" > /tmp/ngrok_startup.log 2>&1 &
MONITOR_PID=$!
echo $MONITOR_PID > "$PID_DIR/main_monitor.pid"

echo -e "${BLUE}Waiting for ngrok to establish...${NC}"
sleep 8

# Get the URL from the monitor's output
if [ -f "/tmp/current_ngrok_url.txt" ]; then
  NGROK_URL=$(cat /tmp/current_ngrok_url.txt)
  echo -e "${GREEN}Ngrok URL: $NGROK_URL${NC}"
else
  echo -e "${RED}ERROR: Could not get ngrok URL${NC}"
  cat /tmp/ngrok_startup.log
  cleanup
  exit 1
fi

# Verify ngrok is working
echo -e "${BLUE}Verifying ngrok connection...${NC}"
VERIFY_RESULT=$(curl -s -L -m 10 -o /dev/null -w "%{http_code}" "$NGROK_URL")
if [ "$VERIFY_RESULT" = "200" ] || [ "$VERIFY_RESULT" = "404" ]; then
  echo -e "${GREEN}NGROK_VERIFIED=YES${NC}"
  echo -e "${GREEN}HTTP Status: $VERIFY_RESULT${NC}"
else
  echo -e "${RED}NGROK_VERIFIED=NO${NC}"
  echo -e "${RED}HTTP Status: $VERIFY_RESULT${NC}"
  
  # Try to diagnose
  echo -e "${YELLOW}Trying to diagnose issues...${NC}"
  curl -s -v "$NGROK_URL" > /tmp/ngrok_debug.log 2>&1
  echo -e "${YELLOW}Debug log saved to /tmp/ngrok_debug.log${NC}"
fi

# Check ngrok web interface
NGROK_DASHBOARD=$(curl -s http://localhost:4040/api/tunnels | grep -o '"web_addr":[^,}]*' | cut -d'"' -f3)
echo -e "${BLUE}Ngrok Web Interface: $NGROK_DASHBOARD${NC}"

# Output for n8n to parse - always ensure these are printed without colors
echo "NGROK_URL=$NGROK_URL"
echo "SERVER_PID=$(cat $PID_DIR/server.pid 2>/dev/null || echo 'unknown')"
echo "MONITOR_PID=$MONITOR_PID"
echo "NGROK_PID=$(cat $PID_DIR/ngrok.pid 2>/dev/null || echo 'unknown')"
echo "NGROK_WEB_INTERFACE=http://localhost:4040"

# Important usage notes
echo ""
echo -e "${BLUE}=================== USAGE NOTES ===================${NC}"
echo -e "${GREEN}1. The ngrok URL is: $NGROK_URL${NC}"
echo -e "${GREEN}2. To stop all services: kill $MONITOR_PID${NC}"
echo -e "${GREEN}3. To view ngrok status: http://localhost:4040${NC}"
echo -e "${GREEN}4. This tunnel will automatically renew if disconnected${NC}"
echo -e "${GREEN}5. Total maximum runtime: 12 hours${NC}"
echo -e "${GREEN}6. Logs can be found at:${NC}"
echo -e "   ${BLUE}- /tmp/ngrok_monitor.log (monitor logs)${NC}"
echo -e "   ${BLUE}- /tmp/ngrok_log.txt (ngrok process logs)${NC}"
echo -e "${BLUE}==================================================${NC}"

# Release lock when done
# (Lock will be released by cleanup trap when process exits) 