#!/bin/bash
# start-chunker-background.sh
cd /home/jason/Documents/DatabaseAdvancedTokenizer/MinimalistRagIntake || { echo "Directory not found"; exit 1; }
# Use dot instead of source (more compatible)
. TheChunker/bin/activate 2>/tmp/chunker_error.log || echo "Activation failed"
./setup_chunker.sh 2>/tmp/chunker_setup_error.log || echo "Setup failed"
# Re-activate the environment
. TheChunker/bin/activate 2>/tmp/chunker_reactiv_error.log || echo "Re-activation failed"
echo "Chunker process started successfully"