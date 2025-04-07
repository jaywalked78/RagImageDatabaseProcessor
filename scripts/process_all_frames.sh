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
#   --help               : Display this help message

# Default values
LIMIT=0
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_CHUNKS=10
STORAGE_DIR="all_frame_embeddings"
DRY_RUN=false
FORCE=false
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

# Create or access processed frames log
PROCESSED_LOG="$STORAGE_DIR/payloads/csv/processed_frames.csv"
if [ ! -f "$PROCESSED_LOG" ]; then
  echo "frame_path,processed_time,status" > "$PROCESSED_LOG"
  echo "Created new processed frames log at $PROCESSED_LOG"
fi

# Get the list of subdirectories in the base dir
SUBDIRS=$(find "$BASE_DIR" -type d | sort)

# Total count of frames
TOTAL_FRAMES=$(find "$BASE_DIR" -type f -name "*.jpg" | wc -l)
echo "Found $TOTAL_FRAMES total frames in $BASE_DIR and subdirectories"
echo "Will store results in $STORAGE_DIR"
echo ""

# Counter for processed folders and frames
PROCESSED_FOLDERS=0
PROCESSED_FRAMES=0
FAILED_FRAMES=0
SKIPPED_FRAMES=0

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
  if grep -q "\"$frame_path\"" "$PROCESSED_LOG"; then
    return 0  # Frame is processed (in CSV log)
  fi
  
  return 1  # Frame is not processed
}

# Loop through each subdirectory
for DIR in $SUBDIRS; do
  # Count JPG files in this directory
  NUM_FILES=$(find "$DIR" -maxdepth 1 -type f -name "*.jpg" | wc -l)
  
  if [ "$NUM_FILES" -eq 0 ]; then
    # Skip directories with no JPG files
    continue
  fi
  
  PROCESSED_FOLDERS=$((PROCESSED_FOLDERS + 1))
  
  # Directory name for display
  DIR_NAME=$(basename "$DIR")
  
  echo "Processing directory $DIR_NAME ($NUM_FILES frames)"
  
  # Get list of frames to process
  FRAMES=$(find "$DIR" -maxdepth 1 -type f -name "*.jpg" | sort)
  
  # Apply limit if specified
  if [ "$LIMIT" -gt 0 ]; then
    FRAMES=$(echo "$FRAMES" | head -n "$LIMIT")
    echo "  Limited to $LIMIT frames"
  fi
  
  # Count frames to process in this directory
  TO_PROCESS=0
  ALREADY_PROCESSED=0
  
  # Check which frames need processing
  for FRAME in $FRAMES; do
    if [ "$FORCE" = true ] || ! frame_is_processed "$FRAME"; then
      TO_PROCESS=$((TO_PROCESS + 1))
    else
      ALREADY_PROCESSED=$((ALREADY_PROCESSED + 1))
    fi
  done
  
  if [ "$ALREADY_PROCESSED" -gt 0 ]; then
    echo "  Found $ALREADY_PROCESSED already processed frames (skipping)"
  fi
  
  if [ "$TO_PROCESS" -eq 0 ]; then
    echo "  All frames already processed, skipping directory"
    SKIPPED_FRAMES=$((SKIPPED_FRAMES + ALREADY_PROCESSED))
    continue
  fi
  
  echo "  Will process $TO_PROCESS frames"
  
  # Create a temporary file with frames to process
  FRAME_LIST=$(mktemp)
  for FRAME in $FRAMES; do
    if [ "$FORCE" = true ] || ! frame_is_processed "$FRAME"; then
      echo "$FRAME" >> "$FRAME_LIST"
    fi
  done
  
  # Construct the command
  CMD="python main.py --input-file \"$FRAME_LIST\" --chunk-size $CHUNK_SIZE --chunk-overlap $CHUNK_OVERLAP --max-chunks $MAX_CHUNKS --sequential --local-only --local-storage-dir \"$STORAGE_DIR\""
  
  if [ "$DRY_RUN" = true ]; then
    echo "  DRY RUN: $CMD"
    rm "$FRAME_LIST"
  else
    echo "  Running: $CMD"
    eval $CMD
    CMD_EXIT=$?
    
    # Count successful and failed frames from the last run
    SUCCESS_COUNT=$(tail -n 4 "$STORAGE_DIR/processing_summary.txt" 2>/dev/null | grep "Successfully processed" | grep -o '[0-9]\+' | head -1 || echo "0")
    FAIL_COUNT=$(tail -n 4 "$STORAGE_DIR/processing_summary.txt" 2>/dev/null | grep "Failed" | grep -o '[0-9]\+' | head -1 || echo "0")
    
    # Log processed frames to CSV
    if [ "$CMD_EXIT" -eq 0 ] && [ "$SUCCESS_COUNT" -gt 0 ]; then
      while read -r FRAME; do
        # Check if the frame was actually processed by looking for its JSON file
        FRAME_FILENAME=$(basename "$FRAME")
        JSON_PATH="$STORAGE_DIR/payloads/json/${FRAME_FILENAME%.jpg}.json"
        
        if [ -f "$JSON_PATH" ]; then
          # Frame was successfully processed
          echo "\"$FRAME\",\"$(date -Iseconds)\",\"success\"" >> "$PROCESSED_LOG"
        else
          # Frame was attempted but failed
          echo "\"$FRAME\",\"$(date -Iseconds)\",\"failed\"" >> "$PROCESSED_LOG"
        fi
      done < "$FRAME_LIST"
    fi
    
    rm "$FRAME_LIST"
    
    PROCESSED_FRAMES=$((PROCESSED_FRAMES + SUCCESS_COUNT))
    FAILED_FRAMES=$((FAILED_FRAMES + FAIL_COUNT))
    
    echo "  Processed $SUCCESS_COUNT frames, failed $FAIL_COUNT frames"
    echo "  Running totals: $PROCESSED_FRAMES processed, $FAILED_FRAMES failed, $SKIPPED_FRAMES skipped"
    echo ""
  fi
done

# Final summary
echo "===== Processing complete ====="
echo "Processed $PROCESSED_FOLDERS directories"
echo "Successfully processed $PROCESSED_FRAMES frames"
echo "Failed frames: $FAILED_FRAMES"
echo "Skipped (already processed): $SKIPPED_FRAMES"
echo "Total frames found: $TOTAL_FRAMES"

# Record the final summary
echo "===== Processing Summary $(date) =====" > "$STORAGE_DIR/final_summary.txt"
echo "Processed $PROCESSED_FOLDERS directories" >> "$STORAGE_DIR/final_summary.txt"
echo "Successfully processed $PROCESSED_FRAMES frames" >> "$STORAGE_DIR/final_summary.txt"
echo "Failed frames: $FAILED_FRAMES" >> "$STORAGE_DIR/final_summary.txt"
echo "Skipped (already processed): $SKIPPED_FRAMES" >> "$STORAGE_DIR/final_summary.txt"
echo "Total frames found: $TOTAL_FRAMES" >> "$STORAGE_DIR/final_summary.txt"

echo "Results saved in $STORAGE_DIR" 