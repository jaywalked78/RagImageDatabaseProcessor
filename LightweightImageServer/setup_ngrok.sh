#!/bin/bash
# setup_ngrok.sh - Helper script to set up ngrok authentication
# This script guides users through ngrok installation and authentication

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Ngrok Setup Assistant ===${NC}"
echo -e "This script will help you set up ngrok for the LightweightImageServer"

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
  echo -e "${RED}ERROR: ngrok is not installed${NC}"
  echo -e "${YELLOW}Please install ngrok:${NC}"
  echo -e "1. Download from ${BLUE}https://ngrok.com/download${NC}"
  echo -e "2. Extract the ngrok binary"
  echo -e "3. Move it to a directory in your PATH (e.g., /usr/local/bin)"
  echo -e "   sudo mv ngrok /usr/local/bin/"
  echo -e "4. Ensure it's executable: ${BLUE}chmod +x /usr/local/bin/ngrok${NC}"
  echo -e "\nRun this script again after installing ngrok."
  exit 1
fi

echo -e "${GREEN}✓ Ngrok is installed${NC}"

# Check if ngrok is authenticated already
echo -e "\n${BLUE}Checking ngrok authentication...${NC}"
if ngrok config check &> /dev/null; then
  # Check for authtoken in config
  if grep -q "authtoken" ~/.config/ngrok/ngrok.yml 2>/dev/null; then
    echo -e "${GREEN}✓ Ngrok is already authenticated${NC}"
    ngrok config check
    echo -e "\n${GREEN}You're all set! You can now run:${NC}"
    echo -e "${BLUE}./ngrok_n8n_integration.sh${NC}"
    exit 0
  fi
fi

# Prompt for authentication
echo -e "\n${YELLOW}Ngrok requires authentication to work properly.${NC}"
echo -e "You'll need to create a free account at ${BLUE}https://ngrok.com${NC} and get your authtoken."
echo -e "\n${YELLOW}Steps:${NC}"
echo -e "1. Sign up at ${BLUE}https://ngrok.com/signup${NC}"
echo -e "2. Log in to your ngrok dashboard"
echo -e "3. Find your authtoken at ${BLUE}https://dashboard.ngrok.com/get-started/your-authtoken${NC}"

# Prompt for token
echo -e "\n${YELLOW}Do you have your authtoken ready? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
  echo -e "\n${YELLOW}Please enter your ngrok authtoken:${NC}"
  read -r authtoken
  
  if [[ -z "$authtoken" ]]; then
    echo -e "${RED}Invalid token. Please try again.${NC}"
    exit 1
  fi
  
  # Configure ngrok with the token
  ngrok config add-authtoken "$authtoken"
  
  if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ Ngrok successfully authenticated!${NC}"
    echo -e "You can now run: ${BLUE}./ngrok_n8n_integration.sh${NC}"
  else
    echo -e "\n${RED}Authentication failed. Please check your token and try again.${NC}"
    exit 1
  fi
else
  echo -e "\n${YELLOW}Please complete the steps above and run this script again when you have your authtoken.${NC}"
  exit 1
fi 