#!/bin/bash
# Fresh OCR Processing Script
# Resets all Flagged fields and processes frames from the beginning

# Set up error handling
set -e

# Load environment variables
source .env

# Log function
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Default parameters
BATCH_SIZE=10
BASE_DIR="/home/jason/Videos/screenRecordings"
SPECIFIC_FOLDER=""
LIMIT_PER_FOLDER=100
START_FROM_FOLDER=""

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --folder|-f)
      SPECIFIC_FOLDER="$2"
      shift 2
      ;;
    --base-dir|-d)
      BASE_DIR="$2"
      shift 2
      ;;
    --batch-size|-b)
      BATCH_SIZE="$2"
      shift 2
      ;;
    --limit|-l)
      LIMIT_PER_FOLDER="$2"
      shift 2
      ;;
    --start-from|-s)
      START_FROM_FOLDER="$2"
      shift 2
      ;;
    *)
      log "Unknown option: $1"
      exit 1
      ;;
  esac
done

log "Starting fresh OCR processing"
log "Batch size: $BATCH_SIZE"

# Step 1: Reset all Flagged fields to false
log "Step 1: Resetting all Flagged fields to 'false'"
node update_flagged_field.js $BATCH_SIZE false false ""

if [ $? -ne 0 ]; then
  log "ERROR: Failed to reset Flagged fields"
  exit 1
fi

log "Successfully reset all Flagged fields"

# Process a specific folder if provided
if [ -n "$SPECIFIC_FOLDER" ]; then
  log "Step 2: Processing specific folder: $SPECIFIC_FOLDER"
  python run_ocr_batch.py --folder "$SPECIFIC_FOLDER" --batch-size $BATCH_SIZE --limit $LIMIT_PER_FOLDER
  
  if [ $? -ne 0 ]; then
    log "ERROR: Failed to process folder: $SPECIFIC_FOLDER"
    exit 1
  fi
  
  log "Successfully processed folder: $SPECIFIC_FOLDER"
  exit 0
fi

# Step 2: Get a list of all folders, sorted chronologically
log "Step 2: Getting list of all folders in $BASE_DIR"
FOLDERS=$(find "$BASE_DIR" -type d -name "screen_recording_*" | sort)
FOLDER_COUNT=$(echo "$FOLDERS" | wc -l)

if [ -z "$FOLDERS" ]; then
  log "ERROR: No folders found in $BASE_DIR"
  exit 1
fi

log "Found $FOLDER_COUNT folders to process"

# Check if we need to start from a specific folder
SHOULD_START=true
if [ -n "$START_FROM_FOLDER" ]; then
  log "Will start processing from folder: $START_FROM_FOLDER"
  SHOULD_START=false
fi

# Step 3: Process each folder chronologically
log "Step 3: Processing folders chronologically"
PROCESSED=0

for FOLDER in $FOLDERS; do
  FOLDER_NAME=$(basename "$FOLDER")
  
  # Check if we should start processing yet
  if [ "$SHOULD_START" = false ]; then
    if [[ "$FOLDER_NAME" == *"$START_FROM_FOLDER"* ]]; then
      SHOULD_START=true
    else
      log "Skipping folder: $FOLDER_NAME (waiting to reach start folder)"
      continue
    fi
  fi
  
  let PROCESSED++
  log "Processing folder $PROCESSED/$FOLDER_COUNT: $FOLDER_NAME"
  
  # Process the folder
  python run_ocr_batch.py --folder "$FOLDER" --batch-size $BATCH_SIZE --limit $LIMIT_PER_FOLDER
  
  if [ $? -ne 0 ]; then
    log "ERROR: Failed to process folder: $FOLDER_NAME"
    log "Continuing with next folder..."
    continue
  fi
  
  log "Successfully processed folder: $FOLDER_NAME"
  
  # Add a short delay between folders to avoid rate limiting
  log "Waiting 5 seconds before processing next folder..."
  sleep 5
done

log "Finished processing $PROCESSED folders"
log "OCR processing complete!" 