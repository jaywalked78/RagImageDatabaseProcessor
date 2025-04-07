#!/bin/bash
# Script to process all frames in the base directory and subdirectories
# Usage: ./scripts/process_all_frames.sh [options]
#
# Optional arguments:
#   --limit N            : Process only N frames per directory (default: 0 for all)
#   --chunk-size N       : Size of text chunks (default: 500)
#   --chunk-overlap N    : Overlap between chunks (default: 50)
#   --max-chunks N       : Maximum chunks per frame (default: 10)
#   --storage-dir DIR    : Directory to store results (default: all_frame_embeddings)
#   --dry-run            : Print what would be processed without actually processing
#   --force              : Force reprocessing of already processed frames
#   --check-db           : Check database for existing frames before processing (requires DB connection)
#   --skip-dupe-chunks   : Skip frames whose chunks already exist in the database
#   --enable-ocr         : Enable OCR text extraction using Tesseract
#   --skip-ocr           : Skip OCR even if it's installed (faster processing)
#   --help               : Display this help message

# Load environment variables
if [ -f "scripts/load_env.sh" ]; then
  source scripts/load_env.sh
fi

# Default values
LIMIT=0
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_CHUNKS=10
STORAGE_DIR="all_frame_embeddings"
DRY_RUN=false
FORCE=false
CHECK_DB=false
SKIP_DUPE_CHUNKS=false
ENABLE_OCR=false
SKIP_OCR=false
BASE_DIR="/home/jason/Videos/screenRecordings"

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --limit)
      LIMIT="$2"
      shift 2
      ;;
    --chunk-size)
      CHUNK_SIZE="$2"
      shift 2
      ;;
    --chunk-overlap)
      CHUNK_OVERLAP="$2"
      shift 2
      ;;
    --max-chunks)
      MAX_CHUNKS="$2"
      shift 2
      ;;
    --storage-dir)
      STORAGE_DIR="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --force)
      FORCE=true
      shift
      ;;
    --check-db)
      CHECK_DB=true
      shift
      ;;
    --skip-dupe-chunks)
      SKIP_DUPE_CHUNKS=true
      shift
      ;;
    --enable-ocr)
      ENABLE_OCR=true
      shift
      ;;
    --skip-ocr)
      SKIP_OCR=true
      shift
      ;;
    --help)
      echo "Usage: ./scripts/process_all_frames.sh [options]"
      echo ""
      echo "Optional arguments:"
      echo "  --limit N            : Process only N frames per directory (default: 0 for all)"
      echo "  --chunk-size N       : Size of text chunks (default: 500)"
      echo "  --chunk-overlap N    : Overlap between chunks (default: 50)"
      echo "  --max-chunks N       : Maximum chunks per frame (default: 10)"
      echo "  --storage-dir DIR    : Directory to store results (default: all_frame_embeddings)"
      echo "  --dry-run            : Print what would be processed without actually processing"
      echo "  --force              : Force reprocessing of already processed frames"
      echo "  --check-db           : Check database for existing frames before processing"
      echo "  --skip-dupe-chunks   : Skip frames whose chunks already exist in the database"
      echo "  --enable-ocr         : Enable OCR text extraction using Tesseract"
      echo "  --skip-ocr           : Skip OCR even if it's installed (faster processing)"
      echo "  --help               : Display this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Create storage directory if it doesn't exist
mkdir -p "$STORAGE_DIR/payloads/json"
mkdir -p "$STORAGE_DIR/payloads/csv"
mkdir -p "$STORAGE_DIR/payloads/ocr"
mkdir -p "$STORAGE_DIR/logs"

# Create or access processed frames log
PROCESSED_FRAMES_CSV="$STORAGE_DIR/payloads/csv/processed_frames.csv"
if [ ! -f "$PROCESSED_FRAMES_CSV" ]; then
  echo "frame_path,processed_time,status,frame_id,metadata_size,ocr_status" > "$PROCESSED_FRAMES_CSV"
  echo "Created new processed frames log at $PROCESSED_FRAMES_CSV"
fi

# Create or access chunks log
FRAME_CHUNKS_CSV="$STORAGE_DIR/payloads/csv/frame_chunks.csv"
if [ ! -f "$FRAME_CHUNKS_CSV" ]; then
  echo "frame_id,chunk_index,chunk_hash,content_length,processed_time,source" > "$FRAME_CHUNKS_CSV"
  echo "Created new frame chunks log at $FRAME_CHUNKS_CSV"
fi

# Create or access OCR text log
OCR_TEXT_CSV="$STORAGE_DIR/payloads/csv/ocr_text.csv"
if [ ! -f "$OCR_TEXT_CSV" ]; then
  echo "frame_id,ocr_text,confidence,processed_time,ocr_hash" > "$OCR_TEXT_CSV"
  echo "Created new OCR text log at $OCR_TEXT_CSV"
fi

# Check if tesseract is installed
if command -v tesseract &> /dev/null; then
  TESSERACT_AVAILABLE=true
  echo "Tesseract OCR is available."
  # Enable OCR by default if available and not explicitly skipped
  if [ "$SKIP_OCR" = false ] && [ "$ENABLE_OCR" = false ]; then
    ENABLE_OCR=true
    echo "OCR enabled by default. Use --skip-ocr to disable."
  fi
else
  TESSERACT_AVAILABLE=false
  echo "Tesseract OCR not found. OCR features will be disabled."
  ENABLE_OCR=false
fi

if [ "$ENABLE_OCR" = true ] && [ "$TESSERACT_AVAILABLE" = false ]; then
  echo "Error: OCR requested but Tesseract is not available."
  echo "Please install Tesseract OCR first with: sudo apt-get install tesseract-ocr"
  exit 1
fi

if [ "$SKIP_OCR" = true ]; then
  ENABLE_OCR=false
  echo "OCR processing disabled by --skip-ocr flag."
fi

# Get directories and sort by timestamp in folder name
# This assumes folder names contain timestamps in a format like YYYY-MM-DD_HH-MM-SS or similar
# Get all subdirectories
ALL_DIRS=$(find "$BASE_DIR" -type d)

# Create an array for sorted directories
declare -a SORTED_DIRS

# Extract timestamp information and sort
for DIR in $ALL_DIRS; do
  # Skip the base directory itself
  if [ "$DIR" = "$BASE_DIR" ]; then
    continue
  fi
  
  # Extract the directory name
  DIR_NAME=$(basename "$DIR")
  
  # Try to extract date components - adjust regex as needed for your naming format
  if [[ "$DIR_NAME" =~ ([0-9]{4})-?([0-9]{2})-?([0-9]{2})[-_]?([0-9]{2})?[:-]?([0-9]{2})?[:-]?([0-9]{2})? ]]; then
    # Create a sortable string (YYYYMMDDHHMMSS)
    YEAR="${BASH_REMATCH[1]:-0000}"
    MONTH="${BASH_REMATCH[2]:-00}"
    DAY="${BASH_REMATCH[3]:-00}"
    HOUR="${BASH_REMATCH[4]:-00}"
    MINUTE="${BASH_REMATCH[5]:-00}"
    SECOND="${BASH_REMATCH[6]:-00}"
    
    TIMESTAMP="${YEAR}${MONTH}${DAY}${HOUR}${MINUTE}${SECOND}"
    
    # Add to the sorted dirs array with timestamp prefix for sorting
    SORTED_DIRS+=("$TIMESTAMP:$DIR")
  else
    # If no timestamp found, use a very high value to sort at the end
    SORTED_DIRS+=("99999999999999:$DIR")
  fi
done

# Sort the array
IFS=$'\n' SORTED_DIRS=($(sort <<<"${SORTED_DIRS[*]}"))
unset IFS

# Extract just the directory paths from sorted array
SUBDIRS=()
for ENTRY in "${SORTED_DIRS[@]}"; do
  DIR="${ENTRY#*:}"
  SUBDIRS+=("$DIR")
done

# Total count of frames
TOTAL_FRAMES=$(find "$BASE_DIR" -type f -name "*.jpg" | wc -l)
echo "Found $TOTAL_FRAMES total frames in $BASE_DIR and subdirectories"
echo "Will store results in $STORAGE_DIR"
echo ""

# Generate timestamp for logs
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$STORAGE_DIR/logs/processing_${TIMESTAMP}.log"
SUMMARY_FILE="$STORAGE_DIR/logs/summary_${TIMESTAMP}.txt"

echo "Logging to: $LOG_FILE"
echo "Summary will be saved to: $SUMMARY_FILE"

# Start the log file
echo "===== Processing Started at $(date -Iseconds) =====" > "$LOG_FILE"
echo "Base directory: $BASE_DIR" >> "$LOG_FILE"
echo "Storage directory: $STORAGE_DIR" >> "$LOG_FILE"
echo "Total frames found: $TOTAL_FRAMES" >> "$LOG_FILE"
echo "Chunk size: $CHUNK_SIZE" >> "$LOG_FILE"
echo "Chunk overlap: $CHUNK_OVERLAP" >> "$LOG_FILE"
echo "Maximum chunks per frame: $MAX_CHUNKS" >> "$LOG_FILE"
echo "Force reprocessing: $FORCE" >> "$LOG_FILE"
echo "Check database: $CHECK_DB" >> "$LOG_FILE"
echo "Skip duplicate chunks: $SKIP_DUPE_CHUNKS" >> "$LOG_FILE"
echo "OCR enabled: $ENABLE_OCR" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Counter for processed folders and frames
PROCESSED_FOLDERS=0
PROCESSED_FRAMES=0
PROCESSED_CHUNKS=0
FAILED_FRAMES=0
SKIPPED_FRAMES=0
DB_SKIPPED_FRAMES=0
DUPE_CHUNKS_SKIPPED=0
OCR_PROCESSED=0
OCR_FAILED=0

# Function to check if a frame has already been processed
frame_is_processed() {
  local frame_path="$1"
  local frame_filename=$(basename "$frame_path")
  local json_path="$STORAGE_DIR/payloads/json/${frame_filename%.jpg}.json"
  
  # First check if JSON file exists
  if [ -f "$json_path" ]; then
    return 0  # Frame is processed (JSON exists)
  fi
  
  # Then check the CSV log
  if grep -q "\"$frame_path\"" "$PROCESSED_FRAMES_CSV"; then
    return 0  # Frame is processed (in CSV log)
  fi
  
  return 1  # Frame is not processed
}

# Function to check if OCR has been done for a frame
ocr_is_done() {
  local frame_path="$1"
  local frame_filename=$(basename "$frame_path")
  local frame_id="${frame_filename%.jpg}"
  local ocr_path="$STORAGE_DIR/payloads/ocr/${frame_id}.txt"
  
  # First check if OCR file exists
  if [ -f "$ocr_path" ]; then
    return 0  # OCR is done (file exists)
  fi
  
  # Then check the CSV log
  if grep -q "\"$frame_id\"" "$OCR_TEXT_CSV"; then
    return 0  # OCR is done (in CSV log)
  fi
  
  return 1  # OCR not done
}

# Function to run OCR on a frame and save results
run_ocr() {
  local frame_path="$1"
  local frame_filename=$(basename "$frame_path")
  local frame_id="${frame_filename%.jpg}"
  local ocr_path="$STORAGE_DIR/payloads/ocr/${frame_id}.txt"
  
  # Skip if OCR is disabled or already done
  if [ "$ENABLE_OCR" = false ]; then
    return 1
  fi
  
  if [ "$FORCE" = false ] && ocr_is_done "$frame_path"; then
    echo "  OCR already done for $frame_filename, skipping" >> "$LOG_FILE"
    return 0
  fi
  
  echo "  Running OCR on $frame_filename" >> "$LOG_FILE"
  
  # Run tesseract OCR
  tesseract "$frame_path" "$STORAGE_DIR/payloads/ocr/${frame_id}" -l eng 2>/dev/null
  
  if [ -f "$ocr_path" ]; then
    # Get OCR text
    local ocr_text=$(cat "$ocr_path")
    local text_length=${#ocr_text}
    
    # Calculate hash of OCR text
    local ocr_hash=$(echo -n "$ocr_text" | md5sum | cut -d' ' -f1)
    
    # Get timestamp
    local current_time=$(date -Iseconds)
    
    # Escape quotes and newlines in OCR text for CSV
    ocr_text=$(echo "$ocr_text" | sed ':a;N;$!ba;s/\n/ /g' | sed 's/"/\\"/g')
    
    # Add to CSV, using 100 as default confidence (we don't have actual confidence scores)
    echo "\"$frame_id\",\"$ocr_text\",\"100\",\"$current_time\",\"$ocr_hash\"" >> "$OCR_TEXT_CSV"
    
    OCR_PROCESSED=$((OCR_PROCESSED + 1))
    return 0
  else
    echo "  OCR failed for $frame_filename" >> "$LOG_FILE"
    OCR_FAILED=$((OCR_FAILED + 1))
    return 1
  fi
}

# Function to check if frame exists in database
frame_in_database() {
  if [ "$CHECK_DB" = false ]; then
    return 1  # Skip database check
  fi
  
  local frame_path="$1"
  local frame_filename=$(basename "$frame_path")
  
  # Use the check_duplicates.py script to check if this frame exists in the DB
  DB_CHECK=$(python scripts/check_duplicates.py --frame "$frame_path" --check-db --quiet 2>/dev/null)
  
  # Check exit code - 0 means frame was found, 1 means not found
  if [ $? -eq 0 ]; then
    echo "  Frame exists in database: $frame_filename" >> "$LOG_FILE"
    return 0  # Frame exists in DB
  fi
  
  return 1  # Frame does not exist in DB
}

# Function to check if we have duplicate chunks with identical content
has_duplicate_chunks() {
  if [ "$SKIP_DUPE_CHUNKS" = false ]; then
    return 1  # Skip this check if not enabled
  fi
  
  local frame_path="$1"
  local frame_filename=$(basename "$frame_path")
  local frame_id="${frame_filename%.jpg}"
  
  # First check if we have OCR text to check for duplicates
  local ocr_path="$STORAGE_DIR/payloads/ocr/${frame_id}.txt"
  
  if [ -f "$ocr_path" ]; then
    # Get OCR text hash
    local ocr_text=$(cat "$ocr_path")
    local ocr_hash=$(echo -n "$ocr_text" | md5sum | cut -d' ' -f1)
    
    # Check if this content hash exists in our chunks database
    # Use the check_duplicates.py script to check if this chunk hash exists in the CSV or DB
    CHUNK_CHECK=$(python scripts/check_duplicates.py --chunk-hash "$ocr_hash" --quiet 2>/dev/null)
    
    # Check exit code - 0 means chunk was found, 1 means not found
    CHUNK_FOUND=$?
    
    if [ $CHUNK_FOUND -eq 0 ]; then
      echo "  Duplicate chunk content detected for frame: $frame_filename (hash: $ocr_hash)" >> "$LOG_FILE"
      DUPE_CHUNKS_SKIPPED=$((DUPE_CHUNKS_SKIPPED + 1))
      return 0  # Duplicate chunks exist
    fi
  elif [ "$TESSERACT_AVAILABLE" = true ] && [ "$ENABLE_OCR" = true ]; then
    # Extract a small sample of text from the image with OCR
    local sample_text_file="/tmp/frame_sample_${frame_id}.txt"
    tesseract "$frame_path" stdout 2>/dev/null | head -c 100 > "$sample_text_file"
    
    if [ -s "$sample_text_file" ]; then
      # Generate hash of the sample text
      local content_hash=$(md5sum "$sample_text_file" | cut -d' ' -f1)
      
      # Check if this content hash exists in our chunks database
      CHUNK_CHECK=$(python scripts/check_duplicates.py --chunk-hash "$content_hash" --quiet 2>/dev/null)
      
      # Check exit code - 0 means chunk was found, 1 means not found
      CHUNK_FOUND=$?
      
      # Clean up
      rm "$sample_text_file"
      
      if [ $CHUNK_FOUND -eq 0 ]; then
        echo "  Duplicate chunk content detected for frame: $frame_filename (hash: $content_hash)" >> "$LOG_FILE"
        DUPE_CHUNKS_SKIPPED=$((DUPE_CHUNKS_SKIPPED + 1))
        return 0  # Duplicate chunks exist
      fi
    fi
    
    # Clean up
    rm -f "$sample_text_file"
  fi
  
  return 1  # No duplicate chunks or couldn't check
}

# Function to extract chunks from a processed JSON file and add to chunks CSV
extract_chunks() {
  local json_path="$1"
  local frame_path="$2"
  local processed_time="$3"
  
  # Skip if JSON doesn't exist
  if [ ! -f "$json_path" ]; then
    return
  fi
  
  # Generate a unique frame_id based on the filename
  local frame_filename=$(basename "$frame_path")
  local frame_id="${frame_filename%.jpg}"
  
  # Check if this frame's chunks are already in the chunks CSV
  if grep -q "\"$frame_id\"" "$FRAME_CHUNKS_CSV"; then
    # Skip if we're not forcing reprocessing
    if [ "$FORCE" = false ]; then
      return
    fi
  fi
  
  # Extract chunks from JSON and add to CSV
  # Extract with jq if available, otherwise use grep/sed (basic)
  if command -v jq &> /dev/null; then
    # Use jq to extract chunks
    local chunks_json=$(jq -r '.chunks[]? | "\(.index),\(.content)"' "$json_path" 2>/dev/null)
    
    if [ -n "$chunks_json" ]; then
      # Count how many chunks we extracted
      local chunk_count=$(echo "$chunks_json" | wc -l)
      PROCESSED_CHUNKS=$((PROCESSED_CHUNKS + chunk_count))
      
      # For each chunk, add to the CSV
      while IFS="," read -r index content; do
        # Generate hash of content
        local content_hash=$(echo -n "$content" | md5sum | cut -d' ' -f1)
        local content_length=${#content}
        
        # Add to CSV
        echo "\"$frame_id\",\"$index\",\"$content_hash\",\"$content_length\",\"$processed_time\",\"json\"" >> "$FRAME_CHUNKS_CSV"
      done <<< "$chunks_json"
      
      # Also update the frame CSV with metadata size and OCR status
      local metadata_size=$(jq '.metadata | length' "$json_path" 2>/dev/null || echo "0")
      local ocr_status="none"
      
      # Check if OCR was done
      if ocr_is_done "$frame_path"; then
        ocr_status="done"
      fi
      
      # Update the frame entry
      sed -i "s|\"$frame_path\",\"$processed_time\",\"success\"|\"$frame_path\",\"$processed_time\",\"success\",\"$frame_id\",\"$metadata_size\",\"$ocr_status\"|" "$PROCESSED_FRAMES_CSV"
      
      # If OCR was done, also add the OCR text as a chunk
      local ocr_path="$STORAGE_DIR/payloads/ocr/${frame_id}.txt"
      if [ -f "$ocr_path" ]; then
        local ocr_text=$(cat "$ocr_path")
        local ocr_hash=$(echo -n "$ocr_text" | md5sum | cut -d' ' -f1)
        local ocr_length=${#ocr_text}
        
        # Add OCR as a special chunk with negative index (-1)
        echo "\"$frame_id\",\"-1\",\"$ocr_hash\",\"$ocr_length\",\"$processed_time\",\"ocr\"" >> "$FRAME_CHUNKS_CSV"
        
        # Increment chunk count
        PROCESSED_CHUNKS=$((PROCESSED_CHUNKS + 1))
      fi
    fi
  else
    # Basic grep-based extraction (not as reliable as jq)
    echo "Warning: jq not found, using basic extraction" >> "$LOG_FILE"
    
    # Using basic extraction
    local chunk_count=$(grep -c "\"content\":" "$json_path")
    PROCESSED_CHUNKS=$((PROCESSED_CHUNKS + chunk_count))
    
    # Just add a basic entry to the frame CSV
    local ocr_status="none"
    if ocr_is_done "$frame_path"; then
      ocr_status="done"
    fi
    
    sed -i "s|\"$frame_path\",\"$processed_time\",\"success\"|\"$frame_path\",\"$processed_time\",\"success\",\"$frame_id\",\"0\",\"$ocr_status\"|" "$PROCESSED_FRAMES_CSV"
  fi
}

# Loop through each subdirectory
for DIR in "${SUBDIRS[@]}"; do
  # Count JPG files in this directory
  NUM_FILES=$(find "$DIR" -maxdepth 1 -type f -name "*.jpg" | wc -l)
  
  if [ "$NUM_FILES" -eq 0 ]; then
    # Skip directories with no JPG files
    continue
  fi
  
  PROCESSED_FOLDERS=$((PROCESSED_FOLDERS + 1))
  
  # Directory name for display
  DIR_NAME=$(basename "$DIR")
  
  # Extract timestamp info for logging
  TIMESTAMP_INFO=""
  if [[ "$DIR_NAME" =~ ([0-9]{4})-?([0-9]{2})-?([0-9]{2})[-_]?([0-9]{2})?[:-]?([0-9]{2})?[:-]?([0-9]{2})? ]]; then
    YEAR="${BASH_REMATCH[1]:-0000}"
    MONTH="${BASH_REMATCH[2]:-00}"
    DAY="${BASH_REMATCH[3]:-00}"
    HOUR="${BASH_REMATCH[4]:-00}"
    MINUTE="${BASH_REMATCH[5]:-00}"
    SECOND="${BASH_REMATCH[6]:-00}"
    TIMESTAMP_INFO=" (Date: $YEAR-$MONTH-$DAY $HOUR:$MINUTE:$SECOND)"
  fi
  
  echo "Processing directory $DIR_NAME$TIMESTAMP_INFO ($NUM_FILES frames)"
  echo "$(date -Iseconds) - Processing directory: $DIR$TIMESTAMP_INFO ($NUM_FILES frames)" >> "$LOG_FILE"
  
  # Get list of frames to process
  FRAMES=$(find "$DIR" -maxdepth 1 -type f -name "*.jpg" | sort)
  
  # Apply limit if specified
  if [ "$LIMIT" -gt 0 ]; then
    FRAMES=$(echo "$FRAMES" | head -n "$LIMIT")
    echo "  Limited to $LIMIT frames"
    echo "  Limited to $LIMIT frames" >> "$LOG_FILE"
  fi
  
  # Count frames to process in this directory
  TO_PROCESS=0
  ALREADY_PROCESSED=0
  DB_EXISTS=0
  DUPE_CHUNKS=0
  
  # First pass: Run OCR on all frames if enabled
  if [ "$ENABLE_OCR" = true ]; then
    echo "  Running OCR on frames in $DIR_NAME"
    echo "  Running OCR on frames in $DIR_NAME" >> "$LOG_FILE"
    
    for FRAME in $FRAMES; do
      FRAME_BASENAME=$(basename "$FRAME")
      
      # Run OCR on frames we haven't processed yet
      if [ "$FORCE" = true ] || ! ocr_is_done "$FRAME"; then
        run_ocr "$FRAME"
      fi
    done
    
    echo "  OCR completed for directory $DIR_NAME"
    echo "  OCR completed for directory $DIR_NAME" >> "$LOG_FILE"
  fi
  
  # Second pass: Check which frames need processing
  for FRAME in $FRAMES; do
    FRAME_BASENAME=$(basename "$FRAME")
    
    if [ "$FORCE" = true ]; then
      # Force reprocessing regardless of local or DB status
      TO_PROCESS=$((TO_PROCESS + 1))
      echo "  Force processing: $FRAME_BASENAME" >> "$LOG_FILE"
    elif frame_is_processed "$FRAME"; then
      # Skip if already processed locally
      ALREADY_PROCESSED=$((ALREADY_PROCESSED + 1))
      echo "  Already processed locally: $FRAME_BASENAME" >> "$LOG_FILE"
    elif frame_in_database "$FRAME"; then
      # Skip if exists in database
      DB_EXISTS=$((DB_EXISTS + 1))
      echo "  Exists in database: $FRAME_BASENAME" >> "$LOG_FILE"
    elif has_duplicate_chunks "$FRAME"; then
      # Skip if duplicate chunks exist
      DUPE_CHUNKS=$((DUPE_CHUNKS + 1))
      echo "  Duplicate chunks exist for: $FRAME_BASENAME" >> "$LOG_FILE"
    else
      # Need to process this frame
      TO_PROCESS=$((TO_PROCESS + 1))
    fi
  done
  
  if [ "$ALREADY_PROCESSED" -gt 0 ]; then
    echo "  Found $ALREADY_PROCESSED already processed frames (skipping)"
    echo "  Skipping $ALREADY_PROCESSED already processed frames" >> "$LOG_FILE"
  fi
  
  if [ "$DB_EXISTS" -gt 0 ]; then
    echo "  Found $DB_EXISTS frames already in database (skipping)"
    echo "  Skipping $DB_EXISTS frames already in database" >> "$LOG_FILE"
    DB_SKIPPED_FRAMES=$((DB_SKIPPED_FRAMES + DB_EXISTS))
  fi
  
  if [ "$DUPE_CHUNKS" -gt 0 ]; then
    echo "  Found $DUPE_CHUNKS frames with duplicate chunk content (skipping)"
    echo "  Skipping $DUPE_CHUNKS frames with duplicate chunk content" >> "$LOG_FILE"
    DUPE_CHUNKS_SKIPPED=$((DUPE_CHUNKS_SKIPPED + DUPE_CHUNKS))
  fi
  
  if [ "$TO_PROCESS" -eq 0 ]; then
    echo "  All frames already processed, in database, or have duplicate content, skipping directory"
    echo "  No frames to process in this directory, skipping" >> "$LOG_FILE"
    SKIPPED_FRAMES=$((SKIPPED_FRAMES + ALREADY_PROCESSED))
    continue
  fi
  
  echo "  Will process $TO_PROCESS frames"
  echo "  Will process $TO_PROCESS frames" >> "$LOG_FILE"
  
  # Create a temporary file with frames to process
  FRAME_LIST=$(mktemp)
  for FRAME in $FRAMES; do
    FRAME_BASENAME=$(basename "$FRAME")
    
    if [ "$FORCE" = true ] || (! frame_is_processed "$FRAME" && ! frame_in_database "$FRAME" && ! has_duplicate_chunks "$FRAME"); then
      echo "$FRAME" >> "$FRAME_LIST"
      echo "  Queued for processing: $FRAME_BASENAME" >> "$LOG_FILE"
    fi
  done
  
  # Construct the command
  if [ "$CHECK_DB" = true ]; then
    # If checking DB, don't use --local-only flag to ensure DB updates happen
    CMD="python main.py --input-file \"$FRAME_LIST\" --chunk-size $CHUNK_SIZE --chunk-overlap $CHUNK_OVERLAP --max-chunks $MAX_CHUNKS --sequential --local-storage-dir \"$STORAGE_DIR\""
  else
    # Otherwise use local-only flag
    CMD="python main.py --input-file \"$FRAME_LIST\" --chunk-size $CHUNK_SIZE --chunk-overlap $CHUNK_OVERLAP --max-chunks $MAX_CHUNKS --sequential --local-only --local-storage-dir \"$STORAGE_DIR\""
  fi
  
  # Add OCR flag if enabled
  if [ "$ENABLE_OCR" = true ]; then
    CMD="$CMD --include-ocr"
  fi
  
  if [ "$DRY_RUN" = true ]; then
    echo "  DRY RUN: $CMD"
    echo "  DRY RUN: $CMD" >> "$LOG_FILE"
    rm "$FRAME_LIST"
  else
    echo "  Running: $CMD"
    echo "  Running: $CMD" >> "$LOG_FILE"
    eval $CMD 2>&1 | tee -a "$LOG_FILE"
    CMD_EXIT=$?
    
    # Count successful and failed frames from the last run
    SUCCESS_COUNT=$(tail -n 4 "$STORAGE_DIR/processing_summary.txt" 2>/dev/null | grep "Successfully processed" | grep -o '[0-9]\+' | head -1 || echo "0")
    FAIL_COUNT=$(tail -n 4 "$STORAGE_DIR/processing_summary.txt" 2>/dev/null | grep "Failed" | grep -o '[0-9]\+' | head -1 || echo "0")
    
    # Log processed frames to CSV
    if [ "$CMD_EXIT" -eq 0 ] && [ "$SUCCESS_COUNT" -gt 0 ]; then
      # Current timestamp for all entries
      CURRENT_TIME=$(date -Iseconds)
      
      while read -r FRAME; do
        # Check if the frame was actually processed by looking for its JSON file
        FRAME_FILENAME=$(basename "$FRAME")
        JSON_PATH="$STORAGE_DIR/payloads/json/${FRAME_FILENAME%.jpg}.json"
        
        if [ -f "$JSON_PATH" ]; then
          # Frame was successfully processed
          # Determine OCR status
          FRAME_ID="${FRAME_FILENAME%.jpg}"
          OCR_STATUS="none"
          if ocr_is_done "$FRAME"; then
            OCR_STATUS="done"
          fi
          
          echo "\"$FRAME\",\"$CURRENT_TIME\",\"success\",\"$FRAME_ID\",\"0\",\"$OCR_STATUS\"" >> "$PROCESSED_FRAMES_CSV"
          echo "  Successfully processed: $FRAME_FILENAME" >> "$LOG_FILE"
          
          # Extract chunks and update CSVs
          extract_chunks "$JSON_PATH" "$FRAME" "$CURRENT_TIME"
        else
          # Frame was attempted but failed
          echo "\"$FRAME\",\"$CURRENT_TIME\",\"failed\",\"\",\"0\",\"none\"" >> "$PROCESSED_FRAMES_CSV"
          echo "  Failed to process: $FRAME_FILENAME" >> "$LOG_FILE"
        fi
      done < "$FRAME_LIST"
    fi
    
    rm "$FRAME_LIST"
    
    PROCESSED_FRAMES=$((PROCESSED_FRAMES + SUCCESS_COUNT))
    FAILED_FRAMES=$((FAILED_FRAMES + FAIL_COUNT))
    
    echo "  Processed $SUCCESS_COUNT frames, failed $FAIL_COUNT frames"
    echo "  Processed $SUCCESS_COUNT frames, failed $FAIL_COUNT frames" >> "$LOG_FILE"
    echo "  Running totals: $PROCESSED_FRAMES processed ($PROCESSED_CHUNKS chunks), $FAILED_FRAMES failed, $SKIPPED_FRAMES skipped locally, $DB_SKIPPED_FRAMES skipped (DB), $DUPE_CHUNKS_SKIPPED skipped (duplicate content)"
    echo "  Running totals: $PROCESSED_FRAMES processed ($PROCESSED_CHUNKS chunks), $FAILED_FRAMES failed, $SKIPPED_FRAMES skipped locally, $DB_SKIPPED_FRAMES skipped (DB), $DUPE_CHUNKS_SKIPPED skipped (duplicate content)" >> "$LOG_FILE"
    echo ""
    echo "" >> "$LOG_FILE"
  fi
done

# Add Airtable integration options
AIRTABLE_BASE_ID="${AIRTABLE_BASE_ID:-}"
AIRTABLE_TABLE_NAME="${AIRTABLE_TABLE_NAME:-}"
AIRTABLE_API_KEY="${AIRTABLE_API_KEY:-}"
UPDATE_AIRTABLE=false
USE_GEMINI=false
GEMINI_API_KEY="${GEMINI_API_KEY:-}"

# Check if OCR data should be processed and Airtable updated
if [ "$ENABLE_OCR" = true ] && [ -n "$AIRTABLE_BASE_ID" ] && [ -n "$AIRTABLE_TABLE_NAME" ] && [ -n "$AIRTABLE_API_KEY" ]; then
  UPDATE_AIRTABLE=true
  echo "OCR data will be processed and Airtable will be updated"
  echo "OCR data will be processed and Airtable will be updated" >> "$LOG_FILE"

  # Check if Gemini should be used
  if [ -n "$GEMINI_API_KEY" ]; then
    USE_GEMINI=true
    echo "Using Google Gemini API for enhanced OCR text analysis"
    echo "Using Google Gemini API for enhanced OCR text analysis" >> "$LOG_FILE"
  fi

  # Run OCR data processor
  OCR_PROCESSOR_CMD="python scripts/ocr_data_processor.py --input-dir \"$STORAGE_DIR/payloads/ocr\" --csv-file \"$PROCESSED_FRAMES_CSV\" --update-airtable --base-id \"$AIRTABLE_BASE_ID\" --table-name \"$AIRTABLE_TABLE_NAME\" --api-key \"$AIRTABLE_API_KEY\""
  
  # Add Gemini API if available
  if [ "$USE_GEMINI" = true ]; then
    OCR_PROCESSOR_CMD="$OCR_PROCESSOR_CMD --use-gemini --gemini-api-key \"$GEMINI_API_KEY\""
  fi
  
  echo "Running: $OCR_PROCESSOR_CMD"
  echo "Running: $OCR_PROCESSOR_CMD" >> "$LOG_FILE"
  
  # Execute the OCR data processor
  eval $OCR_PROCESSOR_CMD 2>&1 | tee -a "$LOG_FILE"
  
  # Record Airtable update in summary
  echo "OCR data processed and Airtable updated" >> "$SUMMARY_FILE"
  if [ "$USE_GEMINI" = true ]; then
    echo "Google Gemini API was used for enhanced text analysis" >> "$SUMMARY_FILE"
  fi
else
  echo "Skipping Airtable update (either OCR disabled or Airtable credentials not provided)"
  echo "Skipping Airtable update (either OCR disabled or Airtable credentials not provided)" >> "$LOG_FILE"
fi

# Final summary with timestamp
FINISH_TIMESTAMP=$(date -Iseconds)
echo "===== Processing complete at $FINISH_TIMESTAMP ====="
echo "===== Processing complete at $FINISH_TIMESTAMP =====" >> "$LOG_FILE"
echo "Started: $TIMESTAMP"
echo "Finished: $FINISH_TIMESTAMP"
echo "Processed $PROCESSED_FOLDERS directories"
echo "Successfully processed $PROCESSED_FRAMES frames ($PROCESSED_CHUNKS chunks)"
echo "OCR processed: $OCR_PROCESSED frames"
echo "OCR failed: $OCR_FAILED frames"
echo "Failed frames: $FAILED_FRAMES"
echo "Skipped frames (already processed locally): $SKIPPED_FRAMES"
echo "Skipped frames (already in database): $DB_SKIPPED_FRAMES"
echo "Skipped frames (duplicate chunk content): $DUPE_CHUNKS_SKIPPED"
echo "Total frames found: $TOTAL_FRAMES"

# Record the final summary
echo "===== Processing Summary - $(date -Iseconds) =====" > "$SUMMARY_FILE"
echo "Run started: $(date -d "$(echo $TIMESTAMP | tr '_' ' ' | sed 's/-/:/g')" -Iseconds)" >> "$SUMMARY_FILE"
echo "Run finished: $FINISH_TIMESTAMP" >> "$SUMMARY_FILE"
echo "Duration: $(date -u -d "$(date -d "$FINISH_TIMESTAMP" +%s) - $(date -d "$(echo $TIMESTAMP | tr '_' ' ' | sed 's/-/:/g')" +%s) seconds" +"%H:%M:%S")" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "Processed $PROCESSED_FOLDERS directories" >> "$SUMMARY_FILE"
echo "Successfully processed $PROCESSED_FRAMES frames" >> "$SUMMARY_FILE"
echo "Successfully processed $PROCESSED_CHUNKS chunks" >> "$SUMMARY_FILE"
echo "OCR processed: $OCR_PROCESSED frames" >> "$SUMMARY_FILE"
echo "OCR failed: $OCR_FAILED frames" >> "$SUMMARY_FILE"
echo "Failed frames: $FAILED_FRAMES" >> "$SUMMARY_FILE"
echo "Skipped frames (already processed locally): $SKIPPED_FRAMES" >> "$SUMMARY_FILE"
echo "Skipped frames (already in database): $DB_SKIPPED_FRAMES" >> "$SUMMARY_FILE"
echo "Skipped frames (duplicate chunk content): $DUPE_CHUNKS_SKIPPED" >> "$SUMMARY_FILE"
echo "Total frames found: $TOTAL_FRAMES" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "Processing options:" >> "$SUMMARY_FILE"
echo "- Chunk size: $CHUNK_SIZE" >> "$SUMMARY_FILE"
echo "- Chunk overlap: $CHUNK_OVERLAP" >> "$SUMMARY_FILE"
echo "- Max chunks per frame: $MAX_CHUNKS" >> "$SUMMARY_FILE"
echo "- Force reprocessing: $FORCE" >> "$SUMMARY_FILE"
echo "- Database checking: $CHECK_DB" >> "$SUMMARY_FILE"
echo "- Skip duplicate chunks: $SKIP_DUPE_CHUNKS" >> "$SUMMARY_FILE"
echo "- OCR enabled: $ENABLE_OCR" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "CSV Files:" >> "$SUMMARY_FILE"
echo "- Frames log: $PROCESSED_FRAMES_CSV ($(wc -l < "$PROCESSED_FRAMES_CSV") entries)" >> "$SUMMARY_FILE"
echo "- Chunks log: $FRAME_CHUNKS_CSV ($(wc -l < "$FRAME_CHUNKS_CSV") entries)" >> "$SUMMARY_FILE"
echo "- OCR text log: $OCR_TEXT_CSV ($(wc -l < "$OCR_TEXT_CSV") entries)" >> "$SUMMARY_FILE"

# Create a symlink to the latest summary
ln -sf "$SUMMARY_FILE" "$STORAGE_DIR/latest_summary.txt"

echo "Results saved in $STORAGE_DIR"
echo "Detailed log: $LOG_FILE"
echo "Summary: $SUMMARY_FILE" 