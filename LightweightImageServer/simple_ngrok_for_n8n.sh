#!/bin/bash
# simple_ngrok_for_n8n.sh - Simple ngrok launcher with permanent subdomain

PORT=7779
SUBDOMAIN="pleasing-strangely-parakeet"  # Subdomain without the ngrok-free.app part
PERMANENT_URL="https://pleasing-strangely-parakeet.ngrok-free.app"

# Check if ngrok is already running
if pgrep -f "ngrok http $PORT" > /dev/null; then
  echo "Ngrok is already running."
  echo "The ngrok URL is: $PERMANENT_URL"
  exit 0
fi

# Start ngrok with the permanent subdomain
echo "Starting ngrok on port $PORT with permanent subdomain..."
ngrok http $PORT --subdomain=$SUBDOMAIN > /dev/null 2>&1 &
NGROK_PID=$!

# Give it a moment to initialize
echo "Waiting for ngrok to initialize..."
sleep 5

# Output the URL
echo "Ngrok started with PID: $NGROK_PID"
echo "The ngrok URL is: $PERMANENT_URL"
echo "Web interface available at: http://localhost:4040"