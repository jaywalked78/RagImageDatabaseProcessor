#!/bin/bash

# TheLogicLoomDB Startup Script
# This script starts the API service with proper configuration

# Text formatting
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed. Please install Python 3.8 or newer.${NC}"
    exit 1
fi

# Check if virtualenv is installed
if ! command -v python3 -m venv &> /dev/null; then
    echo -e "${YELLOW}Warning: Python venv module not found. Will try to use system Python.${NC}"
    PYTHON="python3"
else
    # Check if virtual environment exists, create if needed
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating Python virtual environment...${NC}"
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error creating virtual environment. Will use system Python.${NC}"
            PYTHON="python3"
        else
            PYTHON="venv/bin/python"
        fi
    else
        PYTHON="venv/bin/python"
    fi
fi

# Install dependencies if needed
if [ -d "venv" ]; then
    echo -e "${YELLOW}Installing/updating dependencies...${NC}"
    $PYTHON -m pip install --upgrade pip
    $PYTHON -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error installing dependencies. Please check requirements.txt${NC}"
        exit 1
    fi
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found, using .env.example as template${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}Created .env file from example. Please edit it with your configuration.${NC}"
    else
        echo -e "${RED}Error: Neither .env nor .env.example found. Cannot continue.${NC}"
        exit 1
    fi
fi

# Verify configuration
echo -e "${YELLOW}Verifying configuration...${NC}"
$PYTHON run.py --verify-config
if [ $? -ne 0 ]; then
    echo -e "${RED}Configuration check failed. Please correct the issues in your .env file.${NC}"
    echo -e "${YELLOW}To continue anyway (not recommended), press Enter. To exit, press Ctrl+C.${NC}"
    read -r
fi

# Create logs directory if not exists
mkdir -p logs

# Start the server
echo -e "${GREEN}${BOLD}Starting TheLogicLoomDB API Server...${NC}"
echo -e "${YELLOW}Logs will be written to logs/logicLoom.log${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"

# Run the application
$PYTHON run.py "$@" 