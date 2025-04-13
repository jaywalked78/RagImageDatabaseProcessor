#!/bin/bash

# Integrated Run Processor Script with Image Server
# This script runs both the image server and text chunker for the same folder

# Set up colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Get the folder name from the first argument
FOLDER_NAME=$1
TEST_MODE=$2

# Generate timestamp in Central Standard Time for unique filenames
# Format: YYYYMMDD_HHMMSS
CST_TIMESTAMP=$(TZ="America/Chicago" date +%Y%m%d_%H%M%S)
OUTPUT_FILENAME="${FOLDER_NAME}_${CST_TIMESTAMP}.json"

# Get the absolute path of the current directory (MinimalistRagIntake)
CHUNKER_DIR=$(pwd)
IMAGE_SERVER_DIR=$(realpath "$CHUNKER_DIR/../LightweightImageServer")
FRAME_BASE_DIR=$(grep "FRAME_BASE_DIR" "$CHUNKER_DIR/.env" | cut -d= -f2- | xargs)

# Default values if not found in .env
if [ -z "$FRAME_BASE_DIR" ]; then
    FRAME_BASE_DIR="/home/jason/Videos/screenRecordings"
fi

# Display help if no arguments provided
if [ -z "$FOLDER_NAME" ]; then
    echo -e "${BLUE}Usage:${NC}"
    echo -e "  ./run_processor_with_image_server.sh <folder_name> [test]"
    echo -e "  ./run_processor_with_image_server.sh <folder_name> <file_path>"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo -e "  ./run_processor_with_image_server.sh screen_recording_2025_02_25_at_8_05_47_pm      ${GREEN}# Process folder in production mode${NC}"
    echo -e "  ./run_processor_with_image_server.sh screen_recording_2025_02_25_at_8_05_47_pm test ${GREEN}# Process folder in test mode${NC}"
    echo -e "  ./run_processor_with_image_server.sh screen_recording_2025_02_25_at_8_05_47_pm path/to/file.json ${GREEN}# Process specific file${NC}"
    exit 1
fi

# Check if logs directory exists, create if not
mkdir -p logs
mkdir -p data

# Resolve full path to the folder
if [[ "$FOLDER_NAME" == /* ]]; then
    # Absolute path
    FULL_FOLDER_PATH="$FOLDER_NAME"
else
    # Relative path - check if it's relative to current directory or FRAME_BASE_DIR
    if [ -d "$FOLDER_NAME" ]; then
        FULL_FOLDER_PATH="$(realpath "$FOLDER_NAME")"
    else
        FULL_FOLDER_PATH="$FRAME_BASE_DIR/$FOLDER_NAME"
    fi
fi

echo -e "\n${BLUE}=== Starting Integrated Processing Pipeline ===${NC}"
echo -e "${BLUE}Folder name: ${GREEN}$FOLDER_NAME${NC}"
echo -e "${BLUE}Full path: ${GREEN}$FULL_FOLDER_PATH${NC}"
echo -e "${BLUE}Test mode: ${GREEN}${TEST_MODE:-false}${NC}"
echo -e "${BLUE}Image server directory: ${GREEN}$IMAGE_SERVER_DIR${NC}"
echo -e "${BLUE}Chunker directory: ${GREEN}$CHUNKER_DIR${NC}"
echo -e "${BLUE}Output filename: ${GREEN}$OUTPUT_FILENAME${NC}"

# PART 1: PROCESS IMAGES WITH LIGHTWEIGHTIMAGESERVER
# -----------------------------------------------------

# Function to check if the LightweightImageServer is running
check_image_server() {
    if curl -s http://localhost:7779 >/dev/null; then
        return 0  # Server is running
    else
        return 1  # Server is not running
    fi
}

# Start the image server if not already running
echo -e "\n${BLUE}=== Starting Image Server ===${NC}"
if check_image_server; then
    echo -e "${GREEN}Image server is already running${NC}"
else
    echo -e "${YELLOW}Image server not detected. Starting now...${NC}"
    
    # Start the persistent server
    pushd "$IMAGE_SERVER_DIR" > /dev/null
    # Run the server in the background to not block execution
    bash ./persistent_run.sh &
    
    # Wait for server to start (max 10 seconds)
    for i in {1..10}; do
        if check_image_server; then
            echo -e "${GREEN}Image server started successfully${NC}"
            break
        fi
        echo -e "${YELLOW}Waiting for image server to start (attempt $i/10)...${NC}"
        sleep 1
        
        if [ $i -eq 10 ]; then
            echo -e "${RED}Failed to start image server. Continuing without image URLs.${NC}"
        fi
    done
    popd > /dev/null
fi

# Run the image server loader to generate URLs
echo -e "\n${BLUE}=== Loading Images into Server ===${NC}"
pushd "$IMAGE_SERVER_DIR" > /dev/null
OUTPUT_DIR="$(realpath ./output/json)"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}Running image server loader...${NC}"
echo -e "${BLUE}Command: ${GREEN}./run_with_progress.sh --dir=\"$FULL_FOLDER_PATH\" --timeout=60 --name=\"$FOLDER_NAME\" --output=\"$OUTPUT_DIR\"${NC}"
./run_with_progress.sh --dir="$FULL_FOLDER_PATH" --timeout=60 --name="$FOLDER_NAME" --output="$OUTPUT_DIR"
IMAGE_SERVER_STATUS=$?

# If the image server generated a standard filename, rename it with timestamp
if [ -f "${OUTPUT_DIR}/${FOLDER_NAME}.json" ]; then
    echo -e "${BLUE}Renaming output file to include timestamp...${NC}"
    mv "${OUTPUT_DIR}/${FOLDER_NAME}.json" "${OUTPUT_DIR}/${OUTPUT_FILENAME}"
    echo -e "${GREEN}Output file renamed to: ${OUTPUT_DIR}/${OUTPUT_FILENAME}${NC}"
    
    # Create a symlink to the latest version
    LATEST_LINK="${OUTPUT_DIR}/${FOLDER_NAME}_latest.json"
    ln -sf "${OUTPUT_DIR}/${OUTPUT_FILENAME}" "$LATEST_LINK"
    echo -e "${BLUE}Created symlink to latest version at: ${LATEST_LINK}${NC}"
fi

popd > /dev/null

if [ $IMAGE_SERVER_STATUS -ne 0 ]; then
    echo -e "${RED}Error loading images into server. Continuing without image URLs.${NC}"
else
    if [ -f "${OUTPUT_DIR}/${OUTPUT_FILENAME}" ]; then
        echo -e "${GREEN}Successfully loaded images into server and generated URL JSON at: ${OUTPUT_DIR}/${OUTPUT_FILENAME}${NC}"
        echo -e "${BLUE}Image URLs are now available for n8n to process${NC}"
    else
        echo -e "${RED}Output file not found at expected location: ${OUTPUT_DIR}/${OUTPUT_FILENAME}${NC}"
    fi
fi

# PART 2: PROCESS TEXT WITH MINIMALISTRAGINGTAKE
# -----------------------------------------------------

# Run the chunking processor
echo -e "\n${BLUE}=== Running Text Chunking Processor ===${NC}"

# Check if second argument is "test" or a file path
if [ "$TEST_MODE" == "test" ]; then
    echo -e "${BLUE}Running chunker in TEST mode for folder: ${GREEN}$FOLDER_NAME${NC}"
    echo -e "${BLUE}Command: ${GREEN}python \"$CHUNKER_DIR/process_json_files_v5.py\" --folder \"$FOLDER_NAME\" --test --image-urls \"${OUTPUT_DIR}/${OUTPUT_FILENAME}\"${NC}"
    python "$CHUNKER_DIR/process_json_files_v5.py" --folder "$FOLDER_NAME" --test --image-urls "${OUTPUT_DIR}/${OUTPUT_FILENAME}"
elif [ -n "$TEST_MODE" ] && [ "$TEST_MODE" != "test" ]; then
    echo -e "${BLUE}Chunker processing specific file: ${GREEN}$TEST_MODE${NC}"
    echo -e "${BLUE}Command: ${GREEN}python \"$CHUNKER_DIR/process_json_files_v5.py\" --folder \"$FOLDER_NAME\" --file \"$TEST_MODE\" --image-urls \"${OUTPUT_DIR}/${OUTPUT_FILENAME}\"${NC}"
    python "$CHUNKER_DIR/process_json_files_v5.py" --folder "$FOLDER_NAME" --file "$TEST_MODE" --image-urls "${OUTPUT_DIR}/${OUTPUT_FILENAME}"
else
    echo -e "${BLUE}Running chunker in PRODUCTION mode for folder: ${GREEN}$FOLDER_NAME${NC}"
    echo -e "${BLUE}Command: ${GREEN}python \"$CHUNKER_DIR/process_json_files_v5.py\" --folder \"$FOLDER_NAME\" --image-urls \"${OUTPUT_DIR}/${OUTPUT_FILENAME}\"${NC}"
    python "$CHUNKER_DIR/process_json_files_v5.py" --folder "$FOLDER_NAME" --image-urls "${OUTPUT_DIR}/${OUTPUT_FILENAME}"
fi

PROCESSOR_STATUS=$?

# Check processing status
if [ $PROCESSOR_STATUS -ne 0 ]; then
    echo -e "${RED}Error during text processing. Check logs for details.${NC}"
    exit 1
else
    echo -e "${GREEN}Text chunking completed successfully${NC}"
fi

echo -e "\n${BLUE}=== Processing Complete ===${NC}"
echo -e "${GREEN}Text and image processing for '${FOLDER_NAME}' completed${NC}"
echo -e "${BLUE}Image URLs JSON: ${GREEN}${OUTPUT_DIR}/${OUTPUT_FILENAME}${NC}"
echo -e "${YELLOW}Note: n8n should be configured to use both data sources:${NC}"
echo -e "  ${YELLOW}1. Text chunks from the webhook response${NC}"
echo -e "  ${YELLOW}2. Image URLs from ${OUTPUT_DIR}/${OUTPUT_FILENAME}${NC}" 