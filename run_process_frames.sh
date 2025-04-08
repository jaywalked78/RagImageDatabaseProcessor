#!/bin/bash
# Run the process_frames_by_path.py script with proper parameters
# Reuses existing Python code with Gemini integration

# Set up error handling
set -e

# Load environment variables
source .env

# Log function with timestamps
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Default parameters
BATCH_SIZE=10
SPECIFIC_FOLDER=""
LIMIT=100

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --folder|-f)
      SPECIFIC_FOLDER="$2"
      shift 2
      ;;
    --batch-size|-b)
      BATCH_SIZE="$2"
      shift 2
      ;;
    --limit|-l)
      LIMIT="$2"
      shift 2
      ;;
    *)
      log "Unknown option: $1"
      exit 1
      ;;
  esac
done

log "Starting frame processing using existing Python+Gemini integration"
log "Batch size: $BATCH_SIZE"
log "Limit: $LIMIT"

if [ -n "$SPECIFIC_FOLDER" ]; then
  log "Processing specific folder: $SPECIFIC_FOLDER"
  PATTERN_ARG="--folder-path-pattern \"${SPECIFIC_FOLDER}/*.jpg\""
else
  # Get the most recent folder if none specified
  LATEST_FOLDER=$(find /home/jason/Videos/screenRecordings -type d -name "screen_recording_*" | sort | tail -1)
  if [ -z "$LATEST_FOLDER" ]; then
    log "ERROR: No screen recording folders found"
    exit 1
  fi
  
  log "Using most recent folder: $LATEST_FOLDER"
  PATTERN_ARG="--folder-path-pattern \"${LATEST_FOLDER}/*.jpg\""
fi

# Run the process_frames_by_path.py script with escaped arguments
log "Running command: python process_frames_by_path.py $PATTERN_ARG --batch-size $BATCH_SIZE --limit $LIMIT"
eval "python process_frames_by_path.py $PATTERN_ARG --batch-size $BATCH_SIZE --limit $LIMIT"

if [ $? -ne 0 ]; then
  log "ERROR: Failed to process frames"
  exit 1
fi

log "Frame processing completed successfully!" 