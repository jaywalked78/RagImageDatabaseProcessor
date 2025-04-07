#!/bin/bash

# Test script for batch and sequential processing integration
# This script will test:
# 1. Google Drive connection
# 2. Airtable connection
# 3. Sequential processing pipeline
# 4. Batch processing pipeline

# Text formatting
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BOLD}===== Processing Integration Tests =====${NC}"
echo "This script will test your integration with Google Drive and Airtable."
echo ""

# Step 1: Test Google Drive connection
echo -e "${YELLOW}Step 1: Testing Google Drive connection...${NC}"
if python test_google_drive.py; then
    echo -e "${GREEN}✓ Google Drive connection successful!${NC}"
    echo ""
else
    echo -e "${RED}✗ Google Drive connection failed.${NC}"
    echo -e "Please check if your ${BOLD}credentials/credentials.json${NC} file is valid and"
    echo -e "that the service account has access to your Google Drive files."
    echo ""
    echo "Would you like to continue with the other tests? [y/N]"
    read continue_tests
    if [[ ! "$continue_tests" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 2: Test Airtable connection
echo -e "${YELLOW}Step 2: Testing Airtable connection...${NC}"
if python test_airtable.py; then
    echo -e "${GREEN}✓ Airtable connection successful!${NC}"
    echo ""
else
    echo -e "${RED}✗ Airtable connection failed.${NC}"
    echo -e "Please check your ${BOLD}AIRTABLE_PERSONAL_ACCESS_TOKEN${NC} and ${BOLD}AIRTABLE_BASE_ID${NC} in the .env file."
    echo ""
    echo "Would you like to continue with the processing tests? [y/N]"
    read continue_tests
    if [[ ! "$continue_tests" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 3: Test sequential processing
echo -e "${YELLOW}Step 3: Testing sequential processing pipeline...${NC}"
if python run_sequential_process.py 3; then
    echo -e "${GREEN}✓ Sequential processing test successful!${NC}"
    echo ""
else
    echo -e "${RED}✗ Sequential processing test failed.${NC}"
    echo "Please check the logs for more details."
    echo ""
    echo "Would you like to continue with the batch processing test? [y/N]"
    read continue_tests
    if [[ ! "$continue_tests" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 4: Test batch processing
echo -e "${YELLOW}Step 4: Testing batch processing pipeline...${NC}"
if python run_batch_process.py; then
    echo -e "${GREEN}✓ Batch processing test successful!${NC}"
    echo ""
else
    echo -e "${RED}✗ Batch processing test failed.${NC}"
    echo "Please check the logs for more details."
    echo ""
    exit 1
fi

# All tests passed
echo -e "${GREEN}${BOLD}All tests completed successfully!${NC}"
echo -e "You can now use both sequential and batch processing features with your existing Google Drive and Airtable setup."
echo ""
echo "To start the application, run:"
echo "./run.sh"
echo ""
echo "To start a sequential processing job, use the API endpoint:"
echo "curl -X POST http://localhost:8000/batch/process -H 'Content-Type: application/json' -d '{\"processing_mode\": \"Sequential\", \"max_frames\": 10}'"
echo ""
echo "To start a batch processing job, use the API endpoint:"
echo "curl -X POST http://localhost:8000/batch/process -H 'Content-Type: application/json' -d '{\"processing_mode\": \"Batch\", \"batch_size\": 20}'"
echo "" 