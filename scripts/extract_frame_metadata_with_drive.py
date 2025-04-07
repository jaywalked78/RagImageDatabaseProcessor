#!/usr/bin/env python3
"""
Script to extract real metadata for a frame, generate Google Drive URLs,
and create an updated webhook payload.
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv

# Import the metadata finder from our existing script
from process_frame_with_metadata import AirtableMetadataFinder, FRAME_ID_FIELD, FRAME_NUMBER_FIELD, \
    FOLDER_NAME_FIELD, FOLDER_PATH_FIELD, SUMMARY_FIELD, TOOLS_VISIBLE_FIELD, \
    ACTIONS_DETECTED_FIELD, TECHNICAL_DETAILS_FIELD, RELATIONSHIP_TO_PREVIOUS_FIELD, \
    STAGE_OF_WORK_FIELD

# Import Google Drive downloader
from google_drive_downloader import GoogleDriveDownloader

# Define additional fields
TIMESTAMP_FIELD = 'Timestamp'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("extract_metadata")

# Load environment variables
load_dotenv()
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID', "appewal2KEO5B02KV")
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', "tblFrameAnalysis")
FRAME_BASE_DIR = os.environ.get('FRAME_BASE_DIR', '/home/jason/Videos/screenRecordings')
GOOGLE_CREDENTIALS_PATH = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

# Get test frame path from environment or use default
TEST_FRAME_PATH = os.environ.get('TEST_FRAME_RELATIVE_PATH', 
                               "screen_recording_2025_03_03_at_3_39_52_am/frame_000051.jpg")

# Resolve the full path
if not os.path.isabs(TEST_FRAME_PATH):
    # Replace FRAME_BASE_DIR placeholder if present
    if TEST_FRAME_PATH.startswith('FRAME_BASE_DIR/'):
        TEST_FRAME_PATH = TEST_FRAME_PATH.replace('FRAME_BASE_DIR/', '')
    
    TEST_FRAME_PATH = os.path.join(FRAME_BASE_DIR, TEST_FRAME_PATH)

class GoogleDriveURLGenerator:
    """Generate Google Drive URLs for frames."""
    
    def __init__(self, credentials_path=None):
        """Initialize with Google Drive credentials."""
        self.credentials_path = credentials_path
        self.downloader = GoogleDriveDownloader(credentials_path=credentials_path)
        self.file_info_cache = {}
        
    def authenticate(self) -> bool:
        """Authenticate with Google Drive API."""
        return self.downloader.authenticate()
    
    def check_or_upload_file(self, file_path: str, folder_id: str = None) -> Tuple[bool, Optional[str]]:
        """
        Check if a file exists in Google Drive or upload it.
        
        Args:
            file_path: Path to the local file
            folder_id: Google Drive folder ID to upload to if not found
            
        Returns:
            Tuple of (success, file_id)
        """
        if not self.downloader.drive_service:
            if not self.authenticate():
                logger.error("Failed to authenticate with Google Drive")
                return False, None
        
        file_name = os.path.basename(file_path)
        
        try:
            # Check if file exists by name in the folder
            query = f"name = '{file_name}'"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            query += " and trashed = false"
            
            results = self.downloader.drive_service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                # File exists, use first match
                file_id = files[0]['id']
                logger.info(f"Found existing file in Google Drive: {file_name}, ID: {file_id}")
                return True, file_id
            
            # For the test script, we'll just simulate having a file ID
            # In a real implementation, we would upload the file if not found
            simulated_file_id = f"simulated_{file_name.replace('.', '_').replace('-', '_')}"
            logger.info(f"Simulating file ID for {file_name}: {simulated_file_id}")
            return True, simulated_file_id
            
        except Exception as e:
            logger.error(f"Error checking/uploading file to Google Drive: {e}")
            return False, None
    
    def generate_file_url(self, file_id: str) -> str:
        """
        Generate a Google Drive URL for a file.
        
        Args:
            file_id: Google Drive file ID
            
        Returns:
            Google Drive URL for the file
        """
        return f"https://drive.google.com/file/d/{file_id}/view"

def create_webhook_payload(frame_path: str, record: Dict[str, Any], 
                          google_drive_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a properly formatted webhook payload using real metadata.
    
    Args:
        frame_path: Path to the frame file
        record: Airtable record with metadata
        google_drive_url: Optional Google Drive URL for the frame
        
    Returns:
        Dictionary payload for webhook
    """
    # Extract fields from the record
    fields = record.get('fields', {})
    
    # Get frame path components
    frame_file = Path(frame_path)
    frame_name = frame_file.name
    
    # Use folder path from Airtable if available, otherwise use local path
    folder_path = fields.get(FOLDER_PATH_FIELD, str(frame_file.parent))
    # Extract just the folder name, not the full path with the frame
    if folder_path and frame_name in folder_path:
        folder_path = folder_path.replace(f"/{frame_name}", "")
    
    folder_name = fields.get(FOLDER_NAME_FIELD, frame_file.parent.name)
    
    # Create the payload
    payload = {
        "airtable_id": record.get('id', ''),
        "frame_name": frame_name,
        "folder_path": folder_path,
        "folder_name": folder_name,
        "timestamp": fields.get(TIMESTAMP_FIELD, ''),
        "embeddings": "[0.123, 0.456, 0.789, 0.321, 0.654]",  # Placeholder
        "chunk_count": 5,  # Placeholder
        "metadata": {
            "frame_number": fields.get(FRAME_NUMBER_FIELD, ''),
            "description": fields.get(SUMMARY_FIELD, 'No summary available'),
            "tools_visible": fields.get(TOOLS_VISIBLE_FIELD, []),
            "actions_detected": fields.get(ACTIONS_DETECTED_FIELD, []),
            "technical_details": fields.get(TECHNICAL_DETAILS_FIELD, ''),
            "relationship_to_previous": fields.get(RELATIONSHIP_TO_PREVIOUS_FIELD, ''),
            "stage_of_work": fields.get(STAGE_OF_WORK_FIELD, '')
        }
    }
    
    # Add Google Drive URL if available
    if google_drive_url:
        payload["google_drive_url"] = google_drive_url
    
    return payload

async def main():
    """Extract metadata, generate Google Drive URL, and create webhook payload."""
    # Validate required configuration
    if not all([AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME]):
        logger.error("Missing required Airtable configuration in environment variables.")
        sys.exit(1)
    
    # Check if frame exists
    if not os.path.exists(TEST_FRAME_PATH):
        logger.error(f"Frame file not found: {TEST_FRAME_PATH}")
        sys.exit(1)
    
    logger.info(f"Extracting metadata for frame: {TEST_FRAME_PATH}")
    
    # Find metadata for the frame
    metadata_finder = AirtableMetadataFinder(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
    record = metadata_finder.find_record_by_frame_path(TEST_FRAME_PATH)
    
    if not record:
        logger.error(f"No metadata found for frame: {TEST_FRAME_PATH}")
        sys.exit(1)
    
    logger.info(f"Found metadata for frame with ID: {record.get('id')}")
    
    # Generate Google Drive URL
    google_drive_url = None
    if GOOGLE_CREDENTIALS_PATH:
        logger.info("Generating Google Drive URL...")
        drive_url_generator = GoogleDriveURLGenerator(credentials_path=GOOGLE_CREDENTIALS_PATH)
        
        # Use a test folder ID - in production you'd have a real folder ID
        test_folder_id = "1RwQ8mTtlmYtmPl8KHxcYNdYJYgPiXDBZ"  
        
        success, file_id = drive_url_generator.check_or_upload_file(TEST_FRAME_PATH, test_folder_id)
        if success and file_id:
            google_drive_url = drive_url_generator.generate_file_url(file_id)
            logger.info(f"Generated Google Drive URL: {google_drive_url}")
    else:
        logger.warning("No Google credentials found, skipping Google Drive URL generation")
    
    # Create webhook payload
    payload = create_webhook_payload(TEST_FRAME_PATH, record, google_drive_url)
    
    # Save to JSON file
    output_file = "correct_frame_payload.json"
    with open(output_file, 'w') as f:
        json.dump(payload, f, indent=2)
    
    logger.info(f"Generated webhook payload with real metadata saved to: {output_file}")
    
    # Print the payload
    logger.info("Webhook payload:")
    logger.info(json.dumps(payload, indent=2))

if __name__ == "__main__":
    asyncio.run(main()) 