#!/bin/bash
# OCR Pipeline Script
# This script runs the OCR processing pipeline:
# 1. Process frames with OCR and LLM
# 2. Parse OCRData and update Flagged field

# Load environment variables
source .env

# Set up logging
LOG_DIR="logs/ocr"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="$LOG_DIR/ocr_pipeline_$TIMESTAMP.log"

# Function to log messages
log() {
  local message="$1"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] $message" | tee -a "$LOG_FILE"
}

# Check for required dependencies
check_dependencies() {
  log "Checking dependencies..."
  
  # Check for Python
  if ! command -v python &> /dev/null; then
    log "ERROR: Python is not installed or not in PATH"
    exit 1
  fi
  
  # Check for Node.js
  if ! command -v node &> /dev/null; then
    log "ERROR: Node.js is not installed or not in PATH"
    exit 1
  fi
  
  # Check for npm packages
  if [ ! -d "node_modules/airtable" ]; then
    log "Installing npm packages..."
    npm install airtable dotenv
  fi
  
  log "All dependencies satisfied"
}

# Process frames with OCR and LLM
process_frames() {
  local folder_pattern="$1"
  local limit="$2"
  local batch_size="$3"
  
  if [ -z "$folder_pattern" ]; then
    log "ERROR: No folder pattern specified"
    exit 1
  fi
  
  log "Processing frames with OCR and LLM..."
  log "Folder pattern: $folder_pattern"
  
  if [ -n "$limit" ]; then
    log "Limit: $limit frames"
    python process_frames_by_path.py --folder-path-pattern "$folder_pattern" --limit "$limit" --batch-size "$batch_size"
  else
    log "Processing all matching frames"
    python process_frames_by_path.py --folder-path-pattern "$folder_pattern" --batch-size "$batch_size"
  fi
  
  if [ $? -ne 0 ]; then
    log "ERROR: Frame processing failed"
    exit 1
  fi
  
  log "Frame processing completed successfully"
}

# Parse OCRData and update Flagged field
parse_ocr_data() {
  local batch_size="$1"
  local only_unprocessed="$2"
  
  log "Parsing OCR data and updating Flagged field..."
  log "Only unprocessed: $only_unprocessed"
  
  node parse_ocr_data.js "$batch_size" "$only_unprocessed"
  
  if [ $? -ne 0 ]; then
    log "ERROR: OCR data parsing failed"
    exit 1
  fi
  
  log "OCR data parsing completed successfully"
}

# Process folders chronologically from oldest to newest
process_folders_chronologically() {
  local base_dir="$1"
  local limit="$2"
  local batch_size="$3"
  
  log "Finding and sorting folders chronologically..."
  
  # Get all screen recording folders
  local folders=()
  for folder in "$base_dir"/screen_recording_*; do
    if [ -d "$folder" ]; then
      folders+=("$folder")
    fi
  done
  
  if [ ${#folders[@]} -eq 0 ]; then
    log "No screen recording folders found in $base_dir"
    return 1
  fi
  
  log "Found ${#folders[@]} screen recording folders"
  
  # Sort folders chronologically by extracting date parts from folder names
  # This assumes folder name format like screen_recording_YYYY_MM_DD_*
  local sorted_folders=()
  sorted_folders=($(printf "%s\n" "${folders[@]}" | sort))
  
  log "Folders sorted chronologically, processing from oldest to newest:"
  
  # Apply limit if specified
  if [ -n "$limit" ] && [ "$limit" -gt 0 ]; then
    log "Limiting to $limit folders"
    if [ "$limit" -lt ${#sorted_folders[@]} ]; then
      sorted_folders=("${sorted_folders[@]:0:$limit}")
    fi
  fi
  
  # Process each folder
  for folder in "${sorted_folders[@]}"; do
    folder_name=$(basename "$folder")
    log "Processing folder: $folder_name"
    
    # Process all frames in this folder
    process_frames "$folder/*.jpg" "" "$batch_size"
    
    log "Completed folder: $folder_name"
  done
  
  log "All folders processed successfully"
  return 0
}

# Main function
main() {
  log "Starting OCR pipeline..."
  
  # Parse command line arguments
  local folder_pattern=""
  local limit=""
  local batch_size="10"
  local js_batch_size="100"
  local only_unprocessed="true"
  local process_chronologically="false"
  local base_dir="/home/jason/Videos/screenRecordings" # Default base directory
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --folder-pattern)
        folder_pattern="$2"
        shift 2
        ;;
      --limit)
        limit="$2"
        shift 2
        ;;
      --batch-size)
        batch_size="$2"
        shift 2
        ;;
      --js-batch-size)
        js_batch_size="$2"
        shift 2
        ;;
      --only-unprocessed)
        only_unprocessed="$2"
        shift 2
        ;;
      --process-chronologically)
        process_chronologically="$2"
        shift 2
        ;;
      --base-dir)
        base_dir="$2"
        shift 2
        ;;
      *)
        log "Unknown option: $1"
        exit 1
        ;;
    esac
  done
  
  # Check dependencies
  check_dependencies
  
  # Check if we should process chronologically
  if [ "$process_chronologically" = "true" ]; then
    log "Processing folders chronologically from oldest to newest"
    process_folders_chronologically "$base_dir" "$limit" "$batch_size"
  elif [ -n "$folder_pattern" ]; then
    # Process the specified pattern
    process_frames "$folder_pattern" "$limit" "$batch_size"
  else
    log "ERROR: Either --folder-pattern or --process-chronologically must be provided"
    exit 1
  fi
  
  # Parse OCR data
  parse_ocr_data "$js_batch_size" "$only_unprocessed"
  
  log "OCR pipeline completed successfully"
}

# Run the main function with all arguments
main "$@" 