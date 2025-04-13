#!/bin/bash
# processor-background.sh - Enhanced version for n8n execution

# Get folder name and execution mode from arguments
FOLDER_NAME="${1:-}"
EXECUTION_MODE="${2:-test}"  # Default to test if not provided

# Redirect all output to log files
{
  echo "Starting processor with folder: $FOLDER_NAME, mode: $EXECUTION_MODE"
  
  # Activate virtual environment if it exists, or create it
  if [ -d "venv" ]; then
    source venv/bin/activate
  else
    python3 -m venv venv
    source venv/bin/activate
  fi
  
  # Install requirements with reduced output
  pip install --quiet -r requirements.txt
  
  # Define full paths to ensure correct resolution
  export CHUNKER_DIR=$(pwd)
  export IMAGE_SERVER_DIR=$(realpath "$CHUNKER_DIR/../LightweightImageServer")
  export PATH=$PATH:$CHUNKER_DIR:$IMAGE_SERVER_DIR
  
  # Start image server explicitly if needed
  $IMAGE_SERVER_DIR/persistent_run.sh &
  SERVER_PID=$!
  sleep 5  # Give it time to start
  
  # Run the processor with the specified execution mode
  if [ -z "$FOLDER_NAME" ]; then
    echo "Error: No folder name provided"
    exit 1
  fi
  
  if [ "$EXECUTION_MODE" == "production" ]; then
    echo "Running in PRODUCTION mode with folder: $FOLDER_NAME"
    ./run_processor_with_image_server.sh "$FOLDER_NAME"  # No second arg = production mode
  else
    echo "Running in TEST mode with folder: $FOLDER_NAME"
    ./run_processor_with_image_server.sh "$FOLDER_NAME" test
  fi
  
  echo "Processor completed."
} > /tmp/processor_output.log 2>&1

# Just output a small message for n8n
echo "Process started for folder: $FOLDER_NAME in mode: $EXECUTION_MODE"
echo "Check /tmp/processor_output.log for full details." 