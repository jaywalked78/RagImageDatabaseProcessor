#!/bin/bash
# Script to set up a virtual environment, install dependencies, and run the FastAPI application

# Configuration
VENV_NAME="rag_intake_venv"
REQUIREMENTS_FILE="requirements.txt"
APP_MODULE="main:app"
HOST="0.0.0.0"
PORT=8777

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Exit on error
set -e

# Function to print step information
print_step() {
    echo -e "${GREEN}==> $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    print_step "Creating virtual environment: $VENV_NAME"
    python3 -m venv "$VENV_NAME"
else
    print_warning "Virtual environment already exists. Using existing environment."
fi

# Activate virtual environment
print_step "Activating virtual environment"
source "$VENV_NAME/bin/activate"

# Upgrade pip
print_step "Upgrading pip"
pip install --upgrade pip

# Install dependencies
if [ -f "$REQUIREMENTS_FILE" ]; then
    print_step "Installing dependencies from $REQUIREMENTS_FILE"
    pip install -r "$REQUIREMENTS_FILE"
else
    echo -e "${RED}Requirements file $REQUIREMENTS_FILE not found.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_warning ".env file not found. Copying from .env.example"
        cp .env.example .env
    else
        print_warning "No .env or .env.example file found. Some features may not work properly."
    fi
fi

# Create data and logs directories
mkdir -p data logs

# Check if port is already in use and kill the process
print_step "Checking if port $PORT is already in use"

# Function to check if a port is in use and get the PID
check_port() {
    local port=$1
    local pid=""
    
    # Try lsof first
    if command -v lsof &> /dev/null; then
        pid=$(lsof -ti:$port)
    # Then try netstat
    elif command -v netstat &> /dev/null; then
        pid=$(netstat -tulnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d'/' -f1 | head -n1)
    # Then try ss (modern replacement for netstat)
    elif command -v ss &> /dev/null; then
        pid=$(ss -tulnp | grep ":$port " | grep -o 'pid=[0-9]*' | cut -d'=' -f2 | head -n1)
    else
        print_warning "Neither lsof, netstat, nor ss is available. Cannot check if port is in use."
        return
    fi
    
    echo "$pid"
}

PORT_PID=$(check_port $PORT)
if [ ! -z "$PORT_PID" ]; then
    print_warning "Process with PID $PORT_PID is using port $PORT. Attempting to terminate it."
    kill -15 $PORT_PID 2>/dev/null || kill -9 $PORT_PID 2>/dev/null
    sleep 2  # Give the system time to release the port
    
    # Verify port is now free
    PORT_PID_CHECK=$(check_port $PORT)
    if [ ! -z "$PORT_PID_CHECK" ]; then
        echo -e "${RED}Failed to free up port $PORT. Please terminate process $PORT_PID_CHECK manually.${NC}"
        exit 1
    else
        print_step "Successfully freed port $PORT"
    fi
else
    print_step "Port $PORT is available"
fi

# Run the application
print_step "Starting FastAPI application on $HOST:$PORT"
uvicorn $APP_MODULE --host $HOST --port $PORT

# This line will only be reached if uvicorn exits
print_step "Application stopped"

# Deactivate virtual environment (this line won't be reached during normal operation)
deactivate 