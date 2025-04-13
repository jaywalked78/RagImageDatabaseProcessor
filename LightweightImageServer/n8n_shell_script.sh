#!/bin/bash
# n8n_shell_script.sh - With authentication handling
set -e  # Exit on any errors

echo "Starting server process..."
# Start your server process
./start_publicserver.sh &
SERVER_PID=$!

echo "Server started with PID: $SERVER_PID"
echo "Waiting for server to initialize..."
sleep 5

# Kill any existing tunnels
pkill -f "lt --port 7779" || true

echo "Starting tunnel..."
# Generate a unique subdomain to avoid conflicts
SUBDOMAIN="jserver-$(date +%s)"
lt --port 7779 --subdomain $SUBDOMAIN > /tmp/tunnel_info.txt 2>&1 &
TUNNEL_PID=$!

echo "Waiting for tunnel to establish..."
sleep 5

# Extract the URL
TUNNEL_URL=$(grep -o "https://[^[:space:]]*" /tmp/tunnel_info.txt | head -n 1)

if [ -z "$TUNNEL_URL" ]; then
  echo "ERROR: Could not get tunnel URL"
  cat /tmp/tunnel_info.txt
  exit 1
fi

echo "Tunnel URL: $TUNNEL_URL"

# Try to authenticate with the tunnel
echo "Attempting tunnel authentication..."
# The -L flag follows redirects, -s is silent mode, -c stores cookies
curl -L -s -c /tmp/tunnel_cookies.txt "$TUNNEL_URL" > /tmp/auth_page.html

# Check if there's a password form
if grep -q "password" /tmp/auth_page.html; then
  echo "Password form detected, attempting automatic authentication..."
  
  # Extract any form tokens if needed
  CSRF_TOKEN=$(grep -o 'name="csrf_token" value="[^"]*"' /tmp/auth_page.html | cut -d'"' -f4)
  
  # For localtunnel, the default password is often blank or "bypass"
  # Try a few common default options
  for PASSWORD in "" "bypass" "localtunnel"; do
    echo "Trying password: '$PASSWORD'"
    
    # Submit the form with the password
    AUTH_RESULT=$(curl -L -s -b /tmp/tunnel_cookies.txt -c /tmp/tunnel_cookies.txt \
      -d "password=$PASSWORD" \
      -d "csrf_token=$CSRF_TOKEN" \
      "$TUNNEL_URL")
    
    # Check if authentication was successful by making a test request
    TEST_RESULT=$(curl -L -s -I -b /tmp/tunnel_cookies.txt "$TUNNEL_URL/images/frame_000001.jpg")
    
    # If we get a successful response, authentication worked
    if echo "$TEST_RESULT" | grep -q "200 OK\|302 Found\|301 Moved"; then
      echo "AUTH_SUCCESS=YES"
      echo "AUTH_PASSWORD=$PASSWORD"
      break
    else
      echo "AUTH_SUCCESS=NO"
    fi
  done
else
  echo "No password form detected, tunnel may not require authentication"
  echo "AUTH_SUCCESS=UNKNOWN"
fi

# Final verification test
echo "Performing final verification..."
VERIFY_RESULT=$(curl -L -s -I -b /tmp/tunnel_cookies.txt "$TUNNEL_URL/images/frame_000001.jpg")
if echo "$VERIFY_RESULT" | grep -q "200 OK\|302 Found\|301 Moved"; then
  echo "TUNNEL_VERIFIED=YES"
else
  echo "TUNNEL_VERIFIED=NO"
  echo "$VERIFY_RESULT"
fi

# Store cookies for n8n to use
base64 /tmp/tunnel_cookies.txt > /tmp/tunnel_cookies_base64.txt

# Output for n8n to parse
echo "TUNNEL_URL=$TUNNEL_URL"
echo "SERVER_PID=$SERVER_PID"
echo "TUNNEL_PID=$TUNNEL_PID"
echo "COOKIES_FILE=/tmp/tunnel_cookies_base64.txt"