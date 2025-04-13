#!/bin/bash
# n8n_shell_script.sh - With resource monitoring and safety constraints

# Configuration
MAX_LOG_SIZE=10000000  # 10MB max log size
MAX_RESTART_ATTEMPTS=5
MAX_CHILD_PROCESSES=5
LOCK_FILE="/tmp/tunnel_lock"
PID_DIR="/tmp/tunnel_pids"

# Create PID directory
mkdir -p $PID_DIR

# Check for existing lock to prevent multiple instances
if [ -f "$LOCK_FILE" ]; then
  LOCK_PID=$(cat "$LOCK_FILE")
  if ps -p $LOCK_PID > /dev/null; then
    echo "Another tunnel script is already running with PID $LOCK_PID"
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

# Process monitoring function
check_processes() {
  # Count running monitor processes
  PROCESS_COUNT=$(pgrep -f "ip_auth_monitor.sh" | wc -l)
  if [ $PROCESS_COUNT -gt $MAX_CHILD_PROCESSES ]; then
    echo "WARNING: Too many monitoring processes ($PROCESS_COUNT). Cleaning up excessive processes."
    # Kill newest processes, keeping the oldest ones
    pgrep -f "ip_auth_monitor.sh" | sort -r | tail -n +$MAX_CHILD_PROCESSES | xargs kill 2>/dev/null
  fi
}

# Start the server
cd /home/jason/Documents/DatabaseAdvancedTokenizer/LightweightImageServer
nohup ./start_publicserver.sh > /tmp/publicapi_output.log 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > "$PID_DIR/server.pid"
echo "Server started with PID: $SERVER_PID"

# Give the server a moment to start
sleep 3

# Create IP auth monitor script with resource limitations
cat > /tmp/ip_auth_monitor.sh << 'EOL'
#!/bin/bash

# Configuration
TUNNEL_URL="$1"
CHECK_INTERVAL=20  # Check every 20 seconds
LOG_FILE="/tmp/tunnel_ip_auth.log"
MONITOR_PID_FILE="$2"
MAX_LOG_SIZE=5000000  # 5MB

# Write our PID to file
echo $$ > "$MONITOR_PID_FILE"

# Rotate log if needed
if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
  mv "$LOG_FILE" "${LOG_FILE}.old"
fi

echo "=== Starting IP authentication monitor at $(date) ===" > $LOG_FILE
echo "Monitoring URL: $TUNNEL_URL (PID: $$)" >> $LOG_FILE

# Store cookies
COOKIE_JAR="/tmp/tunnel_cookies_$$.txt"
touch $COOKIE_JAR

# Function to get our public IP
get_public_ip() {
  # Try multiple IP services with timeout to prevent hanging
  IP=$(timeout 5s curl -s https://ipv4.icanhazip.com || 
       timeout 5s curl -s https://api.ipify.org || 
       timeout 5s curl -s https://ifconfig.me)
  
  # Validate IP format (basic check)
  if [[ $IP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "$IP" | tr -d '\n'
    return 0
  else
    return 1
  fi
}

# Function to check if tunnel needs IP authentication
check_ip_auth() {
  # Use timeout to prevent hanging
  RESPONSE=$(timeout 10s curl -s -L -c $COOKIE_JAR "$TUNNEL_URL" -o /tmp/auth_page_$$.html -w "%{http_code}")
  
  # Check if it's asking for endpoint IP
  if [ -f "/tmp/auth_page_$$.html" ] && grep -q "Endpoint IP" "/tmp/auth_page_$$.html"; then
    echo "$(date): IP authentication form detected" >> $LOG_FILE
    return 0  # Needs IP auth
  elif [ "$RESPONSE" = "200" ]; then
    echo "$(date): No authentication required, access successful" >> $LOG_FILE
    return 1  # No auth needed
  else
    echo "$(date): Response code: $RESPONSE" >> $LOG_FILE
    return 0  # Assume auth needed to be safe
  fi
}

# Function to submit IP authentication
submit_ip_auth() {
  # Get our current public IP with retry
  PUBLIC_IP=""
  for i in {1..3}; do
    if PUBLIC_IP=$(get_public_ip); then
      break
    fi
    sleep 1
  done
  
  if [ -z "$PUBLIC_IP" ]; then
    echo "$(date): Failed to get public IP after 3 attempts" >> $LOG_FILE
    return 1
  fi
  
  echo "$(date): Got public IP: $PUBLIC_IP" >> $LOG_FILE
  
  # Extract any form tokens
  CSRF_TOKEN=""
  if [ -f "/tmp/auth_page_$$.html" ]; then
    CSRF_TOKEN=$(grep -o 'name="csrf_token" value="[^"]*"' "/tmp/auth_page_$$.html" | cut -d'"' -f4)
  fi
  
  # Build form data
  FORM_DATA="ip=$PUBLIC_IP"
  if [ -n "$CSRF_TOKEN" ]; then
    FORM_DATA="$FORM_DATA&csrf_token=$CSRF_TOKEN"
  fi
  
  # Submit the form with the IP
  echo "$(date): Submitting IP authentication form" >> $LOG_FILE
  timeout 10s curl -s -L -b $COOKIE_JAR -c $COOKIE_JAR \
    -d "$FORM_DATA" \
    "$TUNNEL_URL" -o "/tmp/post_auth_$$.html"
  
  # Check if it worked by testing access to an image
  TEST_RESULT=$(timeout 10s curl -s -L -b $COOKIE_JAR -o /dev/null -w "%{http_code}" "$TUNNEL_URL/images/frame_000001.jpg")
  
  if [ "$TEST_RESULT" = "200" ] || [ "$TEST_RESULT" = "404" ]; then
    echo "$(date): IP Authentication SUCCESS with IP: $PUBLIC_IP" >> $LOG_FILE
    return 0  # Authentication successful
  else
    echo "$(date): IP Authentication FAILED with IP: $PUBLIC_IP (HTTP $TEST_RESULT)" >> $LOG_FILE
    return 1  # Authentication failed
  fi
}

# Cleanup function
cleanup() {
  echo "$(date): Monitor shutting down" >> $LOG_FILE
  rm -f $COOKIE_JAR
  rm -f "/tmp/auth_page_$$.html"
  rm -f "/tmp/post_auth_$$.html"
  rm -f "$MONITOR_PID_FILE"
  exit 0
}
trap cleanup EXIT INT TERM

# Error counter
ERROR_COUNT=0
MAX_ERRORS=10

# Main monitoring loop
while true; do
  # Check file size and rotate if needed
  if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
    mv "$LOG_FILE" "${LOG_FILE}.old"
    echo "=== Log rotated at $(date) ===" > $LOG_FILE
  fi
  
  # Check for auth requirement
  if ! check_ip_auth; then
    # No auth needed or check failed
    ERROR_COUNT=0  # Reset error counter on success
  else
    echo "$(date): IP authentication required, submitting IP..." >> $LOG_FILE
    if ! submit_ip_auth; then
      ERROR_COUNT=$((ERROR_COUNT + 1))
      echo "$(date): Authentication attempt failed ($ERROR_COUNT/$MAX_ERRORS)" >> $LOG_FILE
      
      # If too many errors, exit to prevent resource drain
      if [ $ERROR_COUNT -ge $MAX_ERRORS ]; then
        echo "$(date): Too many consecutive errors, exiting monitor" >> $LOG_FILE
        cleanup
      fi
    else
      ERROR_COUNT=0  # Reset error counter on success
    fi
  fi
  
  # Make a request to keep the tunnel alive
  timeout 10s curl -s -L -b $COOKIE_JAR "$TUNNEL_URL" -o /dev/null
  
  # Wait before checking again
  sleep $CHECK_INTERVAL
done
EOL

chmod +x /tmp/ip_auth_monitor.sh

# Create the main tunnel monitor with resource checks
cat > /tmp/tunnel_monitor.sh << 'EOL'
#!/bin/bash
PORT=7779
SUBDOMAIN="$1"
KEEPALIVE_INTERVAL=60  # Send a keep-alive every minute
MAX_RUNTIME=10800      # 3 hours max runtime
PID_DIR="/tmp/tunnel_pids"
RESTART_COUNT=0
MAX_RESTARTS=5
LOG_FILE="/tmp/tunnel_monitor.log"
MAX_LOG_SIZE=5000000  # 5MB

# Rotate log if needed
if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
  mv "$LOG_FILE" "${LOG_FILE}.old"
fi

echo "=== Starting tunnel monitor at $(date) ===" > $LOG_FILE

start_tunnel() {
  # Check restart limit
  if [ $RESTART_COUNT -ge $MAX_RESTARTS ]; then
    echo "$(date): Maximum restart attempts reached ($RESTART_COUNT). Exiting." | tee -a $LOG_FILE
    exit 1
  fi
  
  # Kill any existing tunnels for this port
  pkill -f "lt --port $PORT" || true
  
  # Start tunnel with specific subdomain
  lt --port $PORT --subdomain $SUBDOMAIN > /tmp/tunnel_info.txt 2>&1 &
  TUNNEL_PID=$!
  echo $TUNNEL_PID > "$PID_DIR/tunnel.pid"
  echo "$(date): Started tunnel with PID: $TUNNEL_PID" | tee -a $LOG_FILE
  
  # Increment restart counter
  RESTART_COUNT=$((RESTART_COUNT + 1))
  
  # Extract URL
  sleep 5
  TUNNEL_URL=$(grep -o "https://[^[:space:]]*" /tmp/tunnel_info.txt | head -n 1)
  if [ -z "$TUNNEL_URL" ]; then
    echo "$(date): Failed to get tunnel URL" | tee -a $LOG_FILE
    return 1
  fi
  echo "$(date): Tunnel URL: $TUNNEL_URL" | tee -a $LOG_FILE
  echo "$TUNNEL_URL" > /tmp/current_tunnel_url.txt
  
  # Clean up any old auth monitors
  pkill -f "ip_auth_monitor.sh" || true
  sleep 1
  
  # Start the IP authentication monitor in the background
  AUTH_MONITOR_PID_FILE="$PID_DIR/auth_monitor.pid"
  nohup /tmp/ip_auth_monitor.sh "$TUNNEL_URL" "$AUTH_MONITOR_PID_FILE" > /dev/null 2>&1 &
  
  # Wait a moment for PID file to be created
  sleep 2
  if [ -f "$AUTH_MONITOR_PID_FILE" ]; then
    AUTH_MONITOR_PID=$(cat "$AUTH_MONITOR_PID_FILE")
    echo "$(date): Started IP authentication monitor with PID: $AUTH_MONITOR_PID" | tee -a $LOG_FILE
  else
    echo "$(date): Warning: Failed to start IP authentication monitor" | tee -a $LOG_FILE
  fi
  
  return 0
}

# Cleanup function
cleanup() {
  echo "$(date): Monitor shutting down, cleaning up processes" | tee -a $LOG_FILE
  pkill -f "lt --port $PORT" || true
  pkill -f "ip_auth_monitor.sh" || true
  rm -f $PID_DIR/tunnel.pid
  rm -f $PID_DIR/auth_monitor.pid
  exit 0
}
trap cleanup EXIT INT TERM

# Start initial tunnel
start_tunnel
RUNTIME=0

# Keep-alive loop
while [ $RUNTIME -lt $MAX_RUNTIME ]; do
  # Check log file size and rotate if needed
  if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]; then
    mv "$LOG_FILE" "${LOG_FILE}.old"
    echo "=== Log rotated at $(date) ===" > $LOG_FILE
  fi
  
  # Check if tunnel is still running
  if [ -f "$PID_DIR/tunnel.pid" ]; then
    TUNNEL_PID=$(cat "$PID_DIR/tunnel.pid")
    if ! ps -p $TUNNEL_PID > /dev/null; then
      echo "$(date): Tunnel process died, restarting..." | tee -a $LOG_FILE
      start_tunnel
    fi
  else
    echo "$(date): Tunnel PID file missing, restarting..." | tee -a $LOG_FILE
    start_tunnel
  fi
  
  # Check if auth monitor is still running
  if [ -f "$PID_DIR/auth_monitor.pid" ]; then
    AUTH_MONITOR_PID=$(cat "$PID_DIR/auth_monitor.pid")
    if ! ps -p $AUTH_MONITOR_PID > /dev/null; then
      echo "$(date): Auth monitor died, restarting..." | tee -a $LOG_FILE
      
      # Start the IP authentication monitor in the background
      AUTH_MONITOR_PID_FILE="$PID_DIR/auth_monitor.pid"
      TUNNEL_URL=$(cat /tmp/current_tunnel_url.txt 2>/dev/null)
      if [ -n "$TUNNEL_URL" ]; then
        nohup /tmp/ip_auth_monitor.sh "$TUNNEL_URL" "$AUTH_MONITOR_PID_FILE" > /dev/null 2>&1 &
      fi
    fi
  fi
  
  # Sleep for interval
  sleep $KEEPALIVE_INTERVAL
  
  # Increment runtime
  RUNTIME=$((RUNTIME + KEEPALIVE_INTERVAL))
  
  # Check for excessive processes
  PROCESS_COUNT=$(pgrep -f "ip_auth_monitor.sh" | wc -l)
  if [ $PROCESS_COUNT -gt 2 ]; then
    echo "$(date): WARNING: Found $PROCESS_COUNT monitor processes, cleaning up duplicates" | tee -a $LOG_FILE
    pkill -f "ip_auth_monitor.sh" || true
    sleep 1
    # Restart the single monitor
    AUTH_MONITOR_PID_FILE="$PID_DIR/auth_monitor.pid"
    TUNNEL_URL=$(cat /tmp/current_tunnel_url.txt 2>/dev/null)
    if [ -n "$TUNNEL_URL" ]; then
      nohup /tmp/ip_auth_monitor.sh "$TUNNEL_URL" "$AUTH_MONITOR_PID_FILE" > /dev/null 2>&1 &
    fi
  fi
  
  # Check memory usage of our processes
  for pid_file in $PID_DIR/*.pid; do
    if [ -f "$pid_file" ]; then
      PID=$(cat "$pid_file")
      if ps -p $PID > /dev/null; then
        MEM_USAGE=$(ps -o rss= -p $PID)
        # If using more than 100MB, restart it
        if [ $MEM_USAGE -gt 102400 ]; then
          echo "$(date): Process $PID using excessive memory ($MEM_USAGE KB), restarting" | tee -a $LOG_FILE
          kill $PID
        fi
      fi
    fi
  done
done

echo "$(date): Maximum runtime reached, exiting monitor" | tee -a $LOG_FILE
cleanup
EOL

chmod +x /tmp/tunnel_monitor.sh

# Generate a consistent subdomain
SUBDOMAIN="jasonserver-stable-$(hostname | md5sum | head -c 6)"
echo "Using subdomain: $SUBDOMAIN"

echo "Starting tunnel with monitor..."
nohup /tmp/tunnel_monitor.sh "$SUBDOMAIN" > /tmp/tunnel_startup.log 2>&1 &
MONITOR_PID=$!
echo $MONITOR_PID > "$PID_DIR/main_monitor.pid"

echo "Waiting for tunnel to establish..."
sleep 10

# Get the URL from the monitor's output
if [ -f "/tmp/current_tunnel_url.txt" ]; then
  TUNNEL_URL=$(cat /tmp/current_tunnel_url.txt)
  echo "Tunnel URL: $TUNNEL_URL"
else
  echo "ERROR: Could not get tunnel URL"
  cat /tmp/tunnel_startup.log
  cleanup
  exit 1
fi

# Verify tunnel is working
echo "Verifying tunnel connection..."
VERIFY_RESULT=$(curl -s -L "$TUNNEL_URL" -o /tmp/verify_page.html -w "%{http_code}")
if [ "$VERIFY_RESULT" = "200" ]; then
  echo "TUNNEL_VERIFIED=YES"
elif grep -q "Endpoint IP" /tmp/verify_page.html; then
  echo "TUNNEL_REQUIRES_IP_AUTH=YES"
  echo "TUNNEL_VERIFIED=PENDING_AUTH"
  echo "IP authentication monitor has been started and will attempt to authenticate automatically"
else
  echo "TUNNEL_VERIFIED=NO"
  echo "HTTP Status: $VERIFY_RESULT"
fi

# Output for n8n to parse
echo "TUNNEL_URL=$TUNNEL_URL"
echo "SERVER_PID=$SERVER_PID"
echo "MONITOR_PID=$MONITOR_PID"

# Release lock when done
rm -f "$LOCK_FILE"