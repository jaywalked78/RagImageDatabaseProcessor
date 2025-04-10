#!/bin/bash

# Run Processor Script
# This script provides easy commands to run the JSON processor

# Set up colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the folder name from the first argument
FOLDER_NAME=$1
TEST_MODE=$2

# Display help if no arguments provided
if [ -z "$FOLDER_NAME" ]; then
    echo -e "${BLUE}Usage:${NC}"
    echo -e "  ./run_processor.sh <folder_name> [test]"
    echo -e "  ./run_processor.sh <folder_name> <file_path>"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo -e "  ./run_processor.sh screen_recording_2025_02_25_at_8_05_47_pm      ${GREEN}# Process folder in production mode${NC}"
    echo -e "  ./run_processor.sh screen_recording_2025_02_25_at_8_05_47_pm test ${GREEN}# Process folder in test mode${NC}"
    echo -e "  ./run_processor.sh screen_recording_2025_02_25_at_8_05_47_pm path/to/file.json ${GREEN}# Process specific file${NC}"
    exit 1
fi

# Check if logs directory exists, create if not
mkdir -p logs
mkdir -p data

# Check if second argument is "test" or a file path
if [ "$TEST_MODE" == "test" ]; then
    echo -e "${BLUE}Running in TEST mode for folder: ${GREEN}$FOLDER_NAME${NC}"
    python process_json_files_v4.py --folder "$FOLDER_NAME" --test
elif [ -n "$TEST_MODE" ]; then
    echo -e "${BLUE}Processing specific file: ${GREEN}$TEST_MODE${NC}"
    python process_json_files_v4.py --folder "$FOLDER_NAME" --file "$TEST_MODE"
else
    echo -e "${BLUE}Running in PRODUCTION mode for folder: ${GREEN}$FOLDER_NAME${NC}"
    python process_json_files_v4.py --folder "$FOLDER_NAME"
fi 