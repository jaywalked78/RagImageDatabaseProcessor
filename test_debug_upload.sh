#!/bin/bash
#
# test_debug_upload.sh
#
# Script to debug Airtable attachment upload issues

# Ensure the Python virtual environment is activated
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Activated virtual environment"
fi

# Make the debug script executable
chmod +x test_frame_upload_debug.py

# Run the debug uploader
echo "Running debug upload tests..."
./test_frame_upload_debug.py

# Check exit code
if [ $? -eq 0 ]; then
    echo "Debug tests passed successfully!"
else
    echo "Some debug tests failed. Check the logs for details."
fi 