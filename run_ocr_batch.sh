#!/bin/bash
# OCR Batch Processing Script
# First tests with a small batch, then optionally processes all frames

# Set up error handling
set -e

# Load environment variables
source .env

# Log function
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Default parameters
TEST_BATCH_SIZE=10
TEST_LIMIT=10
FULL_BATCH_SIZE=10
BASE_DIR="/home/jason/Videos/screenRecordings"
SPECIFIC_FOLDER=""

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
      TEST_BATCH_SIZE="$2"
      FULL_BATCH_SIZE="$2"
      shift 2
      ;;
    *)
      log "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Function to run OCR on a batch of frames
run_ocr_batch() {
  local folder="$1"
  local limit="$2"
  local batch_size="$3"
  
  log "Running OCR on batch of frames"
  log "Folder: $folder"
  log "Limit: $limit"
  log "Batch size: $batch_size"
  
  if [ -n "$folder" ]; then
    python run_ocr_batch.py --folder "$folder" --limit "$limit" --batch-size "$batch_size"
  else
    python run_ocr_batch.py --base-dir "$BASE_DIR" --limit "$limit" --batch-size "$batch_size"
  fi
  
  return $?
}

# Step 1: Run a small test batch
log "STEP 1: Testing OCR with a small batch of frames"
if [ -n "$SPECIFIC_FOLDER" ]; then
  log "Using specific folder: $SPECIFIC_FOLDER"
  run_ocr_batch "$SPECIFIC_FOLDER" "$TEST_LIMIT" "$TEST_BATCH_SIZE"
else
  log "Using most recent folder in $BASE_DIR"
  run_ocr_batch "" "$TEST_LIMIT" "$TEST_BATCH_SIZE"
fi

# Check if test was successful
if [ $? -eq 0 ]; then
  log "Test batch completed successfully!"
  
  # Step 2: Ask if user wants to process all frames
  read -p "Do you want to process all frames in all folders? (y/n) " answer
  
  if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
    log "STEP 2: Processing all frames in all folders"
    
    # Get all folders
    folders=($(find "$BASE_DIR" -type d -name "screen_recording_*" | sort))
    log "Found ${#folders[@]} folders to process"
    
    # Process each folder
    for folder in "${folders[@]}"; do
      log "Processing folder: $folder"
      run_ocr_batch "$folder" "0" "$FULL_BATCH_SIZE" # 0 means no limit, process all frames
      
      if [ $? -ne 0 ]; then
        log "ERROR: Failed to process folder $folder"
        exit 1
      fi
      
      log "Completed folder: $folder"
    done
    
    log "All folders processed successfully!"
  else
    log "Skipping full processing. Test batch completed successfully."
  fi
else
  log "ERROR: Test batch failed. Please check the logs."
  exit 1
fi 