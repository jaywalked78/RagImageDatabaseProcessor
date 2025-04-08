#!/bin/bash
# Simple script to process frames
# No fancy options, just runs the processor

# Set up error handling
set -e
set -o pipefail

# Load environment variables
source .env

# Batch size
BATCH_SIZE=10

echo "$(date) - Starting frame processing with batch size: $BATCH_SIZE"

# Run the processor
node simple_process_frames.js $BATCH_SIZE

echo "$(date) - Process completed" 