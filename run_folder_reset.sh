#!/bin/bash
# Script to reset Flagged fields by folder
# Processes records folder by folder for better performance

# Set up error handling
set -e
set -o pipefail

# Load environment variables
source .env

# Log function
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Help function
show_help() {
  echo "Usage: $0 [options] [folder_name]"
  echo ""
  echo "Options:"
  echo "  -a, --all              Process all folders (default)"
  echo "  -f, --folder NAME      Process specific folder NAME"
  echo "  -v, --value VALUE      Set flag value (default: false)"
  echo "  -s, --sensitive        Preserve sensitive flags (default: true)"
  echo "  -o, --overwrite-all    Overwrite all flags including sensitive ones"
  echo "  -h, --help             Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0                     Process all folders, set flag to false, preserve sensitive"
  echo "  $0 -f 'My Folder'      Process only 'My Folder'"
  echo "  $0 -v 'new_value'      Set flag to 'new_value' for all folders"
  echo "  $0 -o                  Process all flags, even sensitive ones"
  exit 1
}

# Check if Airtable environment variables are set
if [[ -z "$AIRTABLE_PERSONAL_ACCESS_TOKEN" || -z "$AIRTABLE_BASE_ID" || -z "$AIRTABLE_TABLE_NAME" ]]; then
  log "ERROR: Airtable environment variables not set. Please check your .env file."
  exit 1
fi

# Default configuration
FLAG_VALUE="false"  # Value to set the Flagged field to
SPECIFIC_FOLDER=""  # Optional specific folder name
PRESERVE_SENSITIVE=true  # Set to true to preserve records flagged as sensitive

# Parse command line options
while [[ $# -gt 0 ]]; do
  case "$1" in
    -a|--all)
      SPECIFIC_FOLDER=""
      shift
      ;;
    -f|--folder)
      SPECIFIC_FOLDER="$2"
      shift 2
      ;;
    -v|--value)
      FLAG_VALUE="$2"
      shift 2
      ;;
    -s|--sensitive)
      PRESERVE_SENSITIVE=true
      shift
      ;;
    -o|--overwrite-all)
      PRESERVE_SENSITIVE=false
      shift
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      # If no flag but there's an argument, assume it's a folder name
      if [[ -z "$SPECIFIC_FOLDER" ]]; then
        SPECIFIC_FOLDER="$1"
      else
        log "ERROR: Unknown option: $1"
        show_help
      fi
      shift
      ;;
  esac
done

# Start the process
log "Starting folder-based Flagged field reset"
log "Flag value: $FLAG_VALUE"

if [ -n "$SPECIFIC_FOLDER" ]; then
  log "Processing specific folder: $SPECIFIC_FOLDER"
else
  log "Processing all folders"
fi

if [ "$PRESERVE_SENSITIVE" = true ]; then
  log "Preserving records with 'true' in their flagged field"
  
  # Run the folder update script with "true" as a skip value
  node folder_update_flagged.js "$FLAG_VALUE" "$SPECIFIC_FOLDER" "true"
else
  log "Resetting ALL records (even sensitive ones)"
  
  # Run the folder update script without skip values
  node folder_update_flagged.js "$FLAG_VALUE" "$SPECIFIC_FOLDER"
fi

if [ $? -ne 0 ]; then
  log "ERROR: Failed to reset Flagged fields"
  exit 1
fi

log "Process completed successfully"
exit 0 