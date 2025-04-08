#!/bin/bash
# Full OCR pipeline script
# Processes all records chronologically from oldest to newest

# Set up error handling
set -e
set -o pipefail

# Load environment variables
source .env

# Log function
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Check if Airtable environment variables are set
if [[ -z "$AIRTABLE_PERSONAL_ACCESS_TOKEN" || -z "$AIRTABLE_BASE_ID" || -z "$AIRTABLE_TABLE_NAME" ]]; then
  log "ERROR: Airtable environment variables not set. Please check your .env file."
  exit 1
fi

# Configuration
BATCH_SIZE=10
PROCESS_ALL=true  # Set to true to process all records, false to only process unprocessed records

# Start the pipeline
log "Starting full OCR pipeline"
log "Batch size: $BATCH_SIZE"
log "Process all: $PROCESS_ALL"

# Step 1: Process OCR data and detect sensitive information
log "Step 1: Processing OCR data and detecting sensitive information"
if [ "$PROCESS_ALL" = true ]; then
  log "Processing ALL records chronologically"
  node parse_ocr_data.js $BATCH_SIZE false
else
  log "Processing only unprocessed records"
  node parse_ocr_data.js $BATCH_SIZE true
fi
if [ $? -ne 0 ]; then
  log "ERROR: OCR data processing failed"
  exit 1
fi

log "OCR pipeline completed successfully"
exit 0 