"""
Test script to verify Google Drive API connection.
"""

import os
import sys
from dotenv import load_dotenv
from src.integrations.google_drive import GoogleDriveClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_google_drive")

# Load environment variables
load_dotenv()

def test_connection():
    """Test connection to Google Drive API."""
    try:
        # Get the service account file path
        service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        logger.info(f"Using service account file: {service_account_file}")
        
        # Check if the file exists
        if not os.path.exists(service_account_file):
            logger.error(f"Service account file not found: {service_account_file}")
            return False
            
        # Initialize the Google Drive client
        logger.info("Initializing Google Drive client...")
        drive_client = GoogleDriveClient()
        
        # List files to test connection
        logger.info("Listing files to test connection...")
        files = drive_client.list_files(page_size=10)
        
        # Print file information
        logger.info(f"Successfully retrieved {len(files)} files:")
        for i, file in enumerate(files[:5], 1):  # Show up to 5 files
            logger.info(f"  {i}. {file.get('name', 'Unnamed')} (ID: {file.get('id')})")
            
        logger.info("Google Drive connection test successful!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing Google Drive connection: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Google Drive connection...")
    success = test_connection()
    
    if success:
        print("✅ Connection successful! Your service account is properly configured.")
        sys.exit(0)
    else:
        print("❌ Connection failed. Please check the logs for details.")
        sys.exit(1) 