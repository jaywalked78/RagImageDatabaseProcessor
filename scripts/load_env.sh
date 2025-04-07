#!/bin/bash
# Script to load environment variables from configuration files
# Usage: source scripts/load_env.sh

# Load main environment variables if file exists
if [ -f .env ]; then
  echo "Loading environment variables from .env"
  export $(grep -v '^#' .env | xargs)
fi

# Load Airtable configuration if file exists
if [ -f .env.airtable ]; then
  echo "Loading Airtable configuration from .env.airtable"
  export $(grep -v '^#' .env.airtable | xargs)
fi

# Set default values for variables that might not be set
# OCR Configuration
export ENABLE_OCR=${ENABLE_OCR:-false}
export SKIP_OCR=${SKIP_OCR:-false}

# Airtable Configuration
export AIRTABLE_BASE_ID=${AIRTABLE_BASE_ID:-}
export AIRTABLE_TABLE_NAME=${AIRTABLE_TABLE_NAME:-}
export AIRTABLE_API_KEY=${AIRTABLE_API_KEY:-}
export ENABLE_AIRTABLE_UPDATES=${ENABLE_AIRTABLE_UPDATES:-false}

# Gemini API Configuration
export GEMINI_API_KEY=${GEMINI_API_KEY:-}
export USE_GEMINI=${USE_GEMINI:-false}

# Display configuration status
echo "Configuration status:"
echo "- OCR enabled: $ENABLE_OCR"
echo "- Airtable updates enabled: $ENABLE_AIRTABLE_UPDATES"
echo "- Google Gemini API enabled: $USE_GEMINI"

# Validate required credentials if features are enabled
if [ "$ENABLE_AIRTABLE_UPDATES" = "true" ]; then
  if [ -z "$AIRTABLE_BASE_ID" ] || [ -z "$AIRTABLE_TABLE_NAME" ] || [ -z "$AIRTABLE_API_KEY" ]; then
    echo "Warning: Airtable updates are enabled but credentials are missing"
    echo "Please set AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, and AIRTABLE_API_KEY in .env.airtable"
  fi
fi

if [ "$USE_GEMINI" = "true" ]; then
  if [ -z "$GEMINI_API_KEY" ]; then
    echo "Warning: Google Gemini API is enabled but API key is missing"
    echo "Please set GEMINI_API_KEY in .env.airtable"
  fi
fi 