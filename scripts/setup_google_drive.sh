#!/bin/bash

echo "========================================================"
echo "  Google Drive Service Account Setup Guide"
echo "========================================================"
echo ""
echo "This script will guide you through the process of setting up a"
echo "Google Drive Service Account for batch processing frames."
echo ""
echo "Steps to follow:"
echo ""
echo "1. Go to the Google Cloud Console: https://console.cloud.google.com/"
echo ""
echo "2. Create a new project or select an existing one"
echo "   - Click on the project dropdown in the top navigation bar"
echo "   - Click on 'New Project' or select an existing one"
echo ""
echo "3. Enable the Google Drive API"
echo "   - Go to 'APIs & Services' > 'Library'"
echo "   - Search for 'Google Drive API'"
echo "   - Click on 'Google Drive API' and then 'Enable'"
echo ""
echo "4. Create a service account"
echo "   - Go to 'APIs & Services' > 'Credentials'"
echo "   - Click 'Create Credentials' > 'Service Account'"
echo "   - Enter a name for the service account"
echo "   - Click 'Create and Continue'"
echo ""
echo "5. Grant the service account access to your project"
echo "   - Select a role (recommend 'Viewer' as minimum)"
echo "   - Click 'Continue' and then 'Done'"
echo ""
echo "6. Create a service account key"
echo "   - Click on the service account you just created"
echo "   - Go to the 'Keys' tab"
echo "   - Click 'Add Key' > 'Create new key'"
echo "   - Select 'JSON' as the key type"
echo "   - Click 'Create' to download the key file"
echo ""
echo "7. Move the downloaded key file to this directory"
echo "   - Rename it to 'service-account.json'"
echo "   - Set the GOOGLE_SERVICE_ACCOUNT_FILE environment variable in .env"
echo ""
echo "8. Share your Google Drive files or folders with the service account email"
echo "   - The service account email is in the downloaded JSON file (client_email field)"
echo "   - Open your Google Drive"
echo "   - Right-click on the folder containing your frames"
echo "   - Click 'Share' and add the service account email with 'Viewer' access"
echo ""
echo "========================================================"
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    # Check if GOOGLE_SERVICE_ACCOUNT_FILE is in .env
    if ! grep -q "GOOGLE_SERVICE_ACCOUNT_FILE" .env; then
        echo "Adding GOOGLE_SERVICE_ACCOUNT_FILE to .env..."
        echo "GOOGLE_SERVICE_ACCOUNT_FILE=service-account.json" >> .env
    fi
else
    echo "Warning: .env file not found. Please create one and add GOOGLE_SERVICE_ACCOUNT_FILE=service-account.json"
fi

# Check if service-account.json exists
if [ -f "service-account.json" ]; then
    echo "Found service-account.json file."
    
    # Extract service account email
    SERVICE_ACCOUNT_EMAIL=$(grep -o '"client_email": "[^"]*' service-account.json | cut -d '"' -f 4)
    if [ ! -z "$SERVICE_ACCOUNT_EMAIL" ]; then
        echo ""
        echo "Your service account email is: $SERVICE_ACCOUNT_EMAIL"
        echo "Make sure to share your Google Drive folders with this email."
    fi
else
    echo "service-account.json not found. Please follow the steps above to create and download it."
fi

echo ""
echo "Setup guide completed. Once you've followed all steps, you can use the"
echo "batch processing endpoint to import frames from Airtable and Google Drive."
echo "" 