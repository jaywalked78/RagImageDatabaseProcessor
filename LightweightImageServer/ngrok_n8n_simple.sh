#!/bin/bash
# ngrok_n8n_simple.sh - Simple ngrok integration for n8n

# Configuration
PORT=7779
LOCK_FILE="/tmp/ngrok_lock"
PID_DIR="/tmp/ngrok_pids"

# Create PID directory
mkdir -p $PID_DIR

# Check for existing lock to prevent multiple instances
if [ -f "$LOCK_FILE" ]; then
  LOCK_PID=$(cat "$LOCK_FILE")
  if ps -p $LOCK_PID > /dev/null; then
    echo "Another ngrok script is already running with PID $LOCK_PID"
    
    # If already running, just get the URL and exit
    if [ -f "/tmp/current_ngrok_url.txt" ]; then
      NGROK_URL=$(cat /tmp/current_ngrok_url.txt)
      if [ -n "$NGROK_URL" ]; then
        echo "Using existing ngrok tunnel"
        echo "NGROK_URL=$NGROK_URL"
        exit 0
      fi
    fi
    
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
  pkill -f "ngrok http $PORT" || true
  rm -f "$LOCK_FILE"
  exit 0
}
trap cleanup EXIT INT TERM

# Start the server if it's not already running
cd /home/jason/Documents/DatabaseAdvancedTokenizer/LightweightImageServer
if ! curl -s http://localhost:$PORT &> /dev/null; then
  echo "Starting image server..."
  ./persistent_run.sh &
  SERVER_PID=$!
  echo $SERVER_PID > "$PID_DIR/server.pid"
  echo "Server started with PID: $SERVER_PID"
  
  # Wait for server to initialize
  for i in {1..10}; do
    if curl -s http://localhost:$PORT &> /dev/null; then
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
else
  echo "Image server is already running on port $PORT"
fi

# Kill any existing ngrok
pkill -f "ngrok http $PORT" || true
sleep 2

# Start ngrok
echo "Starting ngrok for port $PORT"
ngrok http $PORT --log=stdout > /tmp/ngrok_log.txt 2>&1 &
NGROK_PID=$!
echo $NGROK_PID > "$PID_DIR/ngrok.pid"

# Give ngrok time to establish connection
echo "Waiting for ngrok to establish..."
sleep 5

# Extract the URL using the ngrok API
NGROK_URL=""
for i in {1..5}; do
  NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*"' | head -n 1 | cut -d'"' -f4)
  if [ -n "$NGROK_URL" ]; then
    break
  fi
  echo "Waiting for ngrok URL... ($i/5)"
  sleep 2
done

if [ -z "$NGROK_URL" ]; then
  echo "ERROR: Failed to get ngrok URL after multiple attempts"
  cat /tmp/ngrok_log.txt
  cleanup
  exit 1
fi

# Save the URL to a file for future reference
echo "$NGROK_URL" > /tmp/current_ngrok_url.txt

echo "Ngrok URL: $NGROK_URL"

# Verify ngrok is working
echo "Verifying ngrok connection..."
VERIFY_RESULT=$(curl -s -L -m 10 -o /dev/null -w "%{http_code}" "$NGROK_URL")
if [ "$VERIFY_RESULT" = "200" ] || [ "$VERIFY_RESULT" = "404" ]; then
  echo "NGROK_VERIFIED=YES"
  echo "HTTP Status: $VERIFY_RESULT"
else
  echo "NGROK_VERIFIED=NO"
  echo "HTTP Status: $VERIFY_RESULT"
fi

# Output for n8n to parse
echo "NGROK_URL=$NGROK_URL"
echo "SERVER_PID=$(cat $PID_DIR/server.pid 2>/dev/null || echo 'unknown')"
echo "NGROK_PID=$NGROK_PID"
echo "NGROK_WEB_INTERFACE=http://localhost:4040"

# Print usage notes
echo ""
echo "=================== USAGE NOTES ==================="
echo "1. The ngrok URL is: $NGROK_URL"
echo "2. To stop all services: kill $NGROK_PID"
echo "3. To view ngrok status: http://localhost:4040"
echo "=================================================="

# Keep script running to maintain the tunnel
# (Comment out this section if you want the script to exit immediately)
echo "Ngrok is running. Press Ctrl+C to stop."
while true; do
  sleep 60
  # Check if ngrok is still running
  if ! ps -p $NGROK_PID > /dev/null; then
    echo "Ngrok process died, exiting"
    cleanup
    exit 1
  fi
done 