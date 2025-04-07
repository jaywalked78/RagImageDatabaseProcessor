"""
Test script to list the frames in a specific screen recording subfolder in Google Drive.
"""

import os
import logging
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("google_drive_test")

# Load environment variables
load_dotenv()

def get_drive_service():
    """Create and return a Google Drive service object using service account credentials."""
    try:
        # Path to the service account credentials JSON file
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not credentials_path:
            credentials_path = 'credentials/credentials.json'
            
        if not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found at: {credentials_path}")
            
        # Create credentials
        scopes = ['https://www.googleapis.com/auth/drive.readonly']
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=scopes)
            
        # Build the Drive API client
        service = build('drive', 'v3', credentials=credentials)
        logger.info("Successfully created Google Drive service")
        return service
    except Exception as e:
        logger.error(f"Error creating Google Drive service: {str(e)}")
        raise

def list_folder_contents(service, folder_id, max_items=50):
    """List the contents of a folder in Google Drive."""
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType, createdTime, imageMediaMetadata)',
            pageSize=max_items,
            orderBy='name'  # Order by name to see the frame sequence
        ).execute()
        
        items = results.get('files', [])
        if not items:
            logger.warning(f"Folder is empty")
            return []
            
        logger.info(f"Found {len(items)} items in the folder")
        return items
    except Exception as e:
        logger.error(f"Error listing folder contents: {str(e)}")
        raise

def main():
    """Main function to list frames in a screen recording folder."""
    # Folder ID to examine - using the most recent one from the previous test
    folder_id = "1ApuDT8RTag3mrlIEbClHkHAZ3dr67P0a"  # screen_recording_2025_04_05_at_3_22_53_am
    
    print(f"🔍 Listing frames in screen recording folder (ID: {folder_id})...")
    
    try:
        # Create Drive service
        service = get_drive_service()
        
        # List folder contents
        contents = list_folder_contents(service, folder_id)
        
        if not contents:
            print(f"   (Empty folder)")
            return False
        
        # Count image files
        image_count = sum(1 for item in contents if 'image' in item.get('mimeType', ''))
        print(f"   Found {image_count} image files out of {len(contents)} total items")
        
        # Display the first 15 items
        print(f"   Contents (showing first 15 items):")
        image_files = [item for item in contents if 'image' in item.get('mimeType', '')]
        
        for i, item in enumerate(image_files[:15]):
            print(f"   {i+1}. 🖼️ {item['name']} (ID: {item['id']})")
            
            # Print image metadata if available
            if 'imageMediaMetadata' in item:
                metadata = item['imageMediaMetadata']
                print(f"      Dimensions: {metadata.get('width', 'N/A')}x{metadata.get('height', 'N/A')}")
                print(f"      Time: {metadata.get('time', 'N/A')}")
        
        if len(image_files) > 15:
            print(f"   ... and {len(image_files) - 15} more image files")
        
        print("\n✅ Google Drive folder contents listed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Google Drive test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 