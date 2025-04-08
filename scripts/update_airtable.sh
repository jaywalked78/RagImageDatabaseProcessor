#!/bin/bash
# Helper script to process OCR data and update Airtable
# Usage: ./scripts/update_airtable.sh [--storage-dir DIR] [--use-gemini] [--airtable-key KEY] [--base-id BASE_ID] [--table-name TABLE] [--dry-run] [--flagged-only]

# Parse command line arguments
STORAGE_DIR="all_frame_embeddings"
USE_GEMINI=false
AIRTABLE_KEY=""
BASE_ID=""
TABLE_NAME=""
DRY_RUN=false
FLAGGED_ONLY=false

while [ "$#" -gt 0 ]; do
  case "$1" in
    --storage-dir)
      STORAGE_DIR="$2"
      shift 2
      ;;
    --use-gemini)
      USE_GEMINI=true
      shift
      ;;
    --airtable-key)
      AIRTABLE_KEY="$2"
      shift 2
      ;;
    --base-id)
      BASE_ID="$2"
      shift 2
      ;;
    --table-name)
      TABLE_NAME="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --flagged-only)
      FLAGGED_ONLY=true
      shift
      ;;
    --help)
      echo "Usage: ./scripts/update_airtable.sh [OPTIONS]"
      echo "Options:"
      echo "  --storage-dir DIR    Set storage directory (default: all_frame_embeddings)"
      echo "  --use-gemini         Use Google Gemini API for enhanced text analysis"
      echo "  --airtable-key KEY   Set Airtable API key"
      echo "  --base-id BASE_ID    Set Airtable base ID"
      echo "  --table-name TABLE   Set Airtable table name"
      echo "  --dry-run            Run without updating Airtable"
      echo "  --flagged-only       Only process frames with flagged content"
      echo "  --help               Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Check if main .env file exists
if [ -f ".env" ]; then
  echo "Loading environment variables from .env"
  source .env
fi

# Check for required environment variables
if [ -z "$AIRTABLE_KEY" ]; then
  AIRTABLE_KEY="${AIRTABLE_API_KEY}"
fi

if [ -z "$BASE_ID" ]; then
  BASE_ID="${AIRTABLE_BASE_ID}"
fi

if [ -z "$TABLE_NAME" ]; then
  TABLE_NAME="${AIRTABLE_TABLE_NAME}"
fi

# Check for required credentials
if [ -z "$AIRTABLE_KEY" ]; then
  echo "Error: Airtable API key not provided"
  echo "Please set it with --airtable-key or in .env file as AIRTABLE_API_KEY"
  exit 1
fi

if [ -z "$BASE_ID" ]; then
  echo "Error: Airtable base ID not provided"
  echo "Please set it with --base-id or in .env file as AIRTABLE_BASE_ID"
  exit 1
fi

if [ -z "$TABLE_NAME" ]; then
  echo "Error: Airtable table name not provided"
  echo "Please set it with --table-name or in .env file as AIRTABLE_TABLE_NAME"
  exit 1
fi

# Check for storage directory
if [ ! -d "$STORAGE_DIR" ]; then
  echo "Warning: Storage directory '$STORAGE_DIR' does not exist, creating it"
  mkdir -p "$STORAGE_DIR/payloads/ocr"
  mkdir -p "$STORAGE_DIR/payloads/csv"
fi

# Check for OCR results directory
OCR_DIR="$STORAGE_DIR/payloads/ocr"
if [ ! -d "$OCR_DIR" ]; then
  echo "Warning: OCR directory '$OCR_DIR' does not exist, creating it"
  mkdir -p "$OCR_DIR"
fi

# Construct CSV path
CSV_FILE="$STORAGE_DIR/payloads/csv/processed_frames.csv"
if [ ! -f "$CSV_FILE" ]; then
  echo "Warning: CSV file '$CSV_FILE' does not exist, creating empty file"
  mkdir -p "$STORAGE_DIR/payloads/csv"
  echo "frame_id,processed_time,frame_path,ocr_status,ocr_structured,flagged,topics,content_types,word_count,char_count,summary,api_keys_detected,ocr_processed_at" > "$CSV_FILE"
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
  echo "Error: python3 not found"
  exit 1
fi

# Check for OCR data processor script
PROCESSOR_SCRIPT="scripts/ocr_data_processor.py"
if [ ! -f "$PROCESSOR_SCRIPT" ]; then
  echo "Error: OCR data processor script not found at '$PROCESSOR_SCRIPT'"
  exit 1
fi

# Construct Gemini flag if requested
GEMINI_FLAG=""
if [ "$USE_GEMINI" = true ]; then
  GEMINI_FLAG="--use-gemini"
  
  # Check for Gemini API key in environment
  if [ -z "$GEMINI_API_KEY" ] && [ -z "$GEMINI_API_KEY_1" ] && [ -z "$GOOGLE_API_KEY" ]; then
    echo "Warning: No Gemini API key found in environment variables"
    echo "Using --use-gemini flag requires one of these variables to be set:"
    echo "  GEMINI_API_KEY, GEMINI_API_KEY_1, or GOOGLE_API_KEY"
  fi
fi

# Construct dry run flag if requested
DRY_RUN_FLAG=""
if [ "$DRY_RUN" = true ]; then
  DRY_RUN_FLAG="--dry-run"
fi

# Construct flagged only flag if requested
FLAGGED_ONLY_FLAG=""
if [ "$FLAGGED_ONLY" = true ]; then
  FLAGGED_ONLY_FLAG="--flagged-only"
fi

# Construct and run the command
CMD="python3 $PROCESSOR_SCRIPT --input-dir $OCR_DIR --csv-file $CSV_FILE --update-airtable --api-key $AIRTABLE_KEY --base-id $BASE_ID --table-name $TABLE_NAME $GEMINI_FLAG $DRY_RUN_FLAG $FLAGGED_ONLY_FLAG"

echo "Running OCR data processor:"
echo "$CMD"
echo ""

# Execute the command
$CMD

# Check the exit status
STATUS=$?
if [ $STATUS -eq 0 ]; then
  echo "✅ OCR data processing completed successfully"
else
  echo "❌ OCR data processing failed with exit code $STATUS"
fi

exit $STATUS 