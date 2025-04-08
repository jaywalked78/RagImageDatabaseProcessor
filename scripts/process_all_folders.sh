#!/bin/bash

# Script: process_all_folders.sh
# Description: Orchestrates the OCRProcessorAndUpsertToAirtable to process all folders chronologically.
# This script focuses only on OCR processing and Airtable updates, not embedding generation.

# Ensure log and output directories exist
mkdir -p logs/ocr
mkdir -p output/reports

# Log file
LOG_FILE="logs/ocr/batch_process_$(date +%Y%m%d_%H%M%S).log"
echo "Starting OCRProcessorAndUpsertToAirtable at $(date)" > $LOG_FILE
echo "------------------------------------------------------" >> $LOG_FILE

# Get all folders sorted chronologically
FOLDERS=$(ls -d /home/jason/Videos/screenRecordings/screen_recording_* | sort -t '_' -k3,3 -k4,4 -k5,5)

# Process each folder
count=0
for folder in $FOLDERS; do
  # Extract date from folder name
  folder_name=$(basename "$folder")
  date_part=$(echo $folder_name | cut -d '_' -f 3,4,5)
  
  echo "" >> $LOG_FILE
  echo "Processing folder: $folder_name ($count)" >> $LOG_FILE
  echo "Started at: $(date)" >> $LOG_FILE
  
  # Execute the OCR processor with a batch size of 10
  echo "Running OCRProcessorAndUpsertToAirtable" >> $LOG_FILE
  python ocr_processor.py \
    --base-dir "$folder" \
    --pattern "*.jpg" \
    --batch-size 10 \
    >> $LOG_FILE 2>&1
  
  # Get the exit code
  exit_code=$?
  
  echo "Completed at: $(date)" >> $LOG_FILE
  echo "Exit code: $exit_code" >> $LOG_FILE
  echo "------------------------------------------------------" >> $LOG_FILE
  
  # Increment counter
  count=$((count + 1))
  
  # Give the system a short break between folders
  sleep 5
done

echo "" >> $LOG_FILE
echo "Complete OCR processing at $(date)" >> $LOG_FILE
echo "Total folders processed: $count" >> $LOG_FILE 