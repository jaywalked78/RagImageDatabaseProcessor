#!/bin/bash
# Test OCR Processing Script - Single Folder Version
# Processes a small number of frames in a single folder

# Set up error handling
set -e

# Load environment variables
source .env

# Default parameters
FOLDER="/home/jason/Videos/screenRecordings/screen_recording_2025_04_07_at_7_36_21_am"
BATCH_SIZE=5
LIMIT=5

echo "$(date) - Starting test OCR processing on a single folder"
echo "$(date) - Folder: $FOLDER"
echo "$(date) - Batch size: $BATCH_SIZE"
echo "$(date) - Limit: $LIMIT"

# Run OCR on the folder
echo "$(date) - Running OCR on folder..."
python run_ocr_batch.py --folder "$FOLDER" --batch-size $BATCH_SIZE --limit $LIMIT

echo "$(date) - Processing complete!" 