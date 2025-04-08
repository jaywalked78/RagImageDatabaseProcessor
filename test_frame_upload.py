#!/usr/bin/env python3
"""
Test Frame Upload Script

This script uploads just 3 frames to Airtable to test the upload process.
It's a simplified version of the main uploader to verify everything works correctly.
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

# Configure logging
os.makedirs("logs/airtable", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/airtable/test_upload_{time.strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("test_uploader")

# Load environment variables
load_dotenv()
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', 'tblFrameAnalysis')
FRAME_BASE_DIR = os.environ.get('FRAME_BASE_DIR', '/home/jason/Videos/screenRecordings')

# Rate limiting for Airtable API
RATE_LIMIT_SLEEP = float(os.environ.get('AIRTABLE_RATE_LIMIT_SLEEP', '0.25'))
MAX_UPLOAD_SIZE = 1024 * 1024 * 2  # Default max 2MB per file for attachments

class TestFrameUploader:
    """
    Class to handle uploading a few test frames to Airtable.
    """

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
        
        logger.info(f"Initialized test uploader for {table_name} in base {base_id}")
    
    def get_airtable_records_by_frame_id(self, frame_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get Airtable records that match specific frame IDs.
        Handles pagination to retrieve all matching records.
        
        Args:
            frame_ids: List of frame IDs to match
            
        Returns:
            List of matching Airtable records
        """
        # Create OR formula for all frame IDs
        or_conditions = []
        for frame_id in frame_ids:
            # Extract just the filename without path
            filename = os.path.basename(frame_id)
            or_conditions.append(f"FIND('{filename}', {{FolderPath}}) > 0")
        
        # Combine conditions with OR
        formula = f"OR({','.join(or_conditions)})"
        
        try:
            logger.info(f"Searching for {len(frame_ids)} specific frames in Airtable")
            
            # Parameters for the first request
            params = {
                "filterByFormula": formula,
                "pageSize": 100  # Maximum allowed page size
            }
            
            all_records = []
            
            # Keep fetching pages until we have all records
            while True:
                # Apply rate limiting
                time.sleep(self.rate_limit)
                
                # Make the API request
                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code != 200:
                    logger.error(f"Airtable API error: {response.status_code}")
                    return all_records
                    
                data = response.json()
                page_records = data.get('records', [])
                all_records.extend(page_records)
                
                # If there's an offset token, prepare for the next page
                offset = data.get('offset')
                if offset:
                    params['offset'] = offset
                    logger.info(f"Found {len(page_records)} records, fetching next page...")
                else:
                    # No more pages
                    break
            
            logger.info(f"Found {len(all_records)} matching Airtable records")
            
            return all_records
        except Exception as e:
            logger.error(f"Error finding matching records: {e}")
            return []
    
    def extract_frame_number(self, frame_name: str) -> int:
        """Extract the frame number from a filename."""
        match = re.search(r'frame_0*(\d+)\.', frame_name)
        if match:
            return int(match.group(1))
        return 0
    
    def upload_image_to_airtable(self, record_id: str, image_path: str) -> bool:
        """
        Upload an image to an Airtable record.
        """
        try:
            frame_name = os.path.basename(image_path)
            logger.info(f"Uploading image {frame_name} to record {record_id}")
            
            # Load and process the image
            img = Image.open(image_path)
            img_format = os.path.splitext(image_path)[1].lower()[1:]
            if img_format == 'jpg':
                img_format = 'jpeg'
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format=img_format.upper())
            base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Prepare the update data - FIX: Use only content_type, not type
            mime_type = f"image/{img_format}"
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
            
            # Apply rate limiting
            time.sleep(self.rate_limit)
            
            # Make the API request
            response = requests.patch(
                f"{self.base_url}/{record_id}",
                headers=self.headers,
                json=update_data
            )
            
            if response.status_code != 200:
                logger.error(f"Error uploading image: status {response.status_code}")
                logger.error(f"Response: {response.text[:200]}")  # Log just the beginning of the response
                return False
            
            logger.info(f"Successfully uploaded {frame_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            return False
    
    def get_test_frames(self, folder_path: str, count: int = 3) -> List[str]:
        """
        Get a specific number of test frames from a folder.
        
        Args:
            folder_path: Path to the folder containing frames
            count: Number of frames to get
            
        Returns:
            List of frame paths
        """
        try:
            # Get all frames
            frame_pattern = os.path.join(folder_path, "*.jpg")
            all_frames = glob.glob(frame_pattern)
            
            # Sort numerically
            all_frames.sort(key=lambda path: self.extract_frame_number(os.path.basename(path)))
            
            # Get the first 'count' frames, or all if less
            test_frames = all_frames[:min(count, len(all_frames))]
            
            logger.info(f"Selected {len(test_frames)} test frames from {len(all_frames)} total frames")
            
            return test_frames
        except Exception as e:
            logger.error(f"Error getting test frames: {e}")
            return []
    
    async def run_test_upload(self, folder_path: str, count: int = 3) -> Dict[str, Any]:
        """
        Run a test upload with a few frames.
        """
        try:
            logger.info(f"Starting test upload from folder: {folder_path}")
            
            # Get test frames
            test_frames = self.get_test_frames(folder_path, count)
            if not test_frames:
                logger.error("No test frames found")
                return {"success": False}
            
            # Get frame IDs for Airtable lookup
            frame_ids = [os.path.basename(frame) for frame in test_frames]
            
            # Get matching Airtable records
            records = self.get_airtable_records_by_frame_id(frame_ids)
            if not records:
                logger.error("No matching Airtable records found")
                return {"success": False}
            
            # Create a mapping of frame filename to record ID
            record_map = {}
            for record in records:
                folder_path = record.get('fields', {}).get('FolderPath', '')
                if folder_path:
                    filename = os.path.basename(folder_path)
                    record_map[filename] = record.get('id')
            
            # Upload each frame
            successful = 0
            for frame_path in test_frames:
                frame_name = os.path.basename(frame_path)
                if frame_name in record_map:
                    record_id = record_map[frame_name]
                    print(f"Uploading {frame_name}...")
                    if self.upload_image_to_airtable(record_id, frame_path):
                        successful += 1
                        print(f"✅ Successfully uploaded {frame_name}")
                    else:
                        print(f"❌ Failed to upload {frame_name}")
                else:
                    print(f"❌ No matching record found for {frame_name}")
                
                # Small delay between uploads
                await asyncio.sleep(0.5)
            
            # Return results
            success = successful == len(test_frames)
            logger.info(f"Test upload complete: {successful}/{len(test_frames)} successful")
            
            return {
                "total_frames": len(test_frames),
                "successful": successful,
                "success": success
            }
            
        except Exception as e:
            logger.error(f"Error in test upload: {e}")
            return {"success": False, "error": str(e)}

async def main():
    """Main entry point for test script."""
    parser = argparse.ArgumentParser(
        description="Test uploading a few frames to Airtable"
    )
    
    parser.add_argument("--folder", 
                       type=str,
                       default=os.path.join(FRAME_BASE_DIR, "screen_recording_2025_02_20_at_12_14_43_pm"),
                       help="Folder containing frames to test with")
    parser.add_argument("--count", 
                       type=int,
                       default=3,
                       help="Number of frames to test (default: 3)")
    
    args = parser.parse_args()
    
    try:
        # Validate credentials
        if not AIRTABLE_TOKEN or not AIRTABLE_BASE_ID:
            logger.error("Missing Airtable credentials")
            return 1
        
        # Initialize uploader
        uploader = TestFrameUploader(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        
        # Run test
        print(f"\nRunning test upload for {args.count} frames from {args.folder}")
        print("------------------------------------------------------")
        
        result = await uploader.run_test_upload(args.folder, args.count)
        
        print("------------------------------------------------------")
        if result.get("success"):
            print(f"Test completed successfully: {result.get('successful')}/{result.get('total_frames')} frames uploaded")
        else:
            print("Test failed. See log for details.")
        
        return 0 if result.get("success") else 1
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 