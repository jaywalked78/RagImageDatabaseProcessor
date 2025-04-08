#!/bin/bash
# Script to process all remaining frames in screen recording folders
# This script will:
# 1. Sort folders in chronological order
# 2. Exclude folders already marked as finished in Airtable
# 3. Generate a list of frames from remaining folders
# 4. Process them using the robust OCR worker through run_with_logs.sh

set -e  # Exit on error

# Unset any existing variables that might interfere
unset TEMP_DIR
unset TMP_DIR
unset TMPDIR

# Set variables
BASE_DIR="/home/jason/Videos/screenRecordings"
TEMP_DIR="/tmp/database_tokenizer"  # Hardcoded absolute path
LOG_DIR="/home/jason/Documents/DatabaseAdvancedTokenizer/logs"  # Hardcoded absolute path
WORKER_ID=1

# Create directories if they don't exist
mkdir -p "$TEMP_DIR"
mkdir -p "$LOG_DIR"

# Log creation of directories
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Created temp directory: $TEMP_DIR"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Created logs directory: $LOG_DIR"

# Generate timestamp for this run
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/process_all_frames_${TIMESTAMP}.log"

# Log function
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "Starting to process all remaining frames"
log "Base directory: $BASE_DIR"
log "Temp directory: $TEMP_DIR"
log "Log directory: $LOG_DIR"

# Load environment variables
if [ -f .env ]; then
  source .env
  log "Loaded environment variables from .env"
else
  log "Warning: .env file not found"
fi

# Validate Airtable configuration
if [ -z "$AIRTABLE_PERSONAL_ACCESS_TOKEN" ]; then
  log "Error: AIRTABLE_PERSONAL_ACCESS_TOKEN not set in .env file"
  exit 1
fi

if [ -z "$AIRTABLE_BASE_ID" ]; then
  log "Error: AIRTABLE_BASE_ID not set in .env file"
  exit 1
fi

# Validate tracking table configuration
if [ -z "$AIRTABLE_TRACKING_TABLE" ]; then
  log "Warning: AIRTABLE_TRACKING_TABLE not set in .env, defaulting to 'Finished OCR Processed Folders'"
  AIRTABLE_TRACKING_TABLE="Finished OCR Processed Folders"
fi

if [ -z "$FOLDER_NAME_FIELD" ]; then
  log "Warning: FOLDER_NAME_FIELD not set in .env, defaulting to 'FolderName'"
  FOLDER_NAME_FIELD="FolderName"
fi

# Define file paths
AIRTABLE_RESPONSE_FILE="${TEMP_DIR}/airtable_response_${TIMESTAMP}.json"
FINISHED_FOLDERS_FILE="${TEMP_DIR}/finished_folders_${TIMESTAMP}.txt"
ALL_FOLDERS_FILE="${TEMP_DIR}/all_folders_${TIMESTAMP}.txt"
REMAINING_FOLDERS_FILE="${TEMP_DIR}/remaining_folders_${TIMESTAMP}.txt"
REMAINING_FRAMES_FILE="${TEMP_DIR}/remaining_frames_${TIMESTAMP}.txt"

# Debug info
log "File paths:"
log "- AIRTABLE_RESPONSE_FILE: $AIRTABLE_RESPONSE_FILE"
log "- FINISHED_FOLDERS_FILE: $FINISHED_FOLDERS_FILE"
log "- ALL_FOLDERS_FILE: $ALL_FOLDERS_FILE"
log "- REMAINING_FOLDERS_FILE: $REMAINING_FOLDERS_FILE"
log "- REMAINING_FRAMES_FILE: $REMAINING_FRAMES_FILE"

# Fetch finished folders from Airtable
log "Fetching list of finished folders from Airtable table: $AIRTABLE_TRACKING_TABLE"

curl -s -X GET \
  "https://api.airtable.com/v0/$AIRTABLE_BASE_ID/$AIRTABLE_TRACKING_TABLE?fields%5B%5D=$FOLDER_NAME_FIELD" \
  -H "Authorization: Bearer $AIRTABLE_PERSONAL_ACCESS_TOKEN" \
  -H "Content-Type: application/json" > "$AIRTABLE_RESPONSE_FILE"

log "Checking if Airtable response was saved: $(ls -la $AIRTABLE_RESPONSE_FILE)"

# Check if jq is available
if command -v jq >/dev/null 2>&1; then
  # Extract folder names from response using jq
  jq -r ".records[].fields.$FOLDER_NAME_FIELD" "$AIRTABLE_RESPONSE_FILE" > "$FINISHED_FOLDERS_FILE" 2>/dev/null
else
  # Fallback to grep and cut if jq is not available
  log "Warning: jq not found, using fallback method to parse JSON"
  grep -o "\"$FOLDER_NAME_FIELD\":\"[^\"]*\"" "$AIRTABLE_RESPONSE_FILE" | cut -d'"' -f4 > "$FINISHED_FOLDERS_FILE"
fi

log "Checking if finished folders file was created: $(ls -la $FINISHED_FOLDERS_FILE 2>/dev/null || echo 'File not found')"

# Count finished folders
if [ -f "$FINISHED_FOLDERS_FILE" ]; then
  FINISHED_COUNT=$(wc -l < "$FINISHED_FOLDERS_FILE")
  log "Found $FINISHED_COUNT finished folders in Airtable"
else
  FINISHED_COUNT=0
  log "No finished folders found or could not parse Airtable response"
  touch "$FINISHED_FOLDERS_FILE"
  log "Created empty finished folders file: $FINISHED_FOLDERS_FILE"
fi

# Get all folders sorted chronologically
log "Getting all folders in chronological order..."
find "$BASE_DIR" -maxdepth 1 -type d -name "screen_recording_*" | sort -t '_' -k3,3 -k4,4 -k5,5 -k7,7 -k8,8 -k9,9 > "$ALL_FOLDERS_FILE"

log "Checking if all folders file was created: $(ls -la $ALL_FOLDERS_FILE 2>/dev/null || echo 'File not found')"

if [ -s "$ALL_FOLDERS_FILE" ]; then
  TOTAL_FOLDERS=$(wc -l < "$ALL_FOLDERS_FILE")
  log "Found $TOTAL_FOLDERS total folders"
else
  log "Error: Could not find any folders matching pattern 'screen_recording_*'"
  log "Checking if BASE_DIR exists: $(ls -la $BASE_DIR)"
  exit 1
fi

# Filter out finished folders
touch "$REMAINING_FOLDERS_FILE"

if [ "$FINISHED_COUNT" -gt 0 ]; then
  log "Filtering out finished folders..."
  while IFS= read -r folder_path; do
    folder_name=$(basename "$folder_path")
    if ! grep -q "^${folder_name}$" "$FINISHED_FOLDERS_FILE" 2>/dev/null; then
      echo "$folder_path" >> "$REMAINING_FOLDERS_FILE"
    fi
  done < "$ALL_FOLDERS_FILE"
else
  log "No finished folders found, processing all folders."
  cp "$ALL_FOLDERS_FILE" "$REMAINING_FOLDERS_FILE"
fi

log "Checking if remaining folders file was created: $(ls -la $REMAINING_FOLDERS_FILE 2>/dev/null || echo 'File not found')"

# Count remaining folders
if [ -s "$REMAINING_FOLDERS_FILE" ]; then
  REMAINING_FOLDERS=$(wc -l < "$REMAINING_FOLDERS_FILE")
  log "After filtering, $REMAINING_FOLDERS folders need processing (skipping $(($TOTAL_FOLDERS - $REMAINING_FOLDERS)) folders)"
else
  log "Error: No folders left to process after filtering"
  exit 1
fi

# Check if there are any folders to process
if [ "$REMAINING_FOLDERS" -eq 0 ]; then
  log "No folders left to process! All folders appear to be finished."
  exit 0
fi

# Collect frames from remaining folders
log "Collecting frames from remaining folders..."
touch "$REMAINING_FRAMES_FILE"

FOLDER_COUNT=0
TOTAL_FRAMES=0

while IFS= read -r folder_path; do
  FOLDER_COUNT=$((FOLDER_COUNT + 1))
  folder_name=$(basename "$folder_path")
  log "Processing folder $FOLDER_COUNT/$REMAINING_FOLDERS: $folder_name"
  
  # Find frames in this folder
  folder_frames=$(find "$folder_path" -type f -name "*.jpg" | sort -V)
  
  # Check if any frames were found
  if [ -n "$folder_frames" ]; then
    frame_count=$(echo "$folder_frames" | wc -l)
    TOTAL_FRAMES=$((TOTAL_FRAMES + frame_count))
    
    # Add frames to the list
    echo "$folder_frames" >> "$REMAINING_FRAMES_FILE"
    
    log "Added $frame_count frames from folder: $folder_name"
  else
    log "No frames found in folder: $folder_name"
  fi
done < "$REMAINING_FOLDERS_FILE"

log "Collected $TOTAL_FRAMES frames from $REMAINING_FOLDERS folders"
log "Checking frames file: $(ls -la $REMAINING_FRAMES_FILE) ($(wc -l < "$REMAINING_FRAMES_FILE") lines)"

# Check if there are any frames to process
if [ "$TOTAL_FRAMES" -eq 0 ]; then
  log "No frames found in the remaining folders!"
  exit 0
fi

# Run the worker using run_with_logs.sh
log "Starting to process $TOTAL_FRAMES frames using run_with_logs.sh"
log "Using worker ID: $WORKER_ID"
log "Using frames file: $REMAINING_FRAMES_FILE"

./run_with_logs.sh "$WORKER_ID" "$REMAINING_FRAMES_FILE"

log "Finished processing frames"
log "Check the worker log for detailed results" 