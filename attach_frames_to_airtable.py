#!/usr/bin/env python3
"""
Script to upload frame images to their corresponding Airtable records.

This script:
1. Scans folders of screen recording frames
2. Finds matching Airtable records by FolderName 
3. Sorts frames numerically
4. Uploads each image to the 'FrameData' attachment field in Airtable

This ensures all frame images are directly accessible in Airtable for later processing.
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
import signal

# Configure logging
os.makedirs("logs/airtable", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/airtable/frame_upload_{time.strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("frame_uploader")

# Load environment variables
load_dotenv()
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', 'tblFrameAnalysis')
FRAME_BASE_DIR = os.environ.get('FRAME_BASE_DIR', '/home/jason/Videos/screenRecordings')

# Rate limiting for Airtable API
RATE_LIMIT_SLEEP = float(os.environ.get('AIRTABLE_RATE_LIMIT_SLEEP', '0.25'))
MAX_UPLOAD_SIZE = 1024 * 1024 * 2  # Default max 2MB per file for attachments

# Add a signal handler function after the imports section
def handle_interrupt(signum, frame):
    """Handle interrupt signal (Ctrl+C) gracefully and clean up the console."""
    print("\n\nProcess interrupted by user. Cleaning up...")
    # Print a few newlines to clear any partial output
    print("\n\n")
    sys.exit(1)

# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, handle_interrupt)

class AirtableFrameUploader:
    """
    Class to handle uploading frame images to Airtable.
    """

    def __init__(self, token, base_id, table_name, rate_limit=RATE_LIMIT_SLEEP):
        """
        Initialize the uploader.
        
        Args:
            token: Airtable API token
            base_id: Airtable base ID
            table_name: Airtable table name
            rate_limit: Sleep time between API calls to avoid rate limits
        """
        self.token = token
        self.base_id = base_id
        self.table_name = table_name
        self.rate_limit = rate_limit
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.base_url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        
        logger.info(f"Initialized Airtable uploader for {table_name} in base {base_id}")
        
    def find_records_by_folder_name(self, folder_name: str) -> List[Dict[str, Any]]:
        """
        Find all Airtable records for a specific folder name.
        Handles pagination to retrieve all matching records.
        
        Args:
            folder_name: Name of the folder to search for
            
        Returns:
            List of matching Airtable records
        """
        try:
            logger.info(f"Finding Airtable records for folder: {folder_name}")
            
            # This pattern is used to match the beginning part of FolderPath
            folder_path_pattern = f"/home/jason/Videos/screenRecordings/{folder_name}"
            
            # Use SEARCH in Airtable formula to match the beginning of FolderPath
            formula = f"SEARCH('{folder_path_pattern}', {{FolderPath}}) = 1"
            
            # Parameters for the first request
            params = {
                "filterByFormula": formula,
                "sort[0][field]": "FrameID",  # Sort by FrameID
                "sort[0][direction]": "asc",
                "pageSize": 100  # Maximum allowed page size
            }
            
            all_records = []
            
            # Keep fetching pages until we have all records
            while True:
                # Apply rate limiting
                time.sleep(self.rate_limit)
                
                # Make API request
                response = requests.get(
                    self.base_url,
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code != 200:
                    logger.error(f"Airtable API error: {response.status_code} - {response.text}")
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
            
            logger.info(f"Found {len(all_records)} Airtable records for folder {folder_name}")
            
            return all_records
        except Exception as e:
            logger.error(f"Error finding records for folder {folder_name}: {e}")
            return []
    
    def extract_frame_number(self, frame_name: str) -> int:
        """
        Extract the frame number from the frame filename.
        
        Args:
            frame_name: Name of the frame file (e.g., 'frame_000123.jpg')
            
        Returns:
            Frame number as an integer
        """
        match = re.search(r'frame_0*(\d+)\.', frame_name)
        if match:
            return int(match.group(1))
        return 0
    
    def get_frames_from_folder(self, folder_path: str, pattern: str = "*.jpg") -> List[str]:
        """
        Get all frame files from a folder and sort them numerically.
        
        Args:
            folder_path: Path to the folder containing frames
            pattern: Glob pattern to match frame files
            
        Returns:
            List of frame paths sorted numerically
        """
        try:
            # Get all frame files
            frame_pattern = os.path.join(folder_path, pattern)
            frames = glob.glob(frame_pattern)
            
            # Sort frames numerically by extracting frame number
            frames.sort(key=lambda path: self.extract_frame_number(os.path.basename(path)))
            
            logger.info(f"Found {len(frames)} frames in folder {os.path.basename(folder_path)}")
            
            return frames
        except Exception as e:
            logger.error(f"Error getting frames from folder {folder_path}: {e}")
            return []
    
    def resize_image_if_needed(self, img, max_size=MAX_UPLOAD_SIZE):
        """
        Resize an image if it's too large for Airtable.
        
        Args:
            img: PIL Image object
            max_size: Maximum allowed file size in bytes
            
        Returns:
            PIL Image resized if necessary
        """
        # Create a temporary buffer to check size
        buffer = io.BytesIO()
        img.save(buffer, format=img.format or 'JPEG')
        size = buffer.getbuffer().nbytes
        
        if size <= max_size:
            return img
        
        # Need to resize - calculate new dimensions
        width, height = img.size
        scale_factor = 0.9  # Reduce by 10% each iteration
        
        while size > max_size:
            width = int(width * scale_factor)
            height = int(height * scale_factor)
            img_resized = img.resize((width, height), Image.LANCZOS)
            
            buffer = io.BytesIO()
            img_resized.save(buffer, format=img.format or 'JPEG')
            size = buffer.getbuffer().nbytes
            
            img = img_resized
            
        logger.info(f"Resized image to {width}x{height} to meet Airtable size limits")
        return img
    
    def upload_frame_to_airtable(self, record_id: str, frame_path: str, current: int = None, total: int = None) -> bool:
        """
        Upload a frame image to an Airtable record's FrameData field.
        
        Args:
            record_id: Airtable record ID
            frame_path: Path to the frame image file
            current: Current frame number for progress reporting
            total: Total frames for progress reporting
            
        Returns:
            True if upload was successful, False otherwise
        """
        try:
            frame_name = os.path.basename(frame_path)
            
            # Create progress display if current and total are provided
            if current is not None and total is not None:
                percent = (current / total) * 100
                
                # Create a progress bar
                bar_length = 30
                filled_length = int(bar_length * current // total)
                bar = '█' * filled_length + '-' * (bar_length - filled_length)
                
                # Print progress on the same line - keep it very minimal
                print(f"\r[{current}/{total} - {percent:.1f}%] Frame: {frame_name}", end="", flush=True)
            else:
                logger.info(f"Uploading frame {frame_name} to record {record_id}")
            
            # Process the image without logging binary data
            try:
                # Load the image and get its format
                img = Image.open(frame_path)
                img_format = os.path.splitext(frame_path)[1].lower()[1:]  # Remove the dot
                if img_format == 'jpg':
                    img_format = 'jpeg'  # PIL uses 'jpeg' not 'jpg'
                    
                # Resize if needed to meet Airtable size limits
                img = self.resize_image_if_needed(img)
                
                # Convert image to base64 without logging
                buffer = io.BytesIO()
                img.save(buffer, format=img_format.upper())
                # Don't log or print the base64 data anywhere
                base64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                # Prepare the update payload - FIX: Use only content_type, not type
                mime_type = f"image/{img_format}"
                update_data = {
                    "fields": {
                        "FrameData": [
                            {
                                "filename": frame_name,
                                "content_type": mime_type,
                                "data": base64_data  # This should never be logged
                            }
                        ]
                    }
                }
            except Exception as e:
                logger.error(f"Error preparing image {frame_name}: {e}")
                return False
            
            # Apply rate limiting
            time.sleep(self.rate_limit)
            
            # Update the record - don't log the full response
            try:
                response = requests.patch(
                    f"{self.base_url}/{record_id}",
                    headers=self.headers,
                    json=update_data
                )
                
                status_code = response.status_code
                if status_code != 200:
                    # Only log the status code, not the full response text which may contain binary data
                    logger.error(f"Error uploading frame to Airtable: status code {status_code}")
                    logger.error(f"Response: {response.text[:200]}")  # Log just the beginning of the response
                    return False
            except Exception as e:
                logger.error(f"Network error uploading frame {frame_name}: {e}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error uploading frame {frame_path} to record {record_id}: {e}")
            return False
    
    def match_frames_to_records(self, frames: List[str], records: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
        """
        Match frame files to Airtable records based on the frame filename in FolderPath.
        
        Args:
            frames: List of frame file paths
            records: List of Airtable records
            
        Returns:
            List of (record_id, frame_path) tuples
        """
        # Extract frame number from FolderPath
        def extract_frame_number_from_path(path):
            if not path:
                return 0
            filename = os.path.basename(path)
            match = re.search(r'frame_0*(\d+)\.', filename)
            if match:
                return int(match.group(1))
            return 0
        
        # Create a map of frame numbers to records using the FolderPath field
        record_map = {}
        for record in records:
            folder_path = record.get('fields', {}).get('FolderPath', '')
            frame_number = extract_frame_number_from_path(folder_path)
            if frame_number > 0:
                record_map[frame_number] = record.get('id')
        
        # Match frames to records by frame number
        matches = []
        for frame_path in frames:
            frame_name = os.path.basename(frame_path)
            frame_number = self.extract_frame_number(frame_name)
            
            if frame_number in record_map:
                matches.append((record_map[frame_number], frame_path))
            else:
                logger.warning(f"No matching record found for frame {frame_name} (number: {frame_number})")
        
        logger.info(f"Matched {len(matches)} frames to Airtable records")
        return matches
    
    async def process_folder(self, folder_path: str, pattern: str = "*.jpg") -> Dict[str, Any]:
        """
        Process all frames in a folder and upload them to Airtable.
        
        Args:
            folder_path: Path to the folder containing frames
            pattern: Glob pattern to match frame files
            
        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Processing folder: {folder_path}")
            
            # Get the folder name
            folder_name = os.path.basename(folder_path)
            
            # Get all frames in the folder
            frames = self.get_frames_from_folder(folder_path, pattern)
            if not frames:
                logger.warning(f"No frames found in folder: {folder_path}")
                return {
                    "folder": folder_path,
                    "total_frames": 0,
                    "frames_uploaded": 0,
                    "success": False
                }
            
            # Sort frames correctly by frame number
            frames.sort(key=lambda path: self.extract_frame_number(os.path.basename(path)))
            
            # Find Airtable records for this folder
            records = self.find_records_by_folder_name(folder_name)
            if not records:
                logger.warning(f"No Airtable records found for folder: {folder_name}")
                return {
                    "folder": folder_path,
                    "total_frames": len(frames),
                    "frames_uploaded": 0,
                    "success": False
                }
            
            # Match frames to records
            matches = self.match_frames_to_records(frames, records)
            if not matches:
                logger.warning(f"No matches found between frames and Airtable records for folder: {folder_name}")
                return {
                    "folder": folder_path,
                    "total_frames": len(frames),
                    "frames_matched": 0,
                    "frames_uploaded": 0,
                    "success": False
                }
            
            # Start upload with a clean line
            print(f"\nFolder: {folder_name} - Uploading {len(matches)}/{len(frames)} frames")
            
            successful_uploads = 0
            for i, (record_id, frame_path) in enumerate(matches, 1):
                if self.upload_frame_to_airtable(record_id, frame_path, i, len(matches)):
                    successful_uploads += 1
                
                # Small delay between uploads
                await asyncio.sleep(0.1)
            
            # Print newline after progress to ensure clean output
            print("\n")
            print(f"Completed: {successful_uploads}/{len(matches)} frames uploaded successfully")
            
            # Return results
            success = successful_uploads == len(matches)
            logger.info(f"Folder {folder_name}: Uploaded {successful_uploads}/{len(matches)} frames")
            
            return {
                "folder": folder_path,
                "total_frames": len(frames),
                "frames_matched": len(matches),
                "frames_uploaded": successful_uploads,
                "success": success
            }
            
        except Exception as e:
            logger.error(f"Error processing folder {folder_path}: {e}")
            return {
                "folder": folder_path,
                "total_frames": 0,
                "frames_uploaded": 0,
                "success": False,
                "error": str(e)
            }
    
    async def process_all_folders(self, base_dir: str, limit_folders: Optional[int] = None) -> Dict[str, Any]:
        """
        Process all folders and upload frames to Airtable.
        
        Args:
            base_dir: Base directory containing screen recording folders
            limit_folders: Optional limit on number of folders to process
            
        Returns:
            Dictionary with overall processing results
        """
        try:
            # Find all screen recording folders
            folder_pattern = os.path.join(base_dir, "screen_recording_*")
            folders = glob.glob(folder_pattern)
            
            # Sort folders chronologically by date in folder name
            folders.sort(key=lambda path: os.path.basename(path).split('_')[2:5])
            
            if limit_folders:
                folders = folders[:limit_folders]
                
            logger.info(f"Found {len(folders)} folders to process")
            
            # Process each folder with overall progress
            folder_results = []
            print(f"\nProcessing {len(folders)} folders:")
            for i, folder in enumerate(folders, 1):
                folder_name = os.path.basename(folder)
                print(f"\nFolder {i}/{len(folders)}: {folder_name}")
                
                result = await self.process_folder(folder)
                folder_results.append(result)
                
                # Print summary after each folder
                success_str = "✅" if result.get("success", False) else "❌"
                print(f"{success_str} Uploaded {result.get('frames_uploaded', 0)}/{result.get('total_frames', 0)} frames")
                
                # Save intermediate progress
                summary_path = f"logs/airtable/upload_progress_{time.strftime('%Y%m%d')}.json"
                with open(summary_path, 'w') as f:
                    json.dump({
                        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "folders_processed": i,
                        "folders_total": len(folders),
                        "current_progress": {
                            "folders_completed": i,
                            "folders_total": len(folders),
                            "percent_complete": (i / len(folders)) * 100
                        },
                        "results": folder_results
                    }, f, indent=2)
            
            # Compute totals
            total_frames = sum(result["total_frames"] for result in folder_results)
            total_uploaded = sum(result["frames_uploaded"] for result in folder_results)
            
            # Print final summary
            print(f"\n====== Upload Complete ======")
            print(f"Folders processed: {len(folders)}")
            print(f"Total frames: {total_frames}")
            print(f"Frames uploaded: {total_uploaded} ({(total_uploaded/total_frames)*100:.1f}%)")
            print(f"==============================\n")
            
            logger.info(f"Completed processing {len(folders)} folders")
            logger.info(f"Total frames: {total_frames}, Uploaded: {total_uploaded}")
            
            return {
                "folders_processed": len(folders),
                "total_frames": total_frames,
                "frames_uploaded": total_uploaded,
                "folder_results": folder_results
            }
            
        except Exception as e:
            logger.error(f"Error processing folders: {e}")
            return {
                "error": str(e),
                "folders_processed": 0,
                "total_frames": 0,
                "frames_uploaded": 0
            }

async def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Upload frame images to their corresponding Airtable records"
    )
    
    parser.add_argument("--base-dir", 
                       default=FRAME_BASE_DIR,
                       help="Base directory containing screen recording folders")
    parser.add_argument("--limit-folders", 
                       type=int, 
                       default=None,
                       help="Maximum number of folders to process")
    parser.add_argument("--dry-run", 
                       action="store_true",
                       help="Perform a dry run without uploading to Airtable")
    
    args = parser.parse_args()
    
    try:
        # Validate Airtable credentials
        if not AIRTABLE_TOKEN or not AIRTABLE_BASE_ID or not AIRTABLE_TABLE_NAME:
            logger.error("Missing Airtable credentials in environment variables")
            return 1
        
        # Initialize uploader
        uploader = AirtableFrameUploader(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        
        if args.dry_run:
            logger.info("DRY RUN MODE - No files will be uploaded to Airtable")
            
            # Just find folders and count frames
            folder_pattern = os.path.join(args.base_dir, "screen_recording_*")
            folders = glob.glob(folder_pattern)
            folders.sort(key=lambda path: os.path.basename(path).split('_')[2:5])
            
            if args.limit_folders:
                folders = folders[:args.limit_folders]
                
            logger.info(f"Found {len(folders)} folders to process")
            
            total_frames = 0
            for folder in folders:
                frames = uploader.get_frames_from_folder(folder)
                total_frames += len(frames)
                
                folder_name = os.path.basename(folder)
                records = uploader.find_records_by_folder_name(folder_name)
                
                logger.info(f"Folder {folder_name}: {len(frames)} frames, {len(records)} Airtable records")
            
            logger.info(f"Total frames to upload: {total_frames}")
            return 0
        
        # Process all folders
        results = await uploader.process_all_folders(args.base_dir, args.limit_folders)
        
        # Save final results
        final_output = f"logs/airtable/upload_final_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(final_output, 'w') as f:
            json.dump({
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
                "parameters": vars(args),
                "results": results
            }, f, indent=2)
            
        logger.info(f"Processing complete. Final results saved to {final_output}")
        
        # Return success if all frames were uploaded
        return 0 if results["frames_uploaded"] == results["total_frames"] else 1
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 