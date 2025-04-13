#!/bin/bash
# Ngrok launcher with nohup for background execution

# Configuration
PORT=7779
DOMAIN="pleasing-strangely-parakeet"
LOG_FILE="ngrok.log"

# Stop existing ngrok processes
pkill -f ngrok || true
echo "Stopped any existing ngrok processes"

# Start ngrok with nohup to keep it running in the background
echo "Starting ngrok for $DOMAIN.ngrok-free.app on port $PORT..."
nohup ngrok http $PORT --domain=$DOMAIN.ngrok-free.app > $LOG_FILE 2>&1 &

# Save the PID for later use
NGROK_PID=$!
echo "Ngrok started with PID: $NGROK_PID"

# Wait a moment for ngrok to initialize
sleep 5

# Check if ngrok is still running
if ps -p $NGROK_PID > /dev/null; then
    echo "SUCCESS: Ngrok is running in the background!"
    echo "URL: https://$DOMAIN.ngrok-free.app"
    echo "Web interface: http://localhost:4040"
    echo "Log file: $LOG_FILE"
else
    echo "FAILED: Ngrok terminated unexpectedly."
    echo "Check the log file: $LOG_FILE"
    cat $LOG_FILE
fi 