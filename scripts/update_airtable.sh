#!/bin/bash
# Helper script to process OCR data and update Airtable
# Usage: ./scripts/update_airtable.sh [--storage-dir DIR] [--use-gemini]

# Default values
STORAGE_DIR="all_frame_embeddings"
USE_GEMINI=false

# Process command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --storage-dir)
      STORAGE_DIR="$2"
      shift 2
      ;;
    --use-gemini)
      USE_GEMINI=true
      shift
      ;;
    --help)
      echo "Usage: ./scripts/update_airtable.sh [--storage-dir DIR] [--use-gemini]"
      echo ""
      echo "Updates Airtable with processed OCR data"
      echo ""
      echo "Options:"
      echo "  --storage-dir DIR  : Directory containing OCR data (default: all_frame_embeddings)"
      echo "  --use-gemini       : Use Google Gemini API for enhanced text analysis"
      echo "  --help             : Display this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Load environment variables
if [ -f "scripts/load_env.sh" ]; then
  source scripts/load_env.sh
else
  echo "Error: scripts/load_env.sh not found"
  exit 1
fi

# Check if Airtable credentials are available
if [ -z "$AIRTABLE_BASE_ID" ] || [ -z "$AIRTABLE_TABLE_NAME" ] || [ -z "$AIRTABLE_API_KEY" ]; then
  echo "Error: Airtable credentials not found"
  echo "Please set AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, and AIRTABLE_API_KEY in .env.airtable"
  exit 1
fi

# Check if OCR directory exists
OCR_DIR="$STORAGE_DIR/payloads/ocr"
if [ ! -d "$OCR_DIR" ]; then
  echo "Error: OCR directory not found: $OCR_DIR"
  exit 1
fi

# Check if processed frames CSV exists
CSV_FILE="$STORAGE_DIR/payloads/csv/processed_frames.csv"
if [ ! -f "$CSV_FILE" ]; then
  echo "Error: Processed frames CSV not found: $CSV_FILE"
  exit 1
fi

# Construct the command
OCR_PROCESSOR_CMD="python scripts/ocr_data_processor.py --input-dir \"$OCR_DIR\" --csv-file \"$CSV_FILE\" --update-airtable --base-id \"$AIRTABLE_BASE_ID\" --table-name \"$AIRTABLE_TABLE_NAME\" --api-key \"$AIRTABLE_API_KEY\""

# Add Gemini API if requested
if [ "$USE_GEMINI" = true ]; then
  if [ -z "$GEMINI_API_KEY" ]; then
    echo "Error: Gemini API key not found"
    echo "Please set GEMINI_API_KEY in .env.airtable"
    exit 1
  fi
  
  OCR_PROCESSOR_CMD="$OCR_PROCESSOR_CMD --use-gemini --gemini-api-key \"$GEMINI_API_KEY\""
fi

# Run the OCR data processor
echo "Processing OCR data and updating Airtable..."
echo "Storage directory: $STORAGE_DIR"
echo "OCR directory: $OCR_DIR"
echo "Using Gemini API: $USE_GEMINI"
echo ""
echo "Running: $OCR_PROCESSOR_CMD"
echo ""

eval $OCR_PROCESSOR_CMD 