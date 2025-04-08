#!/bin/bash
# Script to reset all Flagged fields and run OCR processing
# Use this when starting from scratch

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
SKIP_EXISTING=false  # Set to true to preserve existing flags
PRESERVE_SENSITIVE=true  # Set to true to preserve records flagged as sensitive

# Start the process
log "Starting pipeline with Flagged field reset"
log "Batch size: $BATCH_SIZE"
log "Skip existing flags: $SKIP_EXISTING"
log "Preserve sensitive flags: $PRESERVE_SENSITIVE"

# Step 1: Reset all Flagged fields to false, but preserve sensitive if requested
log "Step 1: Resetting applicable Flagged fields to 'false'"

if [ "$PRESERVE_SENSITIVE" = true ]; then
  log "Preserving records with 'true' in their flagged field"
  node update_flagged_field.js $BATCH_SIZE false $SKIP_EXISTING "true"
else
  log "Resetting ALL records (even sensitive ones)"
  node update_flagged_field.js $BATCH_SIZE false $SKIP_EXISTING
fi

if [ $? -ne 0 ]; then
  log "ERROR: Failed to reset Flagged fields"
  exit 1
fi

# Step 2 (Optional): Process OCR data for any records that have it
log "Step 2: Running OCR processor for any records with OCR data"
node parse_ocr_data.js $BATCH_SIZE false
if [ $? -ne 0 ]; then
  log "ERROR: OCR processor failed"
  exit 1
fi

log "Process completed successfully"
exit 0 