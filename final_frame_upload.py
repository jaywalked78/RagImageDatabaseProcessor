#!/usr/bin/env python3
"""
Final Frame Upload Script

This script uploads frame images to Airtable with the correct format.
It fixes the attachment format issues and properly handles 
pagination when fetching records.
"""

import os
import sys
import re
import glob
import logging
import base64
import json
import time
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
        logging.FileHandler(f"logs/airtable/final_upload_{time.strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("frame_uploader")

class AirtableUploader:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID", "appewal2KEO5B02KV")
        self.table_name = os.getenv("AIRTABLE_TABLE_NAME", "tblFrameAnalysis")
        
        # Set up API endpoints and headers
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_name}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Rate limiting (milliseconds)
        self.rate_limit = 0.2  # 200ms between requests
        
        # Check for required credentials
        if not self.api_key:
            logger.error("AIRTABLE_API_KEY environment variable is required")
            sys.exit(1)
    
    def get_all_records_for_folder(self, folder_name: str) -> List[Dict[str, Any]]:
        """
        Get all records for a specific folder with pagination support.
        
        Args:
            folder_name: The folder name to search for
            
        Returns:
            List of matching Airtable records
        """
        folder_path_pattern = f"/home/jason/Videos/screenRecordings/{folder_name}"
        formula = f"SEARCH('{folder_path_pattern}', {{FolderPath}}) > 0"
        
        all_records = []
        offset = None
        
        while True:
            try:
                params = {
                    "filterByFormula": formula,
                    "maxRecords": 100
                }
                
                if offset:
                    params["offset"] = offset
                
                logger.info(f"Fetching records for folder: {folder_name}" + 
                           (f" (with offset: {offset})" if offset else ""))
                
                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code != 200:
                    logger.error(f"Error fetching records: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    return []
                
                data = response.json()
                records = data.get("records", [])
                all_records.extend(records)
                
                logger.info(f"Found {len(records)} records in this batch")
                
                # Check for more records
                offset = data.get("offset")
                if not offset:
                    break
                
                # Sleep to avoid rate limiting
                time.sleep(self.rate_limit)
                
            except Exception as e:
                logger.error(f"Error fetching records: {e}")
                return []
        
        logger.info(f"Total records found for folder {folder_name}: {len(all_records)}")
        return all_records
    
    def find_matching_record(self, records: List[Dict[str, Any]], frame_path: str) -> Optional[str]:
        """
        Find the record that matches a specific frame.
        
        Args:
            records: List of Airtable records
            frame_path: Path to the frame file
            
        Returns:
            Record ID if found, None otherwise
        """
        try:
            # Extract frame number from filename (e.g., frame_000123.jpg -> 123)
            frame_name = os.path.basename(frame_path)
            frame_match = re.search(r'frame_(\d+)\.jpg', frame_name)
            if not frame_match:
                logger.error(f"Could not extract frame number from {frame_name}")
                return None
            
            frame_number = frame_match.group(1)
            
            # Look for this frame number in the FolderPath field
            for record in records:
                folder_path = record.get("fields", {}).get("FolderPath", "")
                if f"frame_{frame_number}.jpg" in folder_path:
                    return record.get("id")
            
            return None
        except Exception as e:
            logger.error(f"Error finding matching record: {e}")
            return None
    
    def resize_image_if_needed(self, img: Image.Image, max_size: Tuple[int, int] = (1000, 1000)) -> Image.Image:
        """
        Resize the image if it's larger than max_size.
        
        Args:
            img: PIL Image object
            max_size: Maximum width and height
            
        Returns:
            Resized PIL Image object
        """
        width, height = img.size
        if width <= max_size[0] and height <= max_size[1]:
            return img
        
        # Calculate new dimensions while preserving aspect ratio
        if width > height:
            new_width = max_size[0]
            new_height = int(height * (max_size[0] / width))
        else:
            new_height = max_size[1]
            new_width = int(width * (max_size[1] / height))
        
        logger.info(f"Resizing image from {width}x{height} to {new_width}x{new_height}")
        return img.resize((new_width, new_height), Image.LANCZOS)
    
    def upload_frame(self, record_id: str, frame_path: str, current: int = None, total: int = None) -> bool:
        """
        Upload a frame image to an Airtable record.
        
        Args:
            record_id: Airtable record ID
            frame_path: Path to the frame image
            current: Current frame number for progress reporting
            total: Total frames for progress reporting
            
        Returns:
            True if successful, False otherwise
        """
        try:
            frame_name = os.path.basename(frame_path)
            
            # Create progress display
            if current is not None and total is not None:
                percent = (current / total) * 100
                bar_length = 30
                filled_length = int(bar_length * current // total)
                bar = '█' * filled_length + '-' * (bar_length - filled_length)
                print(f"\r[{bar}] {current}/{total} - {percent:.1f}% | Frame: {frame_name}", 
                      end="", flush=True)
            else:
                logger.info(f"Uploading frame {frame_name} to record {record_id}")
            
            # Load and process the image
            img = Image.open(frame_path)
            img_format = os.path.splitext(frame_path)[1].lower()[1:]
            if img_format == 'jpg':
                img_format = 'jpeg'  # PIL uses 'jpeg' not 'jpg'
            
            # Resize if needed
            img = self.resize_image_if_needed(img)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format=img_format.upper())
            base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Prepare the update data with CORRECT attachment format
            # Airtable expects: filename, content_type, and data (not type)
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
                logger.error(f"Error uploading frame to Airtable: status code {response.status_code}")
                logger.error(f"Response: {response.text[:200]}")  # Log just the beginning to avoid binary data
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error uploading frame {frame_path} to record {record_id}: {e}")
            return False
    
    def process_folder(self, folder_path: str, dry_run: bool = False, limit: int = None) -> None:
        """
        Process a folder of frame images.
        
        Args:
            folder_path: Path to the folder containing frames
            dry_run: If True, don't actually upload
            limit: Maximum number of frames to process
        """
        try:
            # Extract folder name from path
            folder_name = os.path.basename(folder_path)
            logger.info(f"Processing folder: {folder_name}")
            
            # Get all frame files in the folder
            frame_files = sorted(glob.glob(os.path.join(folder_path, "frame_*.jpg")))
            if not frame_files:
                logger.error(f"No frame files found in {folder_path}")
                return
            
            if limit:
                frame_files = frame_files[:limit]
            
            logger.info(f"Found {len(frame_files)} frame files")
            
            # Get all records for this folder
            records = self.get_all_records_for_folder(folder_name)
            if not records:
                logger.error(f"No records found for folder {folder_name}")
                return
            
            # Process each frame
            successful = 0
            for i, frame_path in enumerate(frame_files):
                # Find matching record
                record_id = self.find_matching_record(records, frame_path)
                if not record_id:
                    logger.error(f"No matching record found for {frame_path}")
                    continue
                
                # If dry run, just log
                if dry_run:
                    logger.info(f"DRY RUN: Would upload {frame_path} to record {record_id}")
                    successful += 1
                    continue
                
                # Upload the frame
                if self.upload_frame(record_id, frame_path, i + 1, len(frame_files)):
                    successful += 1
            
            print()  # Add newline after progress bar
            logger.info(f"Successfully processed {successful}/{len(frame_files)} frames for {folder_name}")
            
        except Exception as e:
            logger.error(f"Error processing folder {folder_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Upload frame images to Airtable")
    parser.add_argument("--folder", help="Path to folder with frames", default="/home/jason/Videos/screenRecordings")
    parser.add_argument("--folder-name", help="Name of specific folder to process")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually upload frames")
    parser.add_argument("--limit", type=int, help="Limit number of frames to process per folder")
    args = parser.parse_args()
    
    uploader = AirtableUploader()
    
    if args.folder_name:
        # Process specific folder
        folder_path = os.path.join(args.folder, args.folder_name)
        if not os.path.exists(folder_path):
            logger.error(f"Folder {folder_path} does not exist")
            return
        
        uploader.process_folder(folder_path, args.dry_run, args.limit)
    else:
        # Process all folders
        folders = sorted([d for d in os.listdir(args.folder) 
                          if os.path.isdir(os.path.join(args.folder, d)) 
                          and d.startswith("screen_recording_")])
        
        logger.info(f"Found {len(folders)} folders to process")
        
        for i, folder_name in enumerate(folders):
            logger.info(f"Processing folder {i+1}/{len(folders)}: {folder_name}")
            folder_path = os.path.join(args.folder, folder_name)
            uploader.process_folder(folder_path, args.dry_run, args.limit)

if __name__ == "__main__":
    main() 