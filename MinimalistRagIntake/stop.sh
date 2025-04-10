#!/bin/bash
# Script to stop the running FastAPI application

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}==> Stopping RAG Intake API${NC}"

# Find the PID of the uvicorn process serving our app
PID=$(ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}')

if [ -z "$PID" ]; then
    echo -e "${YELLOW}No running instance found.${NC}"
    exit 0
fi

echo -e "${GREEN}Found process with PID: $PID. Stopping...${NC}"

# Kill the process
kill $PID

# Check if kill was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Process successfully terminated.${NC}"
else
    echo -e "${RED}Failed to terminate process. Try manually with: kill -9 $PID${NC}"
    exit 1
fi

echo -e "${GREEN}RAG Intake API stopped.${NC}" 