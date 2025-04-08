#!/bin/bash
#
# test_upload.sh
#
# Simple script to test uploading a few frames to Airtable

# Ensure the Python virtual environment is activated
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Activated virtual environment"
fi

# Make the test script executable
chmod +x test_frame_upload.py

# Run the test uploader with 3 frames
echo "Running test frame uploader..."
./test_frame_upload.py --count 3

exit $? 