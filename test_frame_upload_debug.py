#!/usr/bin/env python3
"""
Debug Test Frame Upload Script

This script debugs the frame upload issues with Airtable by:
1. Using smaller images
2. Providing full error messages
3. Testing different attachment formats
"""

import os
import sys
import re
import glob
import logging
import base64
import json
import time
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv
import requests
from PIL import Image
import io

# Configure verbose logging
os.makedirs("logs/airtable", exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for more verbose output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/airtable/debug_upload_{time.strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("debug_uploader")

# Load environment variables
load_dotenv()
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', 'tblFrameAnalysis')
FRAME_BASE_DIR = os.environ.get('FRAME_BASE_DIR', '/home/jason/Videos/screenRecordings')

# Rate limiting for Airtable API - increase delay to avoid rate limits
RATE_LIMIT_SLEEP = float(os.environ.get('AIRTABLE_RATE_LIMIT_SLEEP', '0.5'))
MAX_UPLOAD_SIZE = 1024 * 1024 * 1  # 1MB max file size (reduced for testing)

class DebugFrameUploader:
    """Debug uploader to test Airtable attachment issues."""

    def __init__(self, token, base_id, table_name, rate_limit=RATE_LIMIT_SLEEP):
        """Initialize uploader with API credentials."""
        self.token = token
        self.base_id = base_id
        self.table_name = table_name
        self.rate_limit = rate_limit
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.base_url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        
        logger.info(f"Initialized debug uploader for {table_name} in base {base_id}")
    
    def get_fields_metadata(self):
        """
        Get metadata about the table fields to verify FrameData is an attachment field.
        """
        try:
            logger.info("Getting table metadata...")
            
            # Apply rate limiting
            time.sleep(self.rate_limit)
            
            # Make API request to fetch metadata
            response = requests.get(
                f"https://api.airtable.com/v0/meta/bases/{self.base_id}/tables",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Error getting table metadata: {response.status_code}")
                if response.status_code == 403:
                    logger.error("PERMISSION ERROR: Your API token may not have schema access. Personal Access Tokens need 'data.records:read' and 'schema.bases:read' scopes.")
                logger.error(f"Response: {response.text}")
                return None
            
            data = response.json()
            logger.debug(f"Metadata response: {json.dumps(data, indent=2)}")
            
            # Find the table and check fields
            tables = data.get('tables', [])
            for table in tables:
                if table.get('name') == self.table_name or table.get('id') == self.table_name:
                    fields = table.get('fields', [])
                    for field in fields:
                        if field.get('name') == 'FrameData':
                            field_type = field.get('type')
                            logger.info(f"Found FrameData field with type: {field_type}")
                            return field_type
            
            logger.warning("FrameData field not found in table metadata")
            return None
            
        except Exception as e:
            logger.error(f"Error getting table metadata: {e}")
            return None
    
    def get_airtable_records_by_id(self, record_id: str) -> Dict[str, Any]:
        """
        Get a specific Airtable record by ID.
        """
        try:
            logger.info(f"Getting record by ID: {record_id}")
            
            # Apply rate limiting
            time.sleep(self.rate_limit)
            
            # Make API request
            response = requests.get(
                f"{self.base_url}/{record_id}",
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"Error getting record: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
            
            data = response.json()
            return data
            
        except Exception as e:
            logger.error(f"Error getting record: {e}")
            return None
    
    def get_first_record(self) -> Dict[str, Any]:
        """
        Get the first record from the table to test with.
        """
        try:
            logger.info("Getting first record from table...")
            
            # Apply rate limiting
            time.sleep(self.rate_limit)
            
            # Make API request
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params={
                    "maxRecords": 1
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Error getting first record: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
            
            data = response.json()
            records = data.get('records', [])
            
            if not records:
                logger.error("No records found in the table")
                return None
            
            return records[0]
            
        except Exception as e:
            logger.error(f"Error getting first record: {e}")
            return None
    
    def extract_frame_number(self, frame_name: str) -> int:
        """Extract the frame number from a filename."""
        match = re.search(r'frame_0*(\d+)\.', frame_name)
        if match:
            return int(match.group(1))
        return 0
    
    def resize_image(self, img, max_size=MAX_UPLOAD_SIZE, max_dimension=1000):
        """
        Resize an image to fit within Airtable's limits.
        
        Args:
            img: PIL Image object
            max_size: Maximum file size in bytes
            max_dimension: Maximum dimension in pixels
            
        Returns:
            Resized PIL Image
        """
        # First resize based on dimensions
        width, height = img.size
        if width > max_dimension or height > max_dimension:
            # Calculate scaling factor
            scale = min(max_dimension / width, max_dimension / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            logger.info(f"Resizing image from {width}x{height} to {new_width}x{new_height}")
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Check size
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        size = buffer.getbuffer().nbytes
        
        # If still too large, reduce quality
        quality = 85
        while size > max_size and quality > 10:
            quality -= 10
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality)
            size = buffer.getbuffer().nbytes
            logger.info(f"Reduced image quality to {quality}%, size: {size/1024:.1f}KB")
        
        logger.info(f"Final image size: {size/1024:.1f}KB")
        return img
    
    def upload_attachment_test(self, record_id: str, image_path: str) -> bool:
        """
        Test uploading an attachment to a specific record.
        
        Args:
            record_id: Airtable record ID
            image_path: Path to image file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            frame_name = os.path.basename(image_path)
            logger.info(f"Testing attachment upload for {frame_name} to record {record_id}")
            
            # Load and resize the image
            img = Image.open(image_path)
            original_size = os.path.getsize(image_path)
            logger.info(f"Original image size: {original_size/1024:.1f}KB")
            
            img = self.resize_image(img)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=80)
            base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Prepare the update data - FIX: Use only content_type, not type field
            mime_type = "image/jpeg"
            update_data = {
                "fields": {
                    "FrameData": [
                        {
                            "filename": frame_name,
                            "content_type": mime_type,
                            "data": base64_data
                        }
                    ]
                }
            }
            
            # Log request body size
            update_json = json.dumps(update_data)
            logger.info(f"Request body size: {len(update_json)/1024:.1f}KB")
            
            # Apply rate limiting
            time.sleep(self.rate_limit)
            
            # Make the API request
            logger.info("Sending attachment upload request...")
            response = requests.patch(
                f"{self.base_url}/{record_id}",
                headers=self.headers,
                json=update_data
            )
            
            if response.status_code != 200:
                logger.error(f"Error uploading attachment: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
            
            logger.info(f"Successfully uploaded attachment")
            return True
            
        except Exception as e:
            logger.error(f"Error in attachment test: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    async def run_debug_tests(self, folder_path: str) -> Dict[str, Any]:
        """
        Run several debug tests to diagnose Airtable attachment issues.
        
        Args:
            folder_path: Path to the folder containing frames
            
        Returns:
            Test results
        """
        results = {
            "metadata_check": False,
            "test_record": False,
            "attachment_test": False
        }
        
        # Step 1: Check table metadata and field type
        field_type = self.get_fields_metadata()
        if field_type == "multipleAttachments":
            logger.info("Metadata check: PASSED - FrameData is an attachment field")
            results["metadata_check"] = True
        else:
            logger.error(f"Metadata check: FAILED - FrameData has type {field_type} instead of multipleAttachments")
        
        # Step 2: Get first record to test with
        first_record = self.get_first_record()
        if first_record:
            record_id = first_record.get('id')
            logger.info(f"Found test record: {record_id}")
            results["test_record"] = True
            
            # Step 3: Try to upload a test attachment
            frame_pattern = os.path.join(folder_path, "*.jpg")
            frames = glob.glob(frame_pattern)
            
            if frames:
                # Use the first frame for testing
                test_frame = frames[0]
                logger.info(f"Using {test_frame} for attachment test")
                
                attachment_result = self.upload_attachment_test(record_id, test_frame)
                results["attachment_test"] = attachment_result
                
                if attachment_result:
                    logger.info("Attachment test: PASSED")
                else:
                    logger.error("Attachment test: FAILED")
            else:
                logger.error(f"No frames found in {folder_path}")
        
        return results

async def main():
    """Main entry point for debug script."""
    parser = argparse.ArgumentParser(
        description="Debug Frame Upload Issues with Airtable"
    )
    
    parser.add_argument("--folder", 
                       type=str,
                       default=os.path.join(FRAME_BASE_DIR, "screen_recording_2025_02_20_at_12_14_43_pm"),
                       help="Folder containing frames to test with")
    
    args = parser.parse_args()
    
    try:
        # Validate credentials
        if not AIRTABLE_TOKEN or not AIRTABLE_BASE_ID:
            logger.error("Missing Airtable credentials")
            return 1
        
        # Initialize uploader
        uploader = DebugFrameUploader(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        
        # Run debug tests
        print(f"\nRunning Airtable attachment debug tests")
        print(f"Using folder: {args.folder}")
        print("------------------------------------------------------")
        
        results = await uploader.run_debug_tests(args.folder)
        
        print("------------------------------------------------------")
        print("Debug Test Results:")
        for test, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test}: {status}")
        
        print("\nCheck the logs for detailed information.")
        return 0 if all(results.values()) else 1
        
    except Exception as e:
        logger.error(f"Error in debug script: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 