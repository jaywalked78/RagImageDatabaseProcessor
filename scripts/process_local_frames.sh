#!/bin/bash
# Script to process frames from a local directory
# Usage: ./process_local_frames.sh [OPTIONS]

# Default values
FRAMES_DIR=${FRAME_BASE_DIR:-"/home/jason/Videos/screenRecordings"}
PATTERN="**/*.jpg"
DRIVE_FOLDER_ID=""
PARALLEL=5
MAX_CHUNKS=10
CHUNK_SIZE=500
CHUNK_OVERLAP=50
LIMIT=""
DB_PATH="frames_local.db"
ACTION="all"

# Help function
show_help() {
    echo "Usage: ./process_local_frames.sh [OPTIONS]"
    echo ""
    echo "This script processes locally stored frames, creates embeddings, and exports to PostgreSQL and/or webhooks."
    echo ""
    echo "Options:"
    echo "  --frames-dir DIR     Directory containing frames (default: $FRAMES_DIR)"
    echo "  --pattern PATTERN    Glob pattern to match frames (default: $PATTERN)"
    echo "  --drive-folder-id ID Google Drive folder ID for URL references"
    echo "  --parallel N         Number of frames to process in parallel (default: $PARALLEL)"
    echo "  --max-chunks N       Maximum number of chunks per frame (default: $MAX_CHUNKS)"
    echo "  --chunk-size N       Size of text chunks (default: $CHUNK_SIZE)"
    echo "  --chunk-overlap N    Overlap between chunks (default: $CHUNK_OVERLAP)"
    echo "  --limit N            Maximum number of frames to process"
    echo "  --db-path PATH       Path to database file (default: $DB_PATH)"
    echo "  --load-only          Only load frames, don't process or export"
    echo "  --process-only       Only process loaded frames, don't export"
    echo "  --export-only        Only export processed frames"
    echo "  --help               Show this help message"
    echo ""
    echo "Example:"
    echo "  ./process_local_frames.sh --drive-folder-id abc123 --parallel 10 --max-chunks 5"
    exit 0
}

# Process arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --frames-dir)
            FRAMES_DIR="$2"
            shift 2
            ;;
        --pattern)
            PATTERN="$2"
            shift 2
            ;;
        --drive-folder-id)
            DRIVE_FOLDER_ID="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL="$2"
            shift 2
            ;;
        --max-chunks)
            MAX_CHUNKS="$2"
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
        --limit)
            LIMIT="--limit $2"
            shift 2
            ;;
        --db-path)
            DB_PATH="$2"
            shift 2
            ;;
        --load-only)
            ACTION="load"
            shift
            ;;
        --process-only)
            ACTION="process"
            shift
            ;;
        --export-only)
            ACTION="export"
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

# Check if frames directory exists
if [ ! -d "$FRAMES_DIR" ]; then
    echo "Error: Frames directory '$FRAMES_DIR' not found."
    exit 1
fi

# Create a timestamp for this run
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="local_processing_${TIMESTAMP}.log"

echo "=== Frame Processing Started at $(date) ==="
echo "Frames Directory: $FRAMES_DIR"
echo "Pattern: $PATTERN"
echo "Google Drive Folder ID: ${DRIVE_FOLDER_ID:-"Not specified"}"
echo "Database: $DB_PATH"
echo "Log File: $LOG_FILE"
echo "Parallel: $PARALLEL"
echo "Max Chunks: $MAX_CHUNKS"
echo "Action: $ACTION"
echo "======================================"

# Build the drive folder argument if provided
DRIVE_ARG=""
if [ -n "$DRIVE_FOLDER_ID" ]; then
    DRIVE_ARG="--drive-folder-id $DRIVE_FOLDER_ID"
fi

# Build the command based on the action
case $ACTION in
    "load")
        CMD="--load"
        ;;
    "process")
        CMD="--process"
        ;;
    "export")
        CMD="--export --export-postgres --export-webhook"
        ;;
    "all")
        CMD="--all"
        ;;
esac

# Run the processor
python local_processor_local_frames.py \
    $CMD \
    --frames-dir "$FRAMES_DIR" \
    --pattern "$PATTERN" \
    $DRIVE_ARG \
    --db-path "$DB_PATH" \
    --parallel "$PARALLEL" \
    --max-chunks "$MAX_CHUNKS" \
    --chunk-size "$CHUNK_SIZE" \
    --chunk-overlap "$CHUNK_OVERLAP" \
    $LIMIT \
    | tee "$LOG_FILE"

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "=== Frame Processing Completed Successfully at $(date) ==="
else
    echo "=== Frame Processing Failed with exit code $EXIT_CODE at $(date) ==="
fi

echo "Database file: $DB_PATH"
echo "Log file: $LOG_FILE"
exit $EXIT_CODE 