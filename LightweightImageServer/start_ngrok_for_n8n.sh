#!/bin/bash
# start_ngrok_for_n8n.sh - Runs the ngrok integration specifically for n8n
# This script ensures proper URL retrieval and formatting for n8n workflows

# Navigate to the LightweightImageServer directory
cd /home/jason/Documents/DatabaseAdvancedTokenizer/LightweightImageServer

# Run the ngrok integration with n8n flag
./ngrok_n8n_integration.sh --n8n

# The script will automatically:
# 1. Start the ngrok integration in the background
# 2. Wait for the URL to be available (up to 30 seconds)
# 3. Output the URL in a format that n8n can parse
# 4. Exit with success/failure status 