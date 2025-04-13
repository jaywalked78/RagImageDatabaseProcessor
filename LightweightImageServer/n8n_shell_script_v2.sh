#!/bin/bash
# n8n_shell_script.sh - Enhanced for stability

# Custom subdomain - MAKE THIS CONSISTENT between runs
# Use something unique to you that others won't guess
SUBDOMAIN="jasonserver-stable-$(hostname | md5sum | head -c 6)"

echo "Starting server process..."
# Start your server process
./start_publicserver.sh &
SERVER_PID=$!

echo "Server started with PID: $SERVER_PID"
echo "Waiting for server to initialize..."
sleep 5

# Kill any existing tunnels
pkill -f "lt --port 7779" || true

# Create a tunnel monitor script
cat > /tmp/tunnel_monitor.sh << 'EOL'
#!/bin/bash
PORT=7779
SUBDOMAIN="$1"
KEEPALIVE_INTERVAL=60  # Send a request every minute
MAX_RUNTIME=7200       # 2 hours max runtime

start_tunnel() {
  # Start tunnel with specific subdomain
  lt --port $PORT --subdomain $SUBDOMAIN > /tmp/tunnel_info.txt 2>&1 &
  TUNNEL_PID=$!
  echo "Started tunnel with PID: $TUNNEL_PID"
  
  # Extract URL
  sleep 5
  TUNNEL_URL=$(grep -o "https://[^[:space:]]*" /tmp/tunnel_info.txt | head -n 1)
  if [ -z "$TUNNEL_URL" ]; then
    echo "Failed to get tunnel URL"
    return 1
  fi
  echo "Tunnel URL: $TUNNEL_URL"
  echo "$TUNNEL_URL" > /tmp/current_tunnel_url.txt
  
  return 0
}

# Start initial tunnel
start_tunnel
RUNTIME=0

# Keep-alive loop
while [ $RUNTIME -lt $MAX_RUNTIME ]; do
  # Check if tunnel is still running
  if ! ps -p $TUNNEL_PID > /dev/null; then
    echo "Tunnel process died, restarting..."
    start_tunnel
  fi
  
  # Get current URL
  TUNNEL_URL=$(cat /tmp/current_tunnel_url.txt)
  
  # Send keep-alive request
  echo "Sending keep-alive at $(date)"
  curl -s -I "$TUNNEL_URL" > /dev/null
  
  # Sleep for interval
  sleep $KEEPALIVE_INTERVAL
  
  # Increment runtime
  RUNTIME=$((RUNTIME + KEEPALIVE_INTERVAL))
done

echo "Maximum runtime reached, exiting monitor"
EOL

chmod +x /tmp/tunnel_monitor.sh

echo "Starting tunnel with monitor..."
nohup /tmp/tunnel_monitor.sh "$SUBDOMAIN" > /tmp/tunnel_monitor.log 2>&1 &
MONITOR_PID=$!

echo "Waiting for tunnel to establish..."
sleep 10

# Get the URL from the monitor's output
if [ -f "/tmp/current_tunnel_url.txt" ]; then
  TUNNEL_URL=$(cat /tmp/current_tunnel_url.txt)
  echo "Tunnel URL: $TUNNEL_URL"
else
  echo "ERROR: Could not get tunnel URL"
  cat /tmp/tunnel_monitor.log
  exit 1
fi

# Verify tunnel is working
echo "Verifying tunnel connection..."
VERIFY_RESULT=$(curl -s -I "$TUNNEL_URL")
if echo "$VERIFY_RESULT" | grep -q "200 OK\|302 Found\|301 Moved"; then
  echo "TUNNEL_VERIFIED=YES"
else
  echo "TUNNEL_VERIFIED=NO"
  echo "$VERIFY_RESULT"
fi

# Output for n8n to parse
echo "TUNNEL_URL=$TUNNEL_URL"
echo "SERVER_PID=$SERVER_PID"
echo "MONITOR_PID=$MONITOR_PID"