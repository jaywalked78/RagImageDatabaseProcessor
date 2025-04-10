# n8n Integration Guide

This document provides a comprehensive guide for integrating the RagImageDatabaseProcessor with n8n for automated workflows.

## System Architecture

The RagImageDatabaseProcessor consists of three distinct tools that can be orchestrated through n8n:

1. **OCR Processing Tool**: Extracts text from screen recording frames and integrates with Airtable
2. **Semantic Chunker**: Processes extracted text into optimized chunks for retrieval
3. **Lightweight Image Server**: Hosts frame images and generates accessible URLs

These tools work together through n8n automation to create a comprehensive processing pipeline.

## Overview

The RagImageDatabaseProcessor can be integrated with n8n to automate the process of:
1. Starting the API server
2. Processing screen recording frames
3. Generating image URLs and text chunks
4. Collecting the results for further processing

## Workflow Setup

### Step 1: Start API Server

First, create an "Execute Command" node to start the API server:

```bash
#!/bin/bash
# Start-background.sh
cd /home/jason/Documents/DatabaseAdvancedTokenizer/MinimalistRagIntake
nohup ./run.sh > /tmp/api_output.log 2>&1 &
echo "Process started in background with PID: $!"
```

### Step 2: Wait for API Server to Start

Add a "Wait" node to allow the API server time to initialize:
- Set wait time to 10 seconds

### Step 3: Send Frame Metadata Request

Create an HTTP Request node:
- Method: POST
- URL: Your API endpoint
- Body: Frame metadata from Airtable

### Step 4: Run Processor with Image Server

Create another "Execute Command" node for the main processing:

```bash
#!/bin/bash
# processor-background.sh
cd /home/jason/Documents/DatabaseAdvancedTokenizer/MinimalistRagIntake

# Activate virtual environment if it exists, or create it
if [ -d "venv" ]; then
  source venv/bin/activate
else
  python3 -m venv venv
  source venv/bin/activate
fi

# Install requirements explicitly
pip install -r requirements.txt

# Define full paths to ensure correct resolution
export CHUNKER_DIR=$(pwd)
export IMAGE_SERVER_DIR=$(realpath "$CHUNKER_DIR/../LightweightImageServer")
export PATH=$PATH:$CHUNKER_DIR:$IMAGE_SERVER_DIR

# Start image server explicitly if needed
$IMAGE_SERVER_DIR/persistent_run.sh &
SERVER_PID=$!
sleep 5  # Give it time to start

# Run the processor with complete logging
./run_processor_with_image_server.sh {{ $('Limit').first().json.FolderName }} {{ $json.executionMode || 'test' }} > /tmp/processor_output.log 2>&1

echo "Processor completed. Check /tmp/processor_output.log for details."
```

## Data Flow Between Components

The workflow coordinates data flow between the three main tools:

1. **OCR Tool → Semantic Chunker**:
   - OCR extracted text is passed to the Semantic Chunker
   - Metadata and context are preserved during transfer

2. **OCR Tool → Image Server**:
   - Frame paths are passed to the Image Server for hosting
   - Frame IDs maintain consistency between systems

3. **Combined Output**:
   - Semantic Chunker generates text chunks for retrieval
   - Image Server provides URLs for visual reference
   - Integration scripts combine these outputs for downstream use

## Data Flow Through n8n

The following data is passed through the workflow:

1. **From Airtable**: 
   - Folder name (`{{ $('Limit').first().json.FolderName }}`)
   - Execution mode (`{{ $json.executionMode }}`, defaults to 'test')

2. **Output Data**:
   - Text chunks from webhook response
   - Image URLs in JSON file: 
     - Path: `LightweightImageServer/output/json/[FOLDER_NAME]_[TIMESTAMP].json`
     - Latest symlink: `LightweightImageServer/output/json/[FOLDER_NAME]_latest.json`

## File Naming Convention

Output JSON files use the following naming convention:
- Format: `[FOLDER_NAME]_[TIMESTAMP].json`
- Timestamp format: `YYYYMMDD_HHMMSS` in Central Standard Time (CST)
- Example: `screen_recording_2025_02_25_at_8_05_47_pm_20240301_120530.json`

## Logging

Detailed logs are available at:
- `/tmp/processor_output.log` - Main processing log
- `/tmp/api_output.log` - API server log

## Advanced Configuration

To customize the workflow:

### Execution Mode

Pass `executionMode` parameter in your n8n workflow:
- `test`: Run in test mode (default)
- `production`: Run in production mode
- Or pass a specific file path to process a single file

### Custom Folder Path

If using non-standard folder locations, update the paths in your execute command node.

## Troubleshooting

Common issues and solutions:

1. **API Server Not Starting**: 
   - Check `/tmp/api_output.log` for errors
   - Ensure the path to `run.sh` is correct

2. **Image URLs Not Generated**:
   - Verify the folder path exists
   - Check if image server is running with `curl http://localhost:7779`

3. **Webhook Not Receiving Data**:
   - Check connection settings
   - Verify webhook URL in `.env` file

4. **File Overwriting Issues**:
   - This should be resolved with timestamped filenames
   - If it persists, check for timezone configuration issues 