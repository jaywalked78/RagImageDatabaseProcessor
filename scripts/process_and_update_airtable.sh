#!/bin/bash
#
# Process OCR data and update Airtable
#
# This script:
# 1. Processes OCR data from text files using the Gemini API
# 2. Updates Airtable with the processed data
# 3. Includes proper rate limiting for the Airtable API
#
# Usage:
#   ./scripts/process_and_update_airtable.sh [options]

# Comprehensive script to process frames with OCR and update Airtable
# Usage: ./scripts/process_and_update_airtable.sh [OPTIONS]

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
fi

# Default values
STORAGE_DIR=${STORAGE_DIR:-"all_frame_embeddings"}
OCR_DIR=${OCR_DIR:-"ocr_results"}
BATCH_SIZE=${BATCH_SIZE:-10}
MAX_WORKERS=${MAX_WORKERS:-4}
DRY_RUN=0
USE_GEMINI=0
VERBOSE=0
FLAGGED_ONLY=0
FRAME_ID=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --storage-dir)
            STORAGE_DIR="$2"
            shift
            shift
            ;;
        --ocr-dir)
            OCR_DIR="$2"
            shift
            shift
            ;;
        --frame-id)
            FRAME_ID="$2"
            shift
            shift
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --use-gemini)
            USE_GEMINI=1
            shift
            ;;
        --batch-size)
            BATCH_SIZE="$2"
            shift
            shift
            ;;
        --max-workers)
            MAX_WORKERS="$2"
            shift
            shift
            ;;
        --flagged-only)
            FLAGGED_ONLY=1
            shift
            ;;
        --verbose)
            VERBOSE=1
            shift
            ;;
        --airtable-key)
            export AIRTABLE_API_KEY="$2"
            shift
            shift
            ;;
        --base-id)
            export AIRTABLE_BASE_ID="$2"
            shift
            shift
            ;;
        --table-name)
            export AIRTABLE_TABLE_NAME="$2"
            shift
            shift
            ;;
        --help)
            echo "Usage: ./scripts/process_and_update_airtable.sh [OPTIONS]"
            echo "Process frames with OCR and update Airtable with the results"
            echo ""
            echo "Options:"
            echo "  --storage-dir DIR     Set storage directory (default: all_frame_embeddings)"
            echo "  --ocr-dir DIR         Directory containing OCR data files"
            echo "  --frame-id ID         Process a specific frame ID"
            echo "  --dry-run             Run without updating Airtable or writing files"
            echo "  --use-gemini          Use Google Gemini API for enhanced text analysis"
            echo "  --batch-size N        Process N frames at a time (default: 10)"
            echo "  --max-workers N       Use N concurrent workers (default: 4)"
            echo "  --flagged-only        Only process frames with flagged content"
            echo "  --verbose             Show detailed logging"
            echo "  --airtable-key KEY    Set Airtable API key"
            echo "  --base-id BASE_ID     Set Airtable base ID"
            echo "  --table-name TABLE    Set Airtable table name"
            echo "  --help                Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Ensure required credentials are available for Airtable
if [ -z "$AIRTABLE_API_KEY" ] && [ $DRY_RUN -eq 0 ]; then
    echo "❌ Error: AIRTABLE_API_KEY is not set in .env or as an argument."
    echo "Either set it in .env or pass it with --airtable-key."
    echo "Run with --dry-run to skip credential checks."
    exit 1
fi

if [ -z "$AIRTABLE_BASE_ID" ] && [ $DRY_RUN -eq 0 ]; then
    echo "❌ Error: AIRTABLE_BASE_ID is not set in .env or as an argument."
    echo "Either set it in .env or pass it with --base-id."
    echo "Run with --dry-run to skip credential checks."
    exit 1
fi

if [ -z "$AIRTABLE_TABLE_NAME" ] && [ $DRY_RUN -eq 0 ]; then
    echo "❌ Error: AIRTABLE_TABLE_NAME is not set in .env or as an argument."
    echo "Either set it in .env or pass it with --table-name."
    echo "Run with --dry-run to skip credential checks."
    exit 1
fi

# Create directories if they don't exist
mkdir -p "$STORAGE_DIR/payloads/csv"
mkdir -p "$STORAGE_DIR/payloads/json"
mkdir -p "$STORAGE_DIR/payloads/chunks"
mkdir -p "$STORAGE_DIR/logs/master_logs"
mkdir -p "$STORAGE_DIR/payloads/ocr"

# Create the CSV file if it doesn't exist
if [ ! -f "$STORAGE_DIR/payloads/csv/processed_frames.csv" ]; then
    echo "frame_id,processed_time,frame_path,ocr_status,ocr_structured,ocr_data,topics,content_types,is_flagged,word_count,char_count,summary" > "$STORAGE_DIR/payloads/csv/processed_frames.csv"
fi

# Build the command
if [ $FLAGGED_ONLY -eq 1 ]; then
    # If flagged-only, run the OCR data processor
    CMD="python scripts/ocr_data_processor.py --input-dir $OCR_DIR --csv-file $STORAGE_DIR/payloads/csv/processed_frames.csv --batch-size $BATCH_SIZE"
    
    if [ $USE_GEMINI -eq 1 ]; then
        CMD="$CMD --use-gemini"
        # Check if we have the Gemini key
        if [ -n "$GEMINI_API_KEY" ]; then
            CMD="$CMD --gemini-api-key $GEMINI_API_KEY"
        elif [ -n "$GOOGLE_API_KEY" ]; then
            CMD="$CMD --gemini-api-key $GOOGLE_API_KEY"
        else
            echo "❌ Error: Gemini API key not found in .env file."
            exit 1
        fi
    fi
else
    # Otherwise, run the frame processing pipeline
    CMD="python3 scripts/process_frame_pipeline.py --storage-dir $STORAGE_DIR --batch-size $BATCH_SIZE "
    
    if [ -n "$FRAME_ID" ]; then
        CMD="$CMD --frame-id $FRAME_ID"
    fi
    
    if [ $DRY_RUN -eq 1 ]; then
        CMD="$CMD --dry-run"
    fi
    
    if [ $VERBOSE -eq 1 ]; then
        CMD="$CMD --verbose"
    fi
fi

# Execute the command
echo "Running frame processing pipeline:"
echo "$CMD"
echo ""
$CMD
PROCESS_EXIT=$?

if [ $PROCESS_EXIT -ne 0 ]; then
    echo "❌ Processing failed with exit code $PROCESS_EXIT"
    exit $PROCESS_EXIT
fi

# If dry run, exit here
if [ $DRY_RUN -eq 1 ]; then
    echo "✅ Dry run completed successfully"
    exit 0
fi

# Update Airtable if not in dry run mode
echo "Updating Airtable:"
if [ $FLAGGED_ONLY -eq 1 ]; then
    python scripts/update_airtable.py --storage-dir "$STORAGE_DIR" --flagged-only
else
    python scripts/update_airtable.py --storage-dir "$STORAGE_DIR"
fi
AIRTABLE_EXIT=$?

if [ $AIRTABLE_EXIT -ne 0 ]; then
    echo "❌ Airtable update failed with exit code $AIRTABLE_EXIT"
    exit $AIRTABLE_EXIT
fi

echo "✅ Processing and Airtable update completed successfully"
exit 0 