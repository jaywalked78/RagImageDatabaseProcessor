#!/bin/bash

# run_parallel_segments.sh
# Script to process folders in parallel using multiple workers
# Each worker processes a different segment of folders

set -e

# Hardcoded paths to avoid environment variable issues
BASE_DIR="/home/jason/Videos/screenRecordings"
MASTER_LIST="./AllFolders.txt"
TEMP_DIR="/tmp/database_tokenizer"
LOG_DIR="/home/jason/Documents/DatabaseAdvancedTokenizer/logs"

# Create directories if they don't exist
mkdir -p "$TEMP_DIR"
mkdir -p "$LOG_DIR"

# Add timestamp to log outputs
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "Starting parallel processing setup"
log "Base directory: $BASE_DIR"
log "Temp directory: $TEMP_DIR"
log "Log directory: $LOG_DIR"

# Update the master folder list
log "Creating/updating master folder list"
find "$BASE_DIR" -type d -name "screen_recording_*" | sort > "$MASTER_LIST.new"

# If the file exists, check for new folders
if [ -f "$MASTER_LIST" ]; then
  # Find new folders
  NEW_FOLDERS=$(comm -13 "$MASTER_LIST" "$MASTER_LIST.new")
  if [ -n "$NEW_FOLDERS" ]; then
    log "Found new folders:"
    echo "$NEW_FOLDERS"
    # Append new folders to the existing list and sort again
    cat "$MASTER_LIST" "$MASTER_LIST.new" | sort | uniq > "$MASTER_LIST.tmp"
    mv "$MASTER_LIST.tmp" "$MASTER_LIST"
  else
    log "No new folders found"
    mv "$MASTER_LIST.new" "$MASTER_LIST"
  fi
else
  # First time, just use the new list
  mv "$MASTER_LIST.new" "$MASTER_LIST"
  log "Created initial master folder list"
fi

# Count total folders
TOTAL_FOLDERS=$(wc -l < "$MASTER_LIST")
log "Total folders: $TOTAL_FOLDERS"

# Divide the folders into three segments
SEGMENT_SIZE=$(( (TOTAL_FOLDERS + 2) / 3 ))  # Round up
log "Each segment will process ~$SEGMENT_SIZE folders"

# Create segment folder lists in the temp directory
SEGMENT1_FILE="$TEMP_DIR/segment1_folders.txt"
SEGMENT2_FILE="$TEMP_DIR/segment2_folders.txt"
SEGMENT3_FILE="$TEMP_DIR/segment3_folders.txt"
SEGMENT3_REVERSED_FILE="$TEMP_DIR/segment3_folders_reversed.txt"

head -n "$SEGMENT_SIZE" "$MASTER_LIST" > "$SEGMENT1_FILE"
SEGMENT1_COUNT=$(wc -l < "$SEGMENT1_FILE")
log "Segment 1 (A → Z): $SEGMENT1_COUNT folders"

sed -n "$((SEGMENT_SIZE+1)),$((SEGMENT_SIZE*2))p" "$MASTER_LIST" > "$SEGMENT2_FILE"
SEGMENT2_COUNT=$(wc -l < "$SEGMENT2_FILE")
log "Segment 2 (middle): $SEGMENT2_COUNT folders"

tail -n "+$((SEGMENT_SIZE*2+1))" "$MASTER_LIST" > "$SEGMENT3_FILE"
SEGMENT3_COUNT=$(wc -l < "$SEGMENT3_FILE")
log "Segment 3 (Z → A): $SEGMENT3_COUNT folders"

# Use bash to process in reverse for the third segment
tac "$SEGMENT3_FILE" > "$SEGMENT3_REVERSED_FILE"
log "Created reversed segment 3 file"

# Create the worker script if it doesn't exist
WORKER_SCRIPT="./run_segment_worker.sh"
if [ ! -f "$WORKER_SCRIPT" ]; then
  log "Creating worker script: $WORKER_SCRIPT"
  cat > "$WORKER_SCRIPT" << 'EOF'
#!/bin/bash
# run_segment_worker.sh - Process a segment of folders

WORKER_ID=$1
SEGMENT_FILE=$2
TEMP_DIR="/tmp/database_tokenizer/worker_${WORKER_ID}"
LOG_DIR="/home/jason/Documents/DatabaseAdvancedTokenizer/logs"
LOG_FILE="${LOG_DIR}/worker_${WORKER_ID}_$(date +"%Y_%m_%d_%H_%M_%S").log"

# Create directories
mkdir -p "$TEMP_DIR"
mkdir -p "$LOG_DIR"

# Log setup
exec > >(tee -a "$LOG_FILE") 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Worker $WORKER_ID started"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Processing segment file: $SEGMENT_FILE"

# Process each folder in the segment
while read -r FOLDER; do
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Processing folder: $FOLDER"
  
  # Collect frames from this folder
  FRAMES_FILE="${TEMP_DIR}/frames_$(basename "$FOLDER").txt"
  find "$FOLDER" -type f -name "*.jpg" | sort > "$FRAMES_FILE"
  FRAME_COUNT=$(wc -l < "$FRAMES_FILE")
  
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Found $FRAME_COUNT frames in folder"
  
  # Use the existing worker to process these frames
  if [ "$FRAME_COUNT" -gt 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting processing for folder: $(basename "$FOLDER")"
    
    # Call the original script that works
    ./run_with_logs.sh "$WORKER_ID" "$FRAMES_FILE"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Completed processing for folder: $(basename "$FOLDER")"
  else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Skipping folder, no frames found"
  fi
done < "$SEGMENT_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Worker $WORKER_ID completed all folders in segment"
EOF
  chmod +x "$WORKER_SCRIPT"
fi

# Check for existing worker processes and prompt to kill them
log "Checking for existing worker processes..."
EXISTING_PIDS=$(ps aux | grep "run_segment_worker.sh" | grep -v grep | awk '{print $2}')

if [ -n "$EXISTING_PIDS" ]; then
  log "Found existing worker processes:"
  ps -p $EXISTING_PIDS -o pid,cmd,%cpu,%mem,etime
  
  read -p "Kill existing worker(s) before starting new ones? (y/n): " kill_existing
  
  if [[ "$kill_existing" =~ ^[Yy] ]]; then
    log "Killing existing worker processes..."
    for pid in $EXISTING_PIDS; do
      kill -15 "$pid" 2>/dev/null || true
      log "Sent SIGTERM to PID: $pid"
    done
    
    # Wait a moment to ensure processes exit
    sleep 2
    
    # Check if any processes are still running and force kill if needed
    for pid in $EXISTING_PIDS; do
      if ps -p "$pid" >/dev/null 2>&1; then
        log "Process $pid still running, sending SIGKILL..."
        kill -9 "$pid" 2>/dev/null || true
      fi
    done
  else
    log "Continuing with existing worker(s) still running."
  fi
fi

# Define cleanup function for handling interrupts
cleanup() {
  echo ""
  log "Interrupt received, terminating worker processes..."
  kill -15 $PID1 $PID2 $PID3 2>/dev/null || true
  sleep 1
  # Force kill if still running
  for pid in $PID1 $PID2 $PID3; do
    if ps -p $pid >/dev/null 2>&1; then
      log "Worker still running, sending SIGKILL to PID: $pid"
      kill -9 $pid 2>/dev/null || true
    fi
  done
  log "Workers terminated. Exiting."
  exit 0
}

# Set trap for SIGINT (Ctrl+C)
trap cleanup SIGINT SIGTERM

# Start worker processes
log "Starting worker 1 (A → Z segment)"
"$WORKER_SCRIPT" 1 "$SEGMENT1_FILE" &
PID1=$!
log "Worker 1 started with PID: $PID1"

log "Starting worker 2 (middle segment)"
"$WORKER_SCRIPT" 2 "$SEGMENT2_FILE" &
PID2=$!
log "Worker 2 started with PID: $PID2"

log "Starting worker 3 (Z → A segment)"
"$WORKER_SCRIPT" 3 "$SEGMENT3_REVERSED_FILE" &
PID3=$!
log "Worker 3 started with PID: $PID3"

log "All workers started. PIDs: $PID1, $PID2, $PID3"
log "Use 'ps -p $PID1,$PID2,$PID3' to check status"
log "Check logs in $LOG_DIR for detailed progress"

# Wait for all workers to complete
wait $PID1 $PID2 $PID3 2>/dev/null || true

log "All workers have finished" 