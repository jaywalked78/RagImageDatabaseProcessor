#!/bin/bash
# Quick setup script for TheChunker environment

echo "Setting up TheChunker environment..."

# Create virtual environment
python3 -m venv TheChunker

# Activate virtual environment
source TheChunker/bin/activate

# Update pip
pip install --upgrade pip

# Install requirements
pip install fastapi==0.95.1 uvicorn==0.22.0 pydantic==1.10.7 python-dotenv==1.0.0 requests==2.30.0 python-multipart==0.0.6 aiofiles==23.1.0 pillow==9.5.0 langchain==0.0.267 langsmith==0.0.92 tiktoken==0.5.1 numpy>=1.20.0 regex>=2022.1.18 tenacity>=8.1.0 pyyaml>=6.0

# Create necessary directories
mkdir -p data logs

# Create basic .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cat > .env << EOF
# API Configuration
API_PORT=8777
API_HOST=0.0.0.0

# Processing Configuration
DATA_DIR=./data
LOGS_DIR=./logs
MAX_PARALLEL_PROCESSES=2

# Frame Source Configuration
FRAME_BASE_DIR=/path/to/your/frames

# Webhook Configuration
TEST_WEBHOOK_URL=http://localhost:5678/webhook-test/your-webhook-id
PRODUCTION_WEBHOOK_URL=http://localhost:5678/webhook/your-webhook-id
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Application Version
VERSION=0.1.0
EOF
    echo "Created .env file. Please update it with your actual configuration."
fi

# Make scripts executable
chmod +x run.sh run_processor.sh stop.sh quick_setup.sh 2>/dev/null

# Check for process_json_files_v2.py
if [ -f "process_json_files_v2.py" ]; then
    echo "Found process_json_files_v2.py - ready to run"
else
    echo "WARNING: process_json_files_v2.py not found. Make sure it exists before running the processor."
fi

# Done
echo "Setup complete. To activate the environment:"
echo "  source TheChunker/bin/activate"

# Deactivate
deactivate 