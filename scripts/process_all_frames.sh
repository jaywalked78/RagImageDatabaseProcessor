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
#   --help               : Display this help message

# Default values
LIMIT=0
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_CHUNKS=10
STORAGE_DIR="all_frame_embeddings"
DRY_RUN=false
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
  
  # Set limit parameter if specified
  LIMIT_PARAM=""
  if [ "$LIMIT" -gt 0 ]; then
    LIMIT_PARAM="--limit $LIMIT"
    echo "Processing directory $DIR_NAME ($NUM_FILES frames, limited to $LIMIT)"
  else
    echo "Processing directory $DIR_NAME ($NUM_FILES frames)"
  fi
  
  # Construct the command
  CMD="python main.py --input \"$DIR\" --pattern \"*.jpg\" $LIMIT_PARAM --chunk-size $CHUNK_SIZE --chunk-overlap $CHUNK_OVERLAP --max-chunks $MAX_CHUNKS --sequential --local-only --local-storage-dir \"$STORAGE_DIR\""
  
  if [ "$DRY_RUN" = true ]; then
    echo "  DRY RUN: $CMD"
  else
    echo "  Running: $CMD"
    eval $CMD
    
    # Count successful and failed frames from the last run
    SUCCESS_COUNT=$(tail -n 4 "$STORAGE_DIR/processing_summary.txt" 2>/dev/null | grep "Successfully processed" | grep -o '[0-9]\+' | head -1 || echo "0")
    FAIL_COUNT=$(tail -n 4 "$STORAGE_DIR/processing_summary.txt" 2>/dev/null | grep "Failed" | grep -o '[0-9]\+' | head -1 || echo "0")
    
    PROCESSED_FRAMES=$((PROCESSED_FRAMES + SUCCESS_COUNT))
    FAILED_FRAMES=$((FAILED_FRAMES + FAIL_COUNT))
    
    echo "  Processed $SUCCESS_COUNT frames, failed $FAIL_COUNT frames"
    echo "  Running totals: $PROCESSED_FRAMES processed, $FAILED_FRAMES failed"
    echo ""
  fi
done

# Final summary
echo "===== Processing complete ====="
echo "Processed $PROCESSED_FOLDERS directories"
echo "Successfully processed $PROCESSED_FRAMES frames out of $TOTAL_FRAMES total"
echo "Failed frames: $FAILED_FRAMES"

# Record the final summary
echo "===== Processing Summary $(date) =====" > "$STORAGE_DIR/final_summary.txt"
echo "Processed $PROCESSED_FOLDERS directories" >> "$STORAGE_DIR/final_summary.txt"
echo "Successfully processed $PROCESSED_FRAMES frames out of $TOTAL_FRAMES total" >> "$STORAGE_DIR/final_summary.txt"
echo "Failed frames: $FAILED_FRAMES" >> "$STORAGE_DIR/final_summary.txt"

echo "Results saved in $STORAGE_DIR" 