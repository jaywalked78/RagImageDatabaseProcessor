#!/bin/bash
# Process All Frames - Folder by Folder
# Processes one folder at a time in chronological order

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
DELAY_BETWEEN_BATCHES=2  # seconds
DELAY_BETWEEN_FOLDERS=5  # seconds
START_FOLDER=""
MAX_FOLDERS=0  # 0 means process all folders
DEBUG_MODE=false

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
    --max-folders|-m)
      MAX_FOLDERS="$2"
      shift 2
      ;;
    --delay-batches|-db)
      DELAY_BETWEEN_BATCHES="$2"
      shift 2
      ;;
    --delay-folders|-df)
      DELAY_BETWEEN_FOLDERS="$2"
      shift 2
      ;;
    --debug|-d)
      DEBUG_MODE=true
      shift
      ;;
    *)
      log "Unknown option: $1"
      exit 1
      ;;
  esac
done

log "Starting folder-by-folder frame processing"
log "Batch size: $BATCH_SIZE"
log "Delay between batches: $DELAY_BETWEEN_BATCHES seconds"
log "Delay between folders: $DELAY_BETWEEN_FOLDERS seconds"
if [ "$DEBUG_MODE" = true ]; then
  log "DEBUG MODE: Enabled (verbose output)"
fi

if [ -n "$START_FOLDER" ]; then
  log "Starting from folder: $START_FOLDER"
fi

if [ "$MAX_FOLDERS" -gt 0 ]; then
  log "Will process at most $MAX_FOLDERS folders"
fi

# Function to process a single folder
process_folder() {
  local folder="$1"
  local folder_basename=$(basename "$folder")
  
  log "Processing folder: $folder_basename"
  
  # Get the count of records for this folder
  log "Counting records in folder: $folder"
  local FOLDER_RECORD_COUNT=$(node -e "
    const Airtable = require('airtable');
    require('dotenv').config();
    const base = new Airtable({ apiKey: process.env.AIRTABLE_PERSONAL_ACCESS_TOKEN }).base(process.env.AIRTABLE_BASE_ID);
    const table = base(process.env.AIRTABLE_TABLE_NAME || 'tblFrameAnalysis');
    
    async function countRecords() {
      try {
        // Construct filter formula to match folder path pattern
        const filterFormula = \`FIND(\\\"${folder}/\\\", {FolderPath}) = 1\`;
        
        const records = await table.select({
          filterByFormula: filterFormula
        }).all();
        
        console.log(records.length);
      } catch (error) {
        console.error(error);
        process.exit(1);
      }
    }
    
    countRecords();
  ")
  
  if [ -z "$FOLDER_RECORD_COUNT" ] || [ "$FOLDER_RECORD_COUNT" -eq 0 ]; then
    log "No records found for folder: $folder_basename, skipping"
    return 0
  fi
  
  log "Found $FOLDER_RECORD_COUNT records in folder: $folder_basename"
  
  # Process folder with cursor-based pagination
  local batch=1
  local next_token=""
  local has_more=true
  
  while [ "$has_more" = true ]; do
    log "Processing batch $batch for folder: $folder_basename"
    
    # Create a temporary file to store output
    local output_file=$(mktemp)
    
    # Run the processor for this folder with the current page token and capture all output
    node direct_ocr_process.js $BATCH_SIZE "$folder" "$next_token" > "$output_file" 2>&1
    
    # Check if the process was successful
    if [ $? -ne 0 ]; then
      log "ERROR: Failed to process batch $batch for folder: $folder_basename"
      cat "$output_file"  # Output the error
      rm "$output_file"
      return 1
    fi
    
    # Display debug output if requested
    if [ "$DEBUG_MODE" = true ]; then
      log "DEBUG: Output from OCR process:"
      cat "$output_file"
    fi
    
    log "Successfully processed batch $batch for folder: $folder_basename"
    
    # Extract next page token from the output file
    next_token=$(grep "NEXT_PAGE_TOKEN:" "$output_file" | tail -n 1 | cut -d ":" -f 2-)
    
    # Log the token for debugging
    if [ "$DEBUG_MODE" = true ]; then
      log "DEBUG: Next page token: '$next_token'"
    fi
    
    # Clean up temporary file
    rm "$output_file"
    
    # Check if we have more pages to process
    if [ -z "$next_token" ] || [ "$next_token" = "undefined" ] || [ "$next_token" = "null" ]; then
      has_more=false
      log "No more pages for folder: $folder_basename"
    else
      batch=$((batch + 1))
      
      # Log the progress through the folder
      local progress=$((batch * BATCH_SIZE))
      if [ $progress -gt $FOLDER_RECORD_COUNT ]; then
        progress=$FOLDER_RECORD_COUNT
      fi
      log "Progress: $progress/$FOLDER_RECORD_COUNT records processed"
      
      # Delay between batches
      log "Waiting $DELAY_BETWEEN_BATCHES seconds before next batch..."
      sleep $DELAY_BETWEEN_BATCHES
    fi
  done
  
  log "Completed processing folder: $folder_basename"
  return 0
}

# Get list of unique folder paths from Airtable
log "Getting list of unique folders from Airtable..."
FOLDERS=$(node -e "
  const Airtable = require('airtable');
  require('dotenv').config();
  const base = new Airtable({ apiKey: process.env.AIRTABLE_PERSONAL_ACCESS_TOKEN }).base(process.env.AIRTABLE_BASE_ID);
  const table = base(process.env.AIRTABLE_TABLE_NAME || 'tblFrameAnalysis');
  
  async function getFolders() {
    try {
      const records = await table.select({
        fields: ['FolderPath']
      }).all();
      
      // Extract unique folder paths
      const folderPaths = new Set();
      records.forEach(record => {
        const path = record.get('FolderPath');
        if (path) {
          // Extract the folder part (up to the last /)
          const folderPath = path.substring(0, path.lastIndexOf('/'));
          folderPaths.add(folderPath);
        }
      });
      
      // Sort folders chronologically based on their names
      const sortedFolders = Array.from(folderPaths).sort();
      console.log(sortedFolders.join('\\n'));
    } catch (error) {
      console.error(error);
      process.exit(1);
    }
  }
  
  getFolders();
")

if [ -z "$FOLDERS" ]; then
  log "ERROR: Failed to get folder list from Airtable"
  exit 1
fi

# Convert to array
IFS=$'\n' read -r -d '' -a FOLDER_ARRAY < <(echo "$FOLDERS" && printf '\0')

log "Found ${#FOLDER_ARRAY[@]} unique folders to process"

# Check if we should start from a specific folder
START_PROCESSING=true
if [ -n "$START_FOLDER" ]; then
  START_PROCESSING=false
  log "Will start processing from folder containing: $START_FOLDER"
fi

# Process each folder in order
PROCESSED_FOLDERS=0
for folder in "${FOLDER_ARRAY[@]}"; do
  # Skip until we find the start folder
  if [ "$START_PROCESSING" = false ]; then
    if [[ "$folder" == *"$START_FOLDER"* ]]; then
      START_PROCESSING=true
      log "Found start folder: $folder, beginning processing"
    else
      log "Skipping folder: $(basename "$folder") (waiting for start folder)"
      continue
    fi
  fi
  
  process_folder "$folder"
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

# Verify the results
log "Processing complete! Verifying results..."
node verify_ocr_results.js

log "All folders processed successfully! Processed $PROCESSED_FOLDERS folders." 