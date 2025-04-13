#!/bin/bash

# Configuration
PORT=7779  # Default port for your image server
TIMEOUT=180  # Default timeout in minutes (3 hours)
NGROK_CONFIG="/home/jason/.ngrok2/ngrok.yml"  # Path to ngrok config
LOG_FILE="/home/jason/ngrok.log"

# Parse command line arguments
while getopts "p:t:" opt; do
  case $opt in
    p) PORT=$OPTARG ;;
    t) TIMEOUT=$OPTARG ;;
    *) echo "Usage: $0 [-p port] [-t timeout_minutes]" >&2
       exit 1 ;;
  esac
done

# Export timeout for the image server
export IMAGE_SERVER_TIMEOUT="$TIMEOUT"
echo "Setting image server timeout to $TIMEOUT minutes"

# Check if ngrok is already running
if pgrep -f "ngrok http $PORT" > /dev/null; then
    echo "ngrok is already running for port $PORT"
    NGROK_PID=$(pgrep -f "ngrok http $PORT")
    echo "NGROK_STATUS=RUNNING|PID=$NGROK_PID"
else
    # Start ngrok
    echo "Starting ngrok for port $PORT..."
    nohup ngrok http --log=stdout --log-level=info $PORT > "$LOG_FILE" 2>&1 &
    
    # Wait for ngrok to start
    sleep 5
    
    # Check if ngrok started successfully
    if pgrep -f "ngrok http $PORT" > /dev/null; then
        NGROK_PID=$(pgrep -f "ngrok http $PORT")
        # Get the public URL
        NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | grep -o 'http[^"]*')
        echo "NGROK_STATUS=SUCCESS|URL=$NGROK_URL|PID=$NGROK_PID"
    else
        echo "NGROK_STATUS=FAILED|ERROR=Process not running after startup attempt"
        exit 1
    fi
fi

# Keep the script running to maintain the service
# This helps systemd know the service is still alive
while true; do
    if ! pgrep -f "ngrok http $PORT" > /dev/null; then
        echo "ngrok process died, restarting..."
        nohup ngrok http --log=stdout --log-level=info $PORT > "$LOG_FILE" 2>&1 &
        sleep 5
    fi
    # Log that we're still alive every hour
    echo "$(date): ngrok still running on port $PORT" >> "$LOG_FILE"
    sleep 3600
done