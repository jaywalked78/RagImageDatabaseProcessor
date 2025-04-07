#!/bin/bash
# Script to process frames from a Google Drive folder
# Usage: ./process_drive_folder.sh FOLDER_ID [OPTIONS]

# Check if folder ID is provided
if [ -z "$1" ]; then
    echo "Error: Google Drive folder ID is required."
    echo "Usage: ./process_drive_folder.sh FOLDER_ID [OPTIONS]"
    exit 1
fi

FOLDER_ID=$1
shift  # Remove the first argument (folder ID)

# Default options
CREDENTIALS=${GOOGLE_CREDENTIALS_PATH:-"credentials.json"}
PARALLEL=5
MAX_CHUNKS=10
CHUNK_SIZE=500
CHUNK_OVERLAP=50
LIMIT=""
PATTERN=""
OUTPUT_DIR="frames_output"

# Process additional options
while [[ $# -gt 0 ]]; do
    case $1 in
        --credentials)
            CREDENTIALS="$2"
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
        --limit)
            LIMIT="--limit $2"
            shift 2
            ;;
        --pattern)
            PATTERN="--pattern $2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
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
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if credentials file exists
if [ ! -f "$CREDENTIALS" ]; then
    echo "Error: Credentials file '$CREDENTIALS' not found."
    echo "Set GOOGLE_CREDENTIALS_PATH environment variable or provide --credentials option."
    exit 1
fi

# Create a timestamp for this run
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_FILE="frames_${TIMESTAMP}.db"
LOG_FILE="processing_${TIMESTAMP}.log"

echo "=== Frame Processing Started at $(date) ==="
echo "Folder ID: $FOLDER_ID"
echo "Database: $DB_FILE"
echo "Log File: $LOG_FILE"
echo "Parallel: $PARALLEL"
echo "Max Chunks: $MAX_CHUNKS"
echo "Credentials: $CREDENTIALS"
echo "======================================"

# Run the processor with all options
python local_processor.py \
    --all \
    --drive-folder "$FOLDER_ID" \
    --credentials "$CREDENTIALS" \
    --db-path "$DB_FILE" \
    --output-dir "$OUTPUT_DIR" \
    --parallel "$PARALLEL" \
    --max-chunks "$MAX_CHUNKS" \
    --chunk-size "$CHUNK_SIZE" \
    --chunk-overlap "$CHUNK_OVERLAP" \
    --export-postgres \
    --export-webhook \
    $LIMIT \
    $PATTERN \
    | tee "$LOG_FILE"

EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "=== Frame Processing Completed Successfully at $(date) ==="
else
    echo "=== Frame Processing Failed with exit code $EXIT_CODE at $(date) ==="
fi

echo "Database file: $DB_FILE"
echo "Log file: $LOG_FILE"
exit $EXIT_CODE 