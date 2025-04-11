# Ngrok Integration Setup Guide

This guide explains how to set up and use ngrok with the LightweightImageServer for stable public URL access.

## Prerequisites

1. **Install ngrok**
   - Download from [ngrok.com/download](https://ngrok.com/download)
   - Extract to a location in your PATH (e.g., `/usr/local/bin`)

2. **Create a free ngrok account**
   - Sign up at [ngrok.com](https://ngrok.com)
   - This is required to get your authtoken

3. **Authenticate ngrok**
   - Copy your authtoken from the ngrok dashboard
   - Authenticate with: 
     ```
     ngrok config add-authtoken YOUR_TOKEN
     ```

## Usage

### Basic Usage

1. **From the command line**:
   ```bash
   cd /path/to/LightweightImageServer
   ./ngrok_n8n_integration.sh
   ```

2. **From n8n**:
   ```bash
   #!/bin/bash
   cd /home/jason/Documents/DatabaseAdvancedTokenizer/LightweightImageServer
   ./ngrok_n8n_integration.sh
   ```

### Integration with Workflow

To use this script in your n8n workflow:

1. Add an "Execute Command" node
2. Configure it to run the ngrok integration script
3. Parse the output to get the NGROK_URL variable
4. Use the URL in subsequent HTTP request nodes

Example n8n shell script:

```bash
#!/bin/bash
# Start ngrok tunneling for image server
cd /home/jason/Documents/DatabaseAdvancedTokenizer/LightweightImageServer
./ngrok_n8n_integration.sh > /tmp/ngrok_output.txt

# Extract the URL for n8n
NGROK_URL=$(grep "NGROK_URL=" /tmp/ngrok_output.txt | cut -d'=' -f2)
echo "The ngrok URL is: $NGROK_URL"

# Continue with workflow...
```

## Features

The ngrok integration includes these advanced features:

- **Automatic monitoring** of the ngrok tunnel
- **Self-healing** - automatically restarts if connection drops
- **Resource monitoring** - prevents memory leaks
- **Log rotation** - keeps log files from growing too large
- **Clean shutdown** - proper cleanup of all processes

## Troubleshooting

### Common Issues

1. **"ngrok not found" error**
   - Ensure ngrok is installed and in your PATH
   - Try running `which ngrok` to verify

2. **Authentication errors**
   - Run `ngrok config add-authtoken YOUR_TOKEN` again
   - Check that you're using the correct authtoken

3. **Port already in use**
   - Check if another instance is running with `ps aux | grep ngrok`
   - Kill existing processes with `pkill -f "ngrok http"`

4. **Unable to establish tunnel**
   - Check internet connection
   - Verify that outbound connections are allowed
   - See logs at `/tmp/ngrok_log.txt`

### Monitoring and Logs

- **Main logs**: `/tmp/ngrok_monitor.log`
- **Process logs**: `/tmp/ngrok_log.txt`
- **Status check**: Access http://localhost:4040 in your browser

## Advantages Over Localtunnel

Ngrok offers several advantages over localtunnel:

1. **Stability**: More reliable connection, less prone to dropping
2. **Control**: Built-in web interface for monitoring and management
3. **Features**: Reserved domains (with paid plan), TLS support
4. **Performance**: Generally better performance with fewer disconnects
5. **API**: REST API for programmatic control
6. **Security**: Additional security features like IP restrictions

## Limitations

- Free tier limitations:
  - Sessions expire after 2 hours (handled by auto-restart)
  - Random URLs unless using a paid plan
  - Limited to 40 connections/minute

For production use, consider upgrading to a paid ngrok plan for more features and stability. 