#!/bin/bash
# Simple Ngrok launcher for your free static domain

# Hardcoded values
PORT=7779
DOMAIN="pleasing-strangely-parakeet"
PERMANENT_URL="https://pleasing-strangely-parakeet.ngrok-free.app"

# Kill any existing ngrok processes
pkill -f ngrok || true
echo "Stopped any running ngrok processes"

# Start ngrok directly without background mode
echo "Starting ngrok on port $PORT with your free domain..."
echo "URL: $PERMANENT_URL"
echo "Web interface will be available at: http://localhost:4040"

# Just run ngrok in the foreground
ngrok http $PORT --domain=$DOMAIN.ngrok-free.app