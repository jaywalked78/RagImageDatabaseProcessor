#!/bin/bash

# Simple script to collect and process all frames
# This uses the same approach that was working for the 10 test frames

set -e

# Hardcoded paths to avoid any environment variable issues
BASE_DIR="/home/jason/Videos/screenRecordings"
TEMP_DIR="/tmp/database_tokenizer"
LOG_DIR="/home/jason/Documents/DatabaseAdvancedTokenizer/logs"
WORKER_ID=1

# Create directories
mkdir -p "$TEMP_DIR"
mkdir -p "$LOG_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting simple frame collection process"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Base directory: $BASE_DIR"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Temp directory: $TEMP_DIR"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Log directory: $LOG_DIR"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ALL_FRAMES_FILE="$TEMP_DIR/all_frames_$TIMESTAMP.txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Collecting all frames..."
find "$BASE_DIR" -type f -name "*.jpg" | sort > "$ALL_FRAMES_FILE"

# Count total frames
TOTAL_FRAMES=$(wc -l < "$ALL_FRAMES_FILE")
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Found $TOTAL_FRAMES frames in total"

# Check if we found any frames
if [ "$TOTAL_FRAMES" -eq 0 ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Error: No frames found!"
  exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting processing with run_with_logs.sh"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Frame list: $ALL_FRAMES_FILE"

# Run the worker using the script that was working
./run_with_logs.sh "$WORKER_ID" "$ALL_FRAMES_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Processing completed" 