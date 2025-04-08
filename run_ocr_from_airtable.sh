#!/bin/bash
#
# run_ocr_from_airtable.sh
#
# Script to run OCR processing on frames directly from Airtable attachments
# This works after frames have been uploaded using upload_frames_to_airtable.sh

# Ensure the Python virtual environment is activated
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Activated virtual environment"
fi

# Ensure log directories exist
mkdir -p logs/ocr
mkdir -p output/ocr_results

# Log file
timestamp=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/ocr/ocr_airtable_$timestamp.log"

echo "Starting OCR processing from Airtable at $(date)" | tee -a "$LOG_FILE"
echo "This will process frames directly from their Airtable attachments" | tee -a "$LOG_FILE"
echo "------------------------------------------------------" | tee -a "$LOG_FILE"

# Check for .env file
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Please create one with your API keys." | tee -a "$LOG_FILE"
    exit 1
fi

# Load all environment variables from .env file
echo "Loading environment variables from .env file" | tee -a "$LOG_FILE"
export $(grep -v '^#' .env | xargs)

# Check required API keys
if [ -z "$AIRTABLE_PERSONAL_ACCESS_TOKEN" ]; then
    echo "ERROR: AIRTABLE_PERSONAL_ACCESS_TOKEN is not set in .env file." | tee -a "$LOG_FILE"
    exit 1
fi

if [ -z "$AIRTABLE_BASE_ID" ]; then
    echo "ERROR: AIRTABLE_BASE_ID is not set in .env file." | tee -a "$LOG_FILE"
    exit 1
fi

# Check for Gemini API keys
gemini_keys_found=0
if [ -n "$GEMINI_API_KEY" ]; then
    echo "Found main Gemini API key: ${GEMINI_API_KEY:0:4}..." | tee -a "$LOG_FILE"
    gemini_keys_found=$((gemini_keys_found + 1))
fi

for i in {1..5}; do
    key_var="GEMINI_API_KEY_$i"
    if [ -n "${!key_var}" ]; then
        echo "Found Gemini API key $i: ${!key_var:0:4}..." | tee -a "$LOG_FILE"
        gemini_keys_found=$((gemini_keys_found + 1))
    fi
done

if [ $gemini_keys_found -eq 0 ]; then
    echo "ERROR: No Gemini API keys found. Please add at least one GEMINI_API_KEY or GEMINI_API_KEY_1 to your .env file." | tee -a "$LOG_FILE"
    exit 1
fi

echo "Found $gemini_keys_found Gemini API key(s) - OCR processing will use key rotation" | tee -a "$LOG_FILE"

# Set key rotation flag
export GEMINI_USE_KEY_ROTATION="true"

echo "Environment setup completed successfully." | tee -a "$LOG_FILE"
echo "------------------------------------------------------" | tee -a "$LOG_FILE"

# Run in dry-run mode first to check what would be processed
echo "Performing dry run to check what would be processed..." | tee -a "$LOG_FILE"
python ocr_processor_airtable.py --dry-run "$@" 2>&1 | tee -a "$LOG_FILE"

# Ask for confirmation before proceeding
read -p "Proceed with OCR processing? (y/n): " confirm
if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo "OCR processing canceled." | tee -a "$LOG_FILE"
    exit 0
fi

# Run the OCR processor
echo "Starting OCR processing..." | tee -a "$LOG_FILE"
echo "This may take some time. Check logs for progress." | tee -a "$LOG_FILE"
python ocr_processor_airtable.py "$@" 2>&1 | tee -a "$LOG_FILE"

exit_code=${PIPESTATUS[0]}

echo "------------------------------------------------------" | tee -a "$LOG_FILE"
echo "OCR processing completed at $(date)" | tee -a "$LOG_FILE"
echo "Exit code: $exit_code" | tee -a "$LOG_FILE"

# Show success/failure message
if [ $exit_code -eq 0 ]; then
    echo "OCR processing completed successfully!"
    echo "Results are saved in output/ocr_results/"
else
    echo "OCR processing completed with errors. Check the log file: $LOG_FILE"
fi

exit $exit_code 