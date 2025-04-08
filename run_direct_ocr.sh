#!/bin/bash
# Direct OCR Processing Script
# Performs OCR directly on the images and updates Airtable with proper flagged values

# Set up error handling
set -e

# Load environment variables
source .env

# Log function
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Default parameters
BATCH_SIZE=5
SPECIFIC_FOLDER=""

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
    *)
      log "Unknown option: $1"
      exit 1
      ;;
  esac
done

log "Starting direct OCR processing"
log "Batch size: $BATCH_SIZE"

if [ -n "$SPECIFIC_FOLDER" ]; then
  log "Processing specific folder: $SPECIFIC_FOLDER"
  node direct_ocr_process.js $BATCH_SIZE "$SPECIFIC_FOLDER"
else
  log "Processing all records (no specific folder)"
  node direct_ocr_process.js $BATCH_SIZE
fi

log "OCR processing complete!" 