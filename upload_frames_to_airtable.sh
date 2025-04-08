#!/bin/bash
#
# upload_frames_to_airtable.sh
#
# Script to upload all frame images to Airtable
# This makes OCR processing and other tasks easier by having
# the images directly accessible in Airtable

# Handle interruptions gracefully
function cleanup {
    echo -e "\n\nProcess interrupted. Cleaning up..."
    # Add a few newlines to clear any partial output
    echo -e "\n\n"
    exit 1
}

# Set up trap for SIGINT (Ctrl+C)
trap cleanup SIGINT

# Ensure the Python virtual environment is activated
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Activated virtual environment"
fi

# Ensure log directories exist
mkdir -p logs/airtable

# Log file
timestamp=$(date +%Y%m%d_%H%M%S)
LOG_FILE="logs/airtable/upload_process_$timestamp.log"

echo "Starting frame image upload process at $(date)" | tee -a "$LOG_FILE"
echo "This will upload all frame images to their matching Airtable records" | tee -a "$LOG_FILE"
echo "Note: Using pagination to retrieve ALL records (not just the default 100 limit)" | tee -a "$LOG_FILE"
echo "------------------------------------------------------" | tee -a "$LOG_FILE"

# Check environment variables
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Please create one with your API keys." | tee -a "$LOG_FILE"
    exit 1
fi

# Load environment variables from .env file more safely
# without executing any commands that might be in the .env file
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip comments and empty lines
    [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
    
    # Extract key and value
    key=$(echo "$line" | cut -d= -f1)
    value=$(echo "$line" | cut -d= -f2-)
    
    # Export the variable
    export "$key"="$value"
done < .env

# Check required variables
if [ -z "$AIRTABLE_PERSONAL_ACCESS_TOKEN" ]; then
    echo "ERROR: AIRTABLE_PERSONAL_ACCESS_TOKEN is not set in .env file." | tee -a "$LOG_FILE"
    exit 1
fi

if [ -z "$AIRTABLE_BASE_ID" ]; then
    echo "ERROR: AIRTABLE_BASE_ID is not set in .env file." | tee -a "$LOG_FILE"
    exit 1
fi

echo "Environment setup completed successfully." | tee -a "$LOG_FILE"

# Run in dry-run mode first to check what would be uploaded
echo "Performing dry run to check what would be uploaded..." | tee -a "$LOG_FILE"
python attach_frames_to_airtable.py --dry-run "$@" 2>&1 | tee -a "$LOG_FILE"

# Ask for confirmation before proceeding
read -p "Proceed with uploading frames to Airtable? (y/n): " confirm
if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo "Frame upload canceled." | tee -a "$LOG_FILE"
    exit 0
fi

# Clear the screen before starting to ensure clean output
clear

# Run the frame uploader
echo "Starting frame upload process..." | tee -a "$LOG_FILE"
echo "This may take some time. Using minimal progress display to avoid cluttering the terminal." | tee -a "$LOG_FILE"
echo "Now handling ALL records with pagination (no 100 record limit)" | tee -a "$LOG_FILE"
echo "For detailed logs, check: $LOG_FILE" | tee -a "$LOG_FILE"
echo "------------------------------------------------------" | tee -a "$LOG_FILE"

# Run with output directly to terminal to avoid capturing binary data in tee
python attach_frames_to_airtable.py "$@" 2>> "$LOG_FILE"

exit_code=$?

echo "------------------------------------------------------" | tee -a "$LOG_FILE"
echo "Frame upload process completed at $(date)" | tee -a "$LOG_FILE"
echo "Exit code: $exit_code" | tee -a "$LOG_FILE"

# Show success/failure message
if [ $exit_code -eq 0 ]; then
    echo "Frame upload completed successfully!"
    echo "You can now run OCR processing using:"
    echo "  ./run_ocr_from_airtable.sh"
else
    echo "Frame upload completed with errors. Check the log file: $LOG_FILE"
fi

exit $exit_code 