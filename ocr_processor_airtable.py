#!/usr/bin/env python3
"""
OCRProcessorFromAirtable

A specialized version of the OCR processor that works with frame images directly from Airtable:
1. Retrieves frames from Airtable's FrameData attachment field
2. Processes frames in batches using OCR
3. Uses Gemini AI to filter and interpret OCR results
4. Updates Airtable with OCR data and sensitive content flags

This approach eliminates the need to match local files with Airtable records.
"""

import os
import sys
import json
import logging
import asyncio
import argparse
import csv
import datetime
import math
import glob
import time
import random
import requests
import io
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai

# Configure logging
os.makedirs("logs/ocr", exist_ok=True)  # Create log directory if it doesn't exist
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/ocr/ocr_processor_airtable_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("ocr_processor_airtable")

# Load environment variables
load_dotenv()
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', 'tblFrameAnalysis')

# Gemini API key rotation setup
GEMINI_API_KEYS = [
    os.environ.get('GEMINI_API_KEY_1'),
    os.environ.get('GEMINI_API_KEY_2'),
    os.environ.get('GEMINI_API_KEY_3'),
    os.environ.get('GEMINI_API_KEY_4'),
    os.environ.get('GEMINI_API_KEY_5'),
]
# Filter out None values
GEMINI_API_KEYS = [key for key in GEMINI_API_KEYS if key]
GEMINI_USE_KEY_ROTATION = os.environ.get('GEMINI_USE_KEY_ROTATION', 'true').lower() == 'true'
GEMINI_RATE_LIMIT = int(os.environ.get('GEMINI_RATE_LIMIT', '60'))
GEMINI_COOLDOWN_PERIOD = int(os.environ.get('GEMINI_COOLDOWN_PERIOD', '60'))

# Fallback to GEMINI_API_KEY if no rotation keys are found
if not GEMINI_API_KEYS:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    if GEMINI_API_KEY:
        GEMINI_API_KEYS = [GEMINI_API_KEY]
        GEMINI_USE_KEY_ROTATION = False
    else:
        logger.error("No Gemini API keys found. Set either GEMINI_API_KEY or GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.")
        sys.exit(1)

# Define output directory for OCR results
OCR_RESULTS_DIR = "output/ocr_results"

class APIKeyManager:
    """
    Manages multiple API keys with rotation and rate limiting.
    """
    
    def __init__(self, api_keys, rate_limit=60, cooldown_period=60):
        """
        Initialize the API key manager.
        
        Args:
            api_keys: List of API keys
            rate_limit: Number of requests allowed per key within the cooldown period
            cooldown_period: Cooldown period in seconds
        """
        self.api_keys = api_keys
        self.rate_limit = rate_limit
        self.cooldown_period = cooldown_period
        
        # Initialize usage tracking
        self.key_usage = {key: [] for key in api_keys}
        self.models = {}
        
        # Create models for each API key
        for key in api_keys:
            genai.configure(api_key=key)
            self.models[key] = genai.GenerativeModel('gemini-pro-vision')
            
        logger.info(f"Initialized {len(api_keys)} Gemini API keys with rotation")
        
    def get_available_key(self):
        """
        Get an available API key based on usage patterns.
        
        Returns:
            An available API key
        """
        current_time = time.time()
        
        # Clean up old usage records
        for key in self.api_keys:
            self.key_usage[key] = [t for t in self.key_usage[key] 
                                  if current_time - t < self.cooldown_period]
        
        # Find keys with usage below rate limit
        available_keys = [key for key in self.api_keys 
                          if len(self.key_usage[key]) < self.rate_limit]
        
        if not available_keys:
            # If all keys are at limit, wait for the one that will be available soonest
            next_available_time = min([min(self.key_usage[key]) + self.cooldown_period 
                                      for key in self.api_keys if self.key_usage[key]])
            wait_time = next_available_time - current_time
            logger.warning(f"All API keys at rate limit. Waiting {wait_time:.2f} seconds")
            time.sleep(max(0, wait_time))
            return self.get_available_key()
        
        # Choose the key with the fewest recent uses
        selected_key = min(available_keys, key=lambda k: len(self.key_usage[k]))
        
        # Record usage
        self.key_usage[selected_key].append(current_time)
        
        return selected_key
    
    def get_model(self, key=None):
        """
        Get the Gemini model for a specific key.
        
        Args:
            key: Optional specific key to use
            
        Returns:
            Gemini model instance
        """
        if key is None:
            key = self.get_available_key()
            
        return self.models[key], key

class AirtableConnector:
    """
    Class to interact with Airtable API.
    """
    
    def __init__(self, token, base_id, table_name):
        """
        Initialize the Airtable connector.
        
        Args:
            token: Airtable API token
            base_id: Airtable base ID
            table_name: Airtable table name
        """
        self.token = token
        self.base_id = base_id
        self.table_name = table_name
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.base_url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        
        # Rate limiting to avoid hitting Airtable API limits
        self.rate_limit_sleep = float(os.environ.get('AIRTABLE_RATE_LIMIT_SLEEP', '0.25'))
        
        logger.info(f"Initialized Airtable connector for {table_name} in base {base_id}")
    
    async def find_records_by_folder_name(self, folder_name: str) -> List[Dict[str, Any]]:
        """
        Find all Airtable records for a specific folder name.
        
        Args:
            folder_name: Name of the folder to search for
            
        Returns:
            List of matching Airtable records
        """
        try:
            logger.info(f"Finding Airtable records for folder: {folder_name}")
            
            # Use the FolderName field in Airtable to find matching records
            formula = f"{{FolderName}}='{folder_name}'"
            
            # Apply rate limiting
            await asyncio.sleep(self.rate_limit_sleep)
            
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params={
                    "filterByFormula": formula,
                    "sort[0][field]": "FrameID",  # Sort by FrameID
                    "sort[0][direction]": "asc"
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Airtable API error: {response.status_code} - {response.text}")
                return []
                
            data = response.json()
            records = data.get('records', [])
            
            logger.info(f"Found {len(records)} Airtable records for folder {folder_name}")
            
            return records
        except Exception as e:
            logger.error(f"Error finding records for folder {folder_name}: {e}")
            return []
    
    async def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single Airtable record by ID.
        
        Args:
            record_id: Airtable record ID
            
        Returns:
            Record dictionary or None if not found
        """
        try:
            logger.debug(f"Getting Airtable record: {record_id}")
            
            # Apply rate limiting
            await asyncio.sleep(self.rate_limit_sleep)
            
            response = requests.get(
                f"{self.base_url}/{record_id}",
                headers=self.headers
            )
            
            if response.status_code != 200:
                logger.error(f"Airtable API error: {response.status_code} - {response.text}")
                return None
                
            return response.json()
        except Exception as e:
            logger.error(f"Error getting Airtable record {record_id}: {e}")
            return None
    
    async def update_record(self, record_id: str, fields: Dict[str, Any]) -> bool:
        """
        Update an Airtable record.
        
        Args:
            record_id: Airtable record ID
            fields: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Updating Airtable record: {record_id}")
            
            # Apply rate limiting
            await asyncio.sleep(self.rate_limit_sleep)
            
            # Prepare the update payload
            update_data = {
                "fields": fields
            }
            
            response = requests.patch(
                f"{self.base_url}/{record_id}",
                headers=self.headers,
                json=update_data
            )
            
            if response.status_code != 200:
                logger.error(f"Airtable API error: {response.status_code} - {response.text}")
                return False
                
            logger.info(f"Successfully updated Airtable record: {record_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating Airtable record {record_id}: {e}")
            return False
    
    async def download_attachment(self, attachment_url: str) -> Optional[bytes]:
        """
        Download an attachment from Airtable.
        
        Args:
            attachment_url: URL of the attachment
            
        Returns:
            Attachment data as bytes or None if failed
        """
        try:
            logger.debug(f"Downloading attachment: {attachment_url}")
            
            # Apply rate limiting
            await asyncio.sleep(self.rate_limit_sleep)
            
            # Use the same authorization header
            response = requests.get(
                attachment_url,
                headers={"Authorization": self.headers["Authorization"]}
            )
            
            if response.status_code != 200:
                logger.error(f"Attachment download error: {response.status_code}")
                return None
                
            return response.content
        except Exception as e:
            logger.error(f"Error downloading attachment: {e}")
            return None

class OCRProcessorFromAirtable:
    """
    Class to handle the OCR processing workflow using frames from Airtable.
    """
    
    def __init__(self, batch_size=10):
        """
        Initialize the OCR processor.
        
        Args:
            batch_size: Number of frames to process in each batch
        """
        self.batch_size = batch_size
        self.airtable = AirtableConnector(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        
        # Set up API key manager for Gemini
        self.api_key_manager = APIKeyManager(
            GEMINI_API_KEYS,
            rate_limit=GEMINI_RATE_LIMIT,
            cooldown_period=GEMINI_COOLDOWN_PERIOD
        )
        
        # Initialize Tesseract OCR
        from pytesseract import pytesseract
        self.pytesseract = pytesseract
        
        # Ensure OCR results directory exists
        os.makedirs(OCR_RESULTS_DIR, exist_ok=True)
        
    async def extract_text_from_image(self, image_data: bytes) -> str:
        """
        Extract text from an image using OCR.
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            Extracted text
        """
        try:
            # Convert bytes to PIL Image
            img = Image.open(io.BytesIO(image_data))
            
            # Use Tesseract to extract text
            ocr_text = await asyncio.to_thread(
                self.pytesseract.image_to_string,
                img,
                lang='eng',
                config='--psm 6'
            )
            
            return ocr_text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return ""
    
    async def get_folders_chronologically(self) -> List[str]:
        """
        Get unique folder names from Airtable sorted chronologically.
        
        Returns:
            List of folder names
        """
        try:
            logger.info("Getting unique folders from Airtable")
            
            # Apply rate limiting
            await asyncio.sleep(self.airtable.rate_limit_sleep)
            
            # Get all records
            response = requests.get(
                self.airtable.base_url,
                headers=self.airtable.headers,
                params={
                    "fields[]": "FolderName",
                    "maxRecords": 10000  # Adjust as needed
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Airtable API error: {response.status_code} - {response.text}")
                return []
                
            data = response.json()
            records = data.get('records', [])
            
            # Extract unique folder names
            folders = set()
            for record in records:
                folder_name = record.get('fields', {}).get('FolderName')
                if folder_name:
                    folders.add(folder_name)
            
            # Sort folders chronologically by date in the name
            sorted_folders = sorted(list(folders), key=lambda x: x.split('_')[2:5])
            
            logger.info(f"Found {len(sorted_folders)} unique folders")
            
            return sorted_folders
        except Exception as e:
            logger.error(f"Error getting folders: {e}")
            return []
    
    async def process_frame(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single frame from Airtable with OCR.
        
        Args:
            record: Airtable record
            
        Returns:
            Dictionary with OCR results and frame info
        """
        try:
            record_id = record.get('id')
            fields = record.get('fields', {})
            
            frame_id = fields.get('FrameID', '')
            folder_name = fields.get('FolderName', '')
            summary = fields.get('Summary', '')
            
            logger.info(f"Processing frame: {frame_id}")
            
            # Check if the frame has an attachment
            attachments = fields.get('FrameData', [])
            if not attachments:
                logger.warning(f"No attachment found for frame {frame_id}")
                return {
                    "record_id": record_id,
                    "frame_id": frame_id,
                    "success": False,
                    "error": "No attachment"
                }
            
            # Get the first attachment
            attachment = attachments[0]
            attachment_url = attachment.get('url')
            
            if not attachment_url:
                logger.warning(f"No attachment URL found for frame {frame_id}")
                return {
                    "record_id": record_id,
                    "frame_id": frame_id,
                    "success": False,
                    "error": "No attachment URL"
                }
            
            # Download the attachment
            image_data = await self.airtable.download_attachment(attachment_url)
            
            if not image_data:
                logger.error(f"Failed to download attachment for frame {frame_id}")
                return {
                    "record_id": record_id,
                    "frame_id": frame_id,
                    "success": False,
                    "error": "Failed to download attachment"
                }
            
            # Extract text using OCR
            ocr_text = await self.extract_text_from_image(image_data)
            
            return {
                "record_id": record_id,
                "frame_id": frame_id,
                "folder_name": folder_name,
                "summary": summary,
                "ocr_text": ocr_text,
                "image_data": image_data,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            return {
                "record_id": record.get('id', ''),
                "frame_id": record.get('fields', {}).get('FrameID', ''),
                "success": False,
                "error": str(e)
            }
    
    async def filter_ocr_with_gemini_batch(self, sub_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a sub-batch of frames with a single Gemini API key.
        
        Args:
            sub_batch: List of frames with OCR results and image data
            
        Returns:
            List of processed results
        """
        try:
            if not sub_batch:
                return []
                
            # Get an available model
            model, key = self.api_key_manager.get_model()
            logger.info(f"Processing {len(sub_batch)} frames with API key: {key[:8]}...")
            
            # Process each frame with Gemini
            results = []
            for frame in sub_batch:
                if not frame["success"]:
                    results.append({
                        "filtered_text": "No readable text",
                        "contains_sensitive_info": False,
                        "processing_error": True
                    })
                    continue
                    
                try:
                    # Create image from bytes
                    image = Image.open(io.BytesIO(frame["image_data"]))
                    
                    prompt = f"""
                    Analyze this screen capture with the OCR text and frame summary.
                    
                    OCR Text: {frame["ocr_text"]}
                    
                    Frame Summary: {frame["summary"]}
                    
                    Your task:
                    1. Extract only the meaningful text that was actually on the screen
                    2. Ignore garbled text, OCR errors, and random artifacts
                    3. Determine if the frame contains sensitive information
                    
                    Respond in JSON format:
                    {{
                        "filtered_text": "The cleaned, meaningful text from the screen (or 'No readable text' if none found)",
                        "contains_sensitive_info": true/false,
                        "sensitive_content_types": ["password", "api_key", "personal_info", etc] (only if sensitive info detected)
                    }}
                    """
                    
                    response = await asyncio.to_thread(
                        model.generate_content,
                        [prompt, image]
                    )
                    
                    # Parse the response
                    text = response.text
                    # Extract JSON part
                    if "```json" in text:
                        json_str = text.split("```json")[1].split("```")[0].strip()
                    elif "```" in text:
                        json_str = text.split("```")[1].strip()
                    else:
                        json_str = text.strip()
                    
                    result = json.loads(json_str)
                    
                    # Ensure "No readable text" is used when appropriate
                    if not result.get("filtered_text") or result.get("filtered_text").strip() == "":
                        result["filtered_text"] = "No readable text"
                        
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"Error processing frame {frame['frame_id']} with Gemini: {e}")
                    results.append({
                        "filtered_text": "No readable text",
                        "contains_sensitive_info": False,
                        "processing_error": True
                    })
                    
                # Small delay between frames to avoid rate limits
                await asyncio.sleep(0.5)
                    
            return results
            
        except Exception as e:
            logger.error(f"Error in filter_ocr_with_gemini_batch: {e}")
            return [{"filtered_text": "No readable text", "contains_sensitive_info": False, "processing_error": True}] * len(sub_batch)
    
    async def filter_ocr_with_gemini(self, frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter OCR results using Gemini to extract meaningful text and detect sensitive content.
        Distributes the processing across multiple API keys for efficiency.
        
        Args:
            frames: List of frames with OCR results and image data
            
        Returns:
            List of dictionaries with filtered OCR results and sensitivity flags
        """
        try:
            # Remove frames that failed OCR
            valid_frames = [f for f in frames if f["success"]]
            
            if not valid_frames:
                logger.warning("No valid frames to process with Gemini")
                return []
            
            # Determine how many API keys to use
            num_keys = min(len(GEMINI_API_KEYS), len(valid_frames))
            if not GEMINI_USE_KEY_ROTATION or num_keys <= 1:
                # Process all frames with a single API key
                return await self.filter_ocr_with_gemini_batch(valid_frames)
            
            # Split the frames into sub-batches based on available API keys
            items_per_key = math.ceil(len(valid_frames) / num_keys)
            sub_batches = []
            for i in range(0, len(valid_frames), items_per_key):
                sub_batches.append(valid_frames[i:i+items_per_key])
                
            logger.info(f"Splitting {len(valid_frames)} frames into {len(sub_batches)} sub-batches for parallel processing")
            
            # Process each sub-batch in parallel
            sub_batch_tasks = [self.filter_ocr_with_gemini_batch(batch) for batch in sub_batches]
            sub_batch_results = await asyncio.gather(*sub_batch_tasks)
            
            # Combine results from all sub-batches
            results = []
            for batch_result in sub_batch_results:
                results.extend(batch_result)
                
            return results
            
        except Exception as e:
            logger.error(f"Error in filter_ocr_with_gemini: {e}")
            return [{"filtered_text": "No readable text", "contains_sensitive_info": False, "processing_error": True}] * len(frames)
    
    async def update_airtable_with_ocr(self, frame: Dict[str, Any], ocr_result: Dict[str, Any]) -> bool:
        """
        Update Airtable record with OCR data and sensitivity flag.
        
        Args:
            frame: Frame information
            ocr_result: Filtered OCR data
            
        Returns:
            Boolean indicating success
        """
        try:
            record_id = frame["record_id"]
            frame_id = frame["frame_id"]
            
            # Prepare OCR data summary
            ocr_summary = {
                "processed_at": datetime.datetime.now().isoformat(),
                "status": "processed",
                "ocr_text": ocr_result.get("filtered_text", "No readable text"),
                "contains_sensitive_info": ocr_result.get("contains_sensitive_info", False),
                "sensitive_content_types": ocr_result.get("sensitive_content_types", [])
            }
            
            # Save OCR result as JSON file
            json_path = os.path.join(OCR_RESULTS_DIR, f"{frame_id.replace('.jpg', '')}.json")
            
            with open(json_path, 'w') as f:
                json.dump({
                    "frame_id": frame_id,
                    "record_id": record_id,
                    "folder_name": frame.get("folder_name", ""),
                    "ocr_data": ocr_summary,
                    "processed_at": datetime.datetime.now().isoformat()
                }, f, indent=2)
            
            logger.info(f"Saved OCR result to {json_path}")
            
            # Update Airtable record
            update_data = {
                "OCRData": json.dumps(ocr_summary),
                "Flagged": ocr_result.get("contains_sensitive_info", False)
            }
            
            success = await self.airtable.update_record(record_id, update_data)
            if success:
                logger.info(f"Updated Airtable record for {frame_id}, sensitive: {ocr_result.get('contains_sensitive_info', False)}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating Airtable for {frame.get('frame_id', '')}: {e}")
            return False
    
    async def process_batch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a batch of frame records.
        
        Args:
            records: List of Airtable records
            
        Returns:
            Dictionary with batch processing results
        """
        logger.info(f"Processing batch of {len(records)} records")
        
        # Step 1: Process OCR for all frames in batch
        frame_tasks = [self.process_frame(record) for record in records]
        frames = await asyncio.gather(*frame_tasks)
        
        # Step 2: Filter OCR results using Gemini
        filtered_results = await self.filter_ocr_with_gemini(frames)
        
        # Step 3: Update Airtable with results
        update_tasks = []
        for i, frame in enumerate(frames):
            if frame["success"] and i < len(filtered_results):
                update_tasks.append(self.update_airtable_with_ocr(frame, filtered_results[i]))
        
        # Wait for all updates to complete
        update_results = await asyncio.gather(*update_tasks)
        
        # Return results
        return {
            "total_frames": len(records),
            "successful_ocr": sum(1 for f in frames if f["success"]),
            "successful_updates": sum(1 for r in update_results if r)
        }
    
    async def process_folder(self, folder_name: str) -> Dict[str, Any]:
        """
        Process all frames in a folder.
        
        Args:
            folder_name: Folder name to process
            
        Returns:
            Dictionary with folder processing results
        """
        logger.info(f"Processing folder: {folder_name}")
        
        # Get all records for this folder
        records = await self.airtable.find_records_by_folder_name(folder_name)
        
        if not records:
            logger.warning(f"No records found for folder: {folder_name}")
            return {
                "folder": folder_name,
                "total_frames": 0,
                "batches_processed": 0,
                "successful_updates": 0
            }
        
        logger.info(f"Found {len(records)} records for folder {folder_name}")
        
        # Divide records into batches
        batches = [records[i:i+self.batch_size] for i in range(0, len(records), self.batch_size)]
        
        # Process each batch
        batch_results = []
        for i, batch in enumerate(batches):
            logger.info(f"Processing batch {i+1}/{len(batches)} with {len(batch)} records")
            result = await self.process_batch(batch)
            batch_results.append(result)
            
            # Optional: Add a small delay between batches
            if i < len(batches) - 1:
                await asyncio.sleep(1)
        
        # Aggregate results
        total_frames = sum(result.get("total_frames", 0) for result in batch_results)
        successful_ocr = sum(result.get("successful_ocr", 0) for result in batch_results)
        successful_updates = sum(result.get("successful_updates", 0) for result in batch_results)
        
        folder_result = {
            "folder": folder_name,
            "total_frames": total_frames,
            "batches_processed": len(batches),
            "successful_ocr": successful_ocr,
            "successful_updates": successful_updates
        }
        
        logger.info(f"Completed folder {folder_name}: {successful_updates}/{total_frames} frames updated")
        
        return folder_result
    
    async def process_all_folders(self, limit_folders: Optional[int] = None) -> Dict[str, Any]:
        """
        Process all folders in chronological order.
        
        Args:
            limit_folders: Optional limit on number of folders to process
            
        Returns:
            Dictionary with overall processing results
        """
        # Get all folders chronologically
        folders = await self.get_folders_chronologically()
        
        if limit_folders:
            folders = folders[:limit_folders]
            
        logger.info(f"Processing {len(folders)} folders chronologically")
        
        # Process each folder
        folder_results = []
        for folder in folders:
            result = await self.process_folder(folder)
            folder_results.append(result)
            
            # Save intermediate result after each folder
            summary_path = os.path.join(OCR_RESULTS_DIR, f"ocr_processing_{datetime.datetime.now().strftime('%Y%m%d')}.json")
            os.makedirs(os.path.dirname(summary_path), exist_ok=True)
            
            with open(summary_path, 'w') as f:
                json.dump({
                    "processing_time": datetime.datetime.now().isoformat(),
                    "folders_processed": len(folder_results),
                    "results": folder_results
                }, f, indent=2)
        
        # Create final summary
        total_frames = sum(result.get("total_frames", 0) for result in folder_results)
        successful_updates = sum(result.get("successful_updates", 0) for result in folder_results)
        
        logger.info(f"Completed all folders: {successful_updates}/{total_frames} frames processed and updated")
        
        return {
            "folders_processed": len(folders),
            "total_frames": total_frames,
            "successful_updates": successful_updates,
            "folder_results": folder_results
        }

async def main():
    """Main entry point for the OCR processor."""
    parser = argparse.ArgumentParser(
        description="OCRProcessorFromAirtable - Process frames directly from Airtable attachments"
    )
    
    # Processing options
    parser.add_argument("--limit-folders", type=int, default=None,
                      help="Maximum number of folders to process")
    parser.add_argument("--batch-size", type=int, default=10,
                      help="Number of frames to process in each batch (default: 10)")
    parser.add_argument("--folder", type=str, default=None,
                      help="Process only a specific folder")
    parser.add_argument("--dry-run", action="store_true",
                      help="Perform a dry run without updating Airtable")
    
    args = parser.parse_args()
    
    try:
        # Initialize processor
        processor = OCRProcessorFromAirtable(batch_size=args.batch_size)
        
        if args.dry_run:
            # Just list folders and counts
            folders = await processor.get_folders_chronologically()
            
            if args.limit_folders:
                folders = folders[:args.limit_folders]
                
            logger.info(f"DRY RUN: Would process {len(folders)} folders")
            
            for folder in folders:
                records = await processor.airtable.find_records_by_folder_name(folder)
                logger.info(f"Folder {folder}: {len(records)} records")
            
            return 0
            
        # Process folders
        if args.folder:
            # Process just the specified folder
            result = await processor.process_folder(args.folder)
        else:
            # Process all folders (or limited number)
            result = await processor.process_all_folders(args.limit_folders)
        
        # Save final results
        final_output = os.path.join(OCR_RESULTS_DIR, f"ocr_processing_final_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(os.path.dirname(final_output), exist_ok=True)
        
        with open(final_output, 'w') as f:
            json.dump({
                "processing_time": datetime.datetime.now().isoformat(),
                "parameters": vars(args),
                "results": result
            }, f, indent=2)
            
        logger.info(f"Processing complete. Final results saved to {final_output}")
        return 0
    
    except Exception as e:
        logger.error(f"Error in OCR processing: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 