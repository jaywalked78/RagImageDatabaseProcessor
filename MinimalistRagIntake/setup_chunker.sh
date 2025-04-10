#!/bin/bash
# Setup script for TheChunker environment

# Color configuration for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}==>${NC} $1"
}

# Function to print warnings
print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

# Function to print errors
print_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}$1${NC}"
    echo -e "${BLUE}$(printf '=%.0s' {1..50})${NC}"
}

# Check Python installation
print_section "Checking Python Installation"
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    print_status "Python is installed: $python_version"
else
    print_error "Python 3 is not installed. Please install Python 3.7+ and try again."
    exit 1
fi

# Create virtual environment
print_section "Setting Up Virtual Environment"
VENV_NAME="TheChunker"

if [ -d "$VENV_NAME" ]; then
    print_warning "Virtual environment '$VENV_NAME' already exists. Removing it for a clean setup."
    rm -rf "$VENV_NAME"
fi

print_status "Creating virtual environment: $VENV_NAME"
python3 -m venv "$VENV_NAME"

if [ ! -d "$VENV_NAME" ]; then
    print_error "Failed to create virtual environment."
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment"
source "$VENV_NAME/bin/activate"

# Verify activation
if [[ "$VIRTUAL_ENV" != *"$VENV_NAME"* ]]; then
    print_error "Failed to activate virtual environment."
    exit 1
fi

print_status "Virtual environment activated successfully"

# Update pip
print_section "Updating Package Manager"
print_status "Upgrading pip to latest version"
pip install --upgrade pip

# Create/Update requirements.txt
print_section "Updating Requirements File"

cat > requirements.txt << EOF
fastapi==0.95.1
uvicorn==0.22.0
pydantic==1.10.7
python-dotenv==1.0.0
requests==2.30.0
# Added additional dependencies
python-multipart==0.0.6  # For form data processing
aiofiles==23.1.0         # For asynchronous file operations
pillow==9.5.0            # For image processing if needed
# Dependencies for process_json_files_v2.py
langchain==0.0.267       # For text splitting and semantic chunking
langsmith==0.0.92        # Required by langchain with specific version
tiktoken==0.5.1          # For token counting in text splitters
numpy>=1.20.0            # Required by langchain
regex>=2022.1.18         # Required for text processing
tenacity>=8.1.0          # For robust API calls
pyyaml>=6.0              # For configuration handling
EOF

print_status "Updated requirements.txt with all necessary dependencies"

# Install dependencies
print_section "Installing Dependencies"
print_status "Installing required packages"
pip install -r requirements.txt

# Check if installation was successful
if [ $? -ne 0 ]; then
    print_error "Failed to install required packages."
    exit 1
fi
print_status "Dependencies installed successfully"

# Check for process_json_files_v2.py
print_section "Checking Script Files"
if [ -f "process_json_files_v4.py" ]; then
    print_status "Found process_json_files_v4.py"
else
    print_warning "process_json_files_v4.py not found. Make sure it exists before running the processor."
fi

# Create necessary directories
print_section "Creating Project Structure"
mkdir -p data logs

# Create/update .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    print_status "Creating .env.example file"
    cat > .env.example << EOF
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
else
    print_status ".env.example already exists, skipping creation"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from .env.example"
    cp .env.example .env
    print_warning "Please update the .env file with your actual configuration values."
else
    print_status ".env file already exists, skipping creation"
fi

# Make run scripts executable
print_section "Setting Up Execution Rights"
if [ -f "run.sh" ]; then
    chmod +x run.sh
    print_status "Made run.sh executable"
fi

if [ -f "stop.sh" ]; then
    chmod +x stop.sh
    print_status "Made stop.sh executable"
fi

if [ -f "run_processor.sh" ]; then
    chmod +x run_processor.sh
    print_status "Made run_processor.sh executable"
fi

chmod +x setup_chunker.sh
print_status "Made setup_chunker.sh executable"

# Final instructions
print_section "Setup Complete"
echo -e "TheChunker environment has been set up successfully.\n"
echo -e "To activate the environment:"
echo -e "  ${GREEN}source TheChunker/bin/activate${NC}\n"
echo -e "To start the service:"
echo -e "  ${GREEN}./run.sh${NC}\n"
echo -e "To process frames:"
echo -e "  ${GREEN}./run_processor.sh <folder_name>${NC}\n"
echo -e "To exit the virtual environment when done:"
echo -e "  ${GREEN}deactivate${NC}\n"

# Deactivate virtual environment
deactivate

print_status "Setup script completed successfully" 