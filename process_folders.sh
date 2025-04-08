#!/bin/bash
# Process all folders one by one using the existing process_frames_by_path.py script
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
LIMIT_PER_FOLDER=50
START_FOLDER=""
MAX_FOLDERS=0  # 0 means process all folders
DELAY_BETWEEN_FOLDERS=10  # seconds

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --start-folder|-s)
      START_FOLDER="$2"
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
    --max-folders|-m)
      MAX_FOLDERS="$2"
      shift 2
      ;;
    --delay|-d)
      DELAY_BETWEEN_FOLDERS="$2"
      shift 2
      ;;
    *)
      log "Unknown option: $1"
      exit 1
      ;;
  esac
done

log "Starting folder-by-folder processing using existing Python+Gemini integration"
log "Batch size: $BATCH_SIZE"
log "Limit per folder: $LIMIT_PER_FOLDER"
log "Delay between folders: $DELAY_BETWEEN_FOLDERS seconds"

if [ -n "$START_FOLDER" ]; then
  log "Starting from folder: $START_FOLDER"
fi

if [ "$MAX_FOLDERS" -gt 0 ]; then
  log "Will process at most $MAX_FOLDERS folders"
fi

# Get list of folders
log "Getting list of screen recording folders..."
FOLDERS=$(find /home/jason/Videos/screenRecordings -type d -name "screen_recording_*" | sort)

if [ -z "$FOLDERS" ]; then
  log "ERROR: No screen recording folders found"
  exit 1
fi

# Convert to array
IFS=$'\n' read -r -d '' -a FOLDER_ARRAY < <(echo "$FOLDERS" && printf '\0')

log "Found ${#FOLDER_ARRAY[@]} folders to process"

# Check if we should start from a specific folder
START_PROCESSING=true
if [ -n "$START_FOLDER" ]; then
  START_PROCESSING=false
  log "Will start processing from folder containing: $START_FOLDER"
fi

# Process each folder in order
PROCESSED_FOLDERS=0
for folder in "${FOLDER_ARRAY[@]}"; do
  folder_basename=$(basename "$folder")
  
  # Skip until we find the start folder
  if [ "$START_PROCESSING" = false ]; then
    if [[ "$folder" == *"$START_FOLDER"* ]]; then
      START_PROCESSING=true
      log "Found start folder: $folder, beginning processing"
    else
      log "Skipping folder: $folder_basename (waiting for start folder)"
      continue
    fi
  fi
  
  log "Processing folder: $folder_basename"
  
  # Run the process_frames_by_path.py script for this folder
  eval "python process_frames_by_path.py --folder-path-pattern \"${folder}/*.jpg\" --batch-size $BATCH_SIZE --limit $LIMIT_PER_FOLDER"
  
  if [ $? -ne 0 ]; then
    log "ERROR: Failed to process folder: $folder_basename"
    log "Continuing with next folder..."
  else
    log "Successfully processed folder: $folder_basename"
  fi
  
  PROCESSED_FOLDERS=$((PROCESSED_FOLDERS + 1))
  
  # Check if we've reached the maximum number of folders
  if [ "$MAX_FOLDERS" -gt 0 ] && [ "$PROCESSED_FOLDERS" -ge "$MAX_FOLDERS" ]; then
    log "Reached maximum number of folders to process: $MAX_FOLDERS"
    break
  fi
  
  # Delay between folders
  if [ $PROCESSED_FOLDERS -lt ${#FOLDER_ARRAY[@]} ] && [ "$MAX_FOLDERS" -eq 0 -o "$PROCESSED_FOLDERS" -lt "$MAX_FOLDERS" ]; then
    log "Waiting $DELAY_BETWEEN_FOLDERS seconds before next folder..."
    sleep $DELAY_BETWEEN_FOLDERS
  fi
done

log "All folders processed successfully! Processed $PROCESSED_FOLDERS folders." 