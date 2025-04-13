#!/bin/bash
# Ngrok diagnostic script

echo "=== System Information ==="
uname -a
echo ""

echo "=== Ngrok Version ==="
ngrok version
echo ""

echo "=== Checking ngrok location ==="
which ngrok
echo ""

echo "=== Checking if port 7779 is already in use ==="
lsof -i :7779 || echo "Port 7779 is free"
echo ""

echo "=== Checking if port 4040 is already in use ==="
lsof -i :4040 || echo "Port 4040 is free"
echo ""

echo "=== Current user and permissions ==="
whoami
id
echo ""

echo "=== Running strace on ngrok to identify termination cause ==="
echo "This will start ngrok and trace system calls..."
echo "Press Ctrl+C after a few seconds to stop the trace."
echo ""
echo "Starting strace in 3 seconds..."
sleep 3

strace -f ngrok http 7779 --domain=pleasing-strangely-parakeet.ngrok-free.app

# Note: This script will not return as strace will run ngrok in the foreground
# You'll need to press Ctrl+C to stop it 