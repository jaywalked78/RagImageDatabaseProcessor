#!/bin/bash
#
# run_ocr_processor.sh
#
# Wrapper script to run the OCRProcessorAndUpsertToAirtable
# Sets up the environment and executes the processor

# Ensure the Python virtual environment is activated
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Activated virtual environment"
fi

# Ensure log and output directories exist
mkdir -p logs/ocr
mkdir -p output/reports
mkdir -p output/ocr_results

# Get environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env file"
    # Extract Gemini API keys and set as environment variables
    export GEMINI_API_KEY=$(grep GEMINI_API_KEY= .env | head -1 | cut -d '=' -f2)
    export GEMINI_API_KEY_1=$(grep GEMINI_API_KEY_1= .env | cut -d '=' -f2)
    export GEMINI_API_KEY_2=$(grep GEMINI_API_KEY_2= .env | cut -d '=' -f2)
    export GEMINI_API_KEY_3=$(grep GEMINI_API_KEY_3= .env | cut -d '=' -f2)
    export GEMINI_API_KEY_4=$(grep GEMINI_API_KEY_4= .env | cut -d '=' -f2)
    export GEMINI_API_KEY_5=$(grep GEMINI_API_KEY_5= .env | cut -d '=' -f2)
    export GEMINI_USE_KEY_ROTATION=$(grep GEMINI_USE_KEY_ROTATION= .env | cut -d '=' -f2)
    
    # Print API key status (first 4 characters only for security)
    if [ -n "$GEMINI_API_KEY_1" ]; then
        echo "Using Gemini API Keys (rotation mode): ${GEMINI_API_KEY_1:0:4}... and others"
    elif [ -n "$GEMINI_API_KEY" ]; then
        echo "Using Gemini API Key: ${GEMINI_API_KEY:0:4}..."
    else
        echo "Warning: No Gemini API keys found in .env file"
    fi
else
    echo "Warning: .env file not found - environment variables may be missing"
fi

# Log file
timestamp=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/ocr/ocr_processor_$timestamp.log"

echo "Starting OCRProcessorAndUpsertToAirtable at $(date)" | tee -a "$LOG_FILE"
echo "------------------------------------------------------" | tee -a "$LOG_FILE"

# Run the OCR processor
# Forward all command line arguments
python ocr_processor.py "$@" 2>&1 | tee -a "$LOG_FILE"

exit_code=${PIPESTATUS[0]}

echo "------------------------------------------------------" | tee -a "$LOG_FILE"
echo "Completed OCR processing at $(date)" | tee -a "$LOG_FILE"
echo "Exit code: $exit_code" | tee -a "$LOG_FILE"

# Show success/failure message
if [ $exit_code -eq 0 ]; then
    echo "OCR processing completed successfully!"
else
    echo "OCR processing completed with errors. Check the log file: $LOG_FILE"
fi

exit $exit_code 