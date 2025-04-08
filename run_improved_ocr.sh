#!/bin/bash
# Run improved OCR pipeline
# This script runs the improved OCR pipeline that:
# 1. Processes frames folder by folder
# 2. Skips frames that already have OCRData
# 3. Processes all frames in a folder before moving to the next
# 4. Handles rate limiting to avoid API issues

set -e

# Load environment variables
source .env

# Log function
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Check for required commands
check_dependencies() {
  log "Checking dependencies..."
  
  if ! command -v node &> /dev/null; then
    log "ERROR: Node.js is required but not installed."
    exit 1
  fi
  
  if ! command -v python &> /dev/null; then
    log "ERROR: Python is required but not installed."
    exit 1
  fi
  
  # Check for required Node.js packages
  if [ ! -d "node_modules/airtable" ]; then
    log "Installing required npm packages..."
    npm install airtable dotenv
  fi
  
  log "All dependencies are installed."
}

# Display usage information
usage() {
  echo "Usage: $0 [OPTIONS]"
  echo "Options:"
  echo "  --folder=PATH     Process a specific folder only"
  echo "  --help            Display this usage information"
  echo ""
  echo "Example:"
  echo "  $0                Process all folders chronologically"
  echo "  $0 --folder=/home/jason/Videos/screenRecordings/screen_recording_2025_04_02_at_6_07_21_pm"
}

# Parse command line arguments
FOLDER=""

for arg in "$@"; do
  case $arg in
    --folder=*)
      FOLDER="${arg#*=}"
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      log "Unknown option: $arg"
      usage
      exit 1
      ;;
  esac
done

# Main execution
main() {
  log "Starting improved OCR pipeline..."
  
  # Check dependencies
  check_dependencies
  
  # Create logs directory if it doesn't exist
  mkdir -p logs
  
  # Run the improved OCR pipeline
  if [ -n "$FOLDER" ]; then
    log "Processing specific folder: $FOLDER"
    node improved_ocr_pipeline.js --folder="$FOLDER" 2>&1 | tee logs/improved_ocr_$(date +%Y%m%d_%H%M%S).log
  else
    log "Processing all folders chronologically"
    node improved_ocr_pipeline.js 2>&1 | tee logs/improved_ocr_$(date +%Y%m%d_%H%M%S).log
  fi
  
  if [ $? -eq 0 ]; then
    log "OCR pipeline completed successfully!"
  else
    log "ERROR: OCR pipeline failed."
    exit 1
  fi
}

# Run the main function
main 