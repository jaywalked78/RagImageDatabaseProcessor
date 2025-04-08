#!/usr/bin/env python3
"""
OCRProcessorAndUpsertToAirtable

A focused subprogram of DatabaseAdvancedTokenizer that only:
1. Runs OCR on frames chronologically from oldest to newest
2. Processes in batches of 10 frames
3. Filters OCR results through Gemini to extract meaningful text
4. Updates Airtable with OCR data and sensitive content flags

Does NOT perform:
- Text chunking
- Embedding generation
- Webhook sending

Use this script when you only need to update Airtable with OCR data.
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
        logging.FileHandler(f"logs/ocr/ocr_processor_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("ocr_processor")

# Load environment variables
load_dotenv()
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', 'tblFrameAnalysis')

# Gemini API key setup
# Try to get the individual API keys first
GEMINI_API_KEYS = []
for i in range(1, 6):
    key = os.environ.get(f'GEMINI_API_KEY_{i}')
    if key:
        GEMINI_API_KEYS.append(key)

# If no individual keys found, fall back to the main API key
if not GEMINI_API_KEYS:
    main_key = os.environ.get('GEMINI_API_KEY')
    if main_key:
        GEMINI_API_KEYS.append(main_key)
        logger.info(f"Using main GEMINI_API_KEY")
    else:
        logger.error(f"No Gemini API keys found. Please set GEMINI_API_KEY or GEMINI_API_KEY_1, etc. in your .env file")
        sys.exit(1)

# Configure Gemini
GEMINI_API_KEY = GEMINI_API_KEYS[0]  # Use the first key as default
genai.configure(api_key=GEMINI_API_KEY)
logger.info(f"Configured Gemini with {len(GEMINI_API_KEYS)} API key(s)")

# Define output directory for OCR results
OCR_RESULTS_DIR = "output/ocr_results"
os.makedirs(OCR_RESULTS_DIR, exist_ok=True)

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

class OCRProcessorAndUpsertToAirtable:
    """
    Class to handle the OCR processing and Airtable updating workflow.
    """
    
    def __init__(self, batch_size=10):
        """
        Initialize the OCR processor.
        
        Args:
            batch_size: Number of frames to process in each batch
        """
        self.batch_size = batch_size
        self.airtable = AirtableMetadataFinder(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        self.frame_processor = FrameProcessor()
        
        # Set up API key manager for Gemini
        self.api_key_manager = APIKeyManager(
            GEMINI_API_KEYS,
            rate_limit=GEMINI_RATE_LIMIT,
            cooldown_period=GEMINI_COOLDOWN_PERIOD
        )
        
        # Ensure OCR results directory exists
        os.makedirs(OCR_RESULTS_DIR, exist_ok=True)
        
    async def get_folders_chronologically(self, base_dir):
        """
        Get folders sorted chronologically based on folder name.
        
        Args:
            base_dir: Base directory containing screen recording folders
            
        Returns:
            List of folder paths sorted chronologically
        """
        folder_pattern = os.path.join(base_dir, "screen_recording_*")
        folders = glob.glob(folder_pattern)
        
        # Sort folders by date in the name (assuming format screen_recording_YYYY_MM_DD_*)
        folders.sort(key=lambda x: os.path.basename(x).split('_')[2:5])
        
        return folders
    
    async def get_frames_in_folder(self, folder_path, pattern="*.jpg"):
        """
        Get all frames in a folder that match the pattern.
        
        Args:
            folder_path: Path to the folder
            pattern: File pattern to match
            
        Returns:
            List of frame paths
        """
        frame_pattern = os.path.join(folder_path, pattern)
        frames = glob.glob(frame_pattern)
        frames.sort()  # Sort frames numerically
        
        return frames
    
    async def divide_into_batches(self, frames, batch_size=None):
        """
        Divide frames into batches of specified size.
        
        Args:
            frames: List of frame paths
            batch_size: Size of each batch (defaults to self.batch_size)
            
        Returns:
            List of batches, where each batch is a list of frame paths
        """
        if batch_size is None:
            batch_size = self.batch_size
            
        # Calculate number of batches (round up to account for remainder)
        num_batches = math.ceil(len(frames) / batch_size)
        
        batches = []
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min(start_idx + batch_size, len(frames))
            batches.append(frames[start_idx:end_idx])
            
        return batches
    
    async def process_frame_ocr(self, frame_path):
        """
        Process a single frame with OCR.
        
        Args:
            frame_path: Path to the frame image
            
        Returns:
            Dictionary with OCR results and frame info
        """
        try:
            # Load the image
            img = Image.open(frame_path)
            logger.info(f"Processing OCR for frame: {os.path.basename(frame_path)}")
            
            # Get OCR text using the frame processor
            ocr_result = await self.frame_processor.extract_text(img)
            
            return {
                "frame_path": frame_path,
                "ocr_text": ocr_result,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error processing OCR for {frame_path}: {e}")
            return {
                "frame_path": frame_path,
                "ocr_text": "",
                "success": False,
                "error": str(e)
            }
    
    async def get_airtable_summary(self, frame_path):
        """
        Get the summary field from Airtable for a frame.
        
        Args:
            frame_path: Path to the frame
            
        Returns:
            Summary text or empty string if not found
        """
        try:
            record = await self.airtable.find_record_by_frame_path(frame_path)
            if record and 'fields' in record:
                return record['fields'].get('Summary', '')
            return ''
        except Exception as e:
            logger.error(f"Error getting Airtable summary for {frame_path}: {e}")
            return ''
    
    async def filter_ocr_with_gemini_batch(self, sub_batch):
        """
        Process a sub-batch of frames with a single Gemini API key.
        
        Args:
            sub_batch: List of (frame_path, ocr_text, summary) tuples
            
        Returns:
            List of processed results
        """
        try:
            if not sub_batch:
                return []
                
            # Get an available model
            model, key = self.api_key_manager.get_model()
            logger.info(f"Processing {len(sub_batch)} frames with API key: {key[:8]}...")
            
            # Load images for the sub-batch
            images = []
            prompts = []
            
            for frame_path, ocr_text, summary in sub_batch:
                try:
                    images.append(Image.open(frame_path))
                    prompt = f"""
                    Analyze this screen capture with the OCR text and frame summary.
                    
                    OCR Text: {ocr_text}
                    
                    Frame Summary: {summary}
                    
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
                    prompts.append(prompt)
                except Exception as e:
                    logger.error(f"Error loading image {frame_path}: {e}")
                    images.append(None)
                    prompts.append(None)
            
            # Process each frame with Gemini
            results = []
            for i, (frame_path, ocr_text, summary) in enumerate(sub_batch):
                if images[i] is None or prompts[i] is None:
                    results.append({
                        "filtered_text": "No readable text",
                        "contains_sensitive_info": False,
                        "processing_error": True
                    })
                    continue
                    
                try:
                    response = await asyncio.to_thread(
                        model.generate_content,
                        [prompts[i], images[i]]
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
                    logger.error(f"Error processing frame {frame_path} with Gemini: {e}")
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
    
    async def filter_ocr_with_gemini(self, ocr_results, image_paths):
        """
        Filter OCR results using Gemini to extract meaningful text and detect sensitive content.
        Distributes the processing across multiple API keys for efficiency.
        
        Args:
            ocr_results: List of raw OCR text results
            image_paths: List of corresponding image paths
            
        Returns:
            List of dictionaries with filtered OCR results and sensitivity flags
        """
        try:
            # Collect Airtable summaries for each frame
            summary_tasks = [self.get_airtable_summary(path) for path in image_paths]
            summaries = await asyncio.gather(*summary_tasks)
            
            # Create a list of tuples with all the data needed for processing
            frame_data = list(zip(image_paths, ocr_results, summaries))
            
            # Determine how many API keys to use
            num_keys = min(len(GEMINI_API_KEYS), len(frame_data))
            if not GEMINI_USE_KEY_ROTATION or num_keys <= 1:
                # Process all frames with a single API key
                return await self.filter_ocr_with_gemini_batch(frame_data)
            
            # Split the frames into sub-batches based on available API keys
            items_per_key = math.ceil(len(frame_data) / num_keys)
            sub_batches = []
            for i in range(0, len(frame_data), items_per_key):
                sub_batches.append(frame_data[i:i+items_per_key])
                
            logger.info(f"Splitting {len(frame_data)} frames into {len(sub_batches)} sub-batches for parallel processing")
            
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
            return [{"filtered_text": "No readable text", "contains_sensitive_info": False, "processing_error": True}] * len(ocr_results)
    
    async def update_airtable_with_ocr(self, frame_path, ocr_data, sensitive_flag=False):
        """
        Update Airtable record with OCR data and sensitivity flag.
        
        Args:
            frame_path: Path to the frame
            ocr_data: Filtered OCR data to save
            sensitive_flag: Whether the frame contains sensitive information
            
        Returns:
            Boolean indicating success
        """
        try:
            # Find record in Airtable
            record = await self.airtable.find_record_by_frame_path(frame_path)
            if not record:
                logger.error(f"No Airtable record found for frame: {frame_path}")
                return False
            
            # Extract record ID
            airtable_id = record.get('id')
            
            # Prepare OCR data summary
            ocr_summary = {
                "processed_at": datetime.datetime.now().isoformat(),
                "status": "processed",
                "ocr_text": ocr_data.get("filtered_text", "No readable text"),
                "contains_sensitive_info": sensitive_flag,
                "sensitive_content_types": ocr_data.get("sensitive_content_types", [])
            }
            
            # Save OCR result as JSON file
            frame_name = os.path.basename(frame_path)
            frame_id = os.path.splitext(frame_name)[0]
            json_path = os.path.join(OCR_RESULTS_DIR, f"{frame_id}.json")
            
            with open(json_path, 'w') as f:
                json.dump({
                    "frame_path": frame_path,
                    "frame_name": frame_name,
                    "airtable_id": airtable_id,
                    "ocr_data": ocr_summary,
                    "processed_at": datetime.datetime.now().isoformat()
                }, f, indent=2)
            
            logger.info(f"Saved OCR result to {json_path}")
            
            # Update Airtable record
            update_data = {
                "OCRData": json.dumps(ocr_summary),
                "Flagged": sensitive_flag
            }
            
            self.airtable.update_record(airtable_id, update_data)
            logger.info(f"Updated Airtable record for {os.path.basename(frame_path)}, sensitive: {sensitive_flag}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Airtable for {frame_path}: {e}")
            return False
    
    async def process_batch(self, batch_frames):
        """
        Process a batch of frames through OCR, Gemini filtering, and Airtable update.
        
        Args:
            batch_frames: List of frame paths in the batch
            
        Returns:
            Dictionary with batch processing results
        """
        # Step 1: Process OCR for all frames in batch
        ocr_tasks = [self.process_frame_ocr(frame) for frame in batch_frames]
        ocr_results = await asyncio.gather(*ocr_tasks)
        
        # Step 2: Collect OCR text for successful frames
        successful_frames = []
        ocr_texts = []
        
        for result in ocr_results:
            if result["success"]:
                successful_frames.append(result["frame_path"])
                ocr_texts.append(result["ocr_text"])
        
        # Step 3: If we have successful frames, filter with Gemini
        if successful_frames:
            filtered_results = await self.filter_ocr_with_gemini(ocr_texts, successful_frames)
            
            # Step 4: Update Airtable for each frame
            update_tasks = []
            for i, frame_path in enumerate(successful_frames):
                if i < len(filtered_results):
                    frame_result = filtered_results[i]
                    sensitive_flag = frame_result.get("contains_sensitive_info", False)
                    
                    update_task = self.update_airtable_with_ocr(
                        frame_path, 
                        frame_result,
                        sensitive_flag
                    )
                    update_tasks.append(update_task)
                else:
                    logger.error(f"Missing result for frame {frame_path}")
            
            # Wait for all Airtable updates to complete
            update_results = await asyncio.gather(*update_tasks)
            
            # Return batch results
            return {
                "total_frames": len(batch_frames),
                "successful_ocr": len(successful_frames),
                "successful_updates": sum(1 for r in update_results if r),
                "filtered_results": filtered_results
            }
        else:
            logger.warning(f"No successful OCR results in batch of {len(batch_frames)} frames")
            return {
                "total_frames": len(batch_frames),
                "successful_ocr": 0,
                "successful_updates": 0
            }
    
    async def process_folder(self, folder_path, pattern="*.jpg"):
        """
        Process all frames in a folder through OCR and Airtable update.
        
        Args:
            folder_path: Path to the folder
            pattern: File pattern to match
            
        Returns:
            Dictionary with folder processing results
        """
        logger.info(f"Processing folder: {os.path.basename(folder_path)}")
        
        # Get all frames in the folder
        frames = await self.get_frames_in_folder(folder_path, pattern)
        
        if not frames:
            logger.warning(f"No frames found in folder: {folder_path}")
            return {
                "folder": folder_path,
                "total_frames": 0,
                "batches_processed": 0,
                "successful_updates": 0
            }
        
        logger.info(f"Found {len(frames)} frames in folder {os.path.basename(folder_path)}")
        
        # Divide frames into batches
        batches = await self.divide_into_batches(frames, self.batch_size)
        
        # Process each batch
        batch_results = []
        for i, batch in enumerate(batches):
            logger.info(f"Processing batch {i+1}/{len(batches)} with {len(batch)} frames")
            result = await self.process_batch(batch)
            batch_results.append(result)
            
            # Optional: Add a small delay between batches to avoid rate limits
            if i < len(batches) - 1:
                await asyncio.sleep(1)
        
        # Aggregate results
        total_updates = sum(result.get("successful_updates", 0) for result in batch_results)
        
        folder_result = {
            "folder": folder_path,
            "total_frames": len(frames),
            "batches_processed": len(batches),
            "successful_updates": total_updates,
            "batch_results": batch_results
        }
        
        logger.info(f"Completed folder {os.path.basename(folder_path)}: "
                   f"{total_updates}/{len(frames)} frames updated")
        
        return folder_result

    async def process_all_folders(self, base_dir, limit_folders=None, pattern="*.jpg"):
        """
        Process all folders in chronological order.
        
        Args:
            base_dir: Base directory containing screen recording folders
            limit_folders: Optional limit on number of folders to process
            pattern: File pattern to match
            
        Returns:
            Dictionary with overall processing results
        """
        # Get all folders chronologically
        folders = await self.get_folders_chronologically(base_dir)
        
        if limit_folders:
            folders = folders[:limit_folders]
            
        logger.info(f"Processing {len(folders)} folders chronologically")
        
        # Process each folder
        folder_results = []
        for folder in folders:
            result = await self.process_folder(folder, pattern)
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
        total_updates = sum(result.get("successful_updates", 0) for result in folder_results)
        
        logger.info(f"Completed all folders: {total_updates}/{total_frames} frames processed and updated")
        
        return {
            "folders_processed": len(folders),
            "total_frames": total_frames,
            "successful_updates": total_updates,
            "folder_results": folder_results
        }

async def main():
    """Main entry point for the OCR processor."""
    parser = argparse.ArgumentParser(
        description="OCRProcessorAndUpsertToAirtable - Process frames with OCR and update Airtable"
    )
    
    # Input options
    parser.add_argument("--base-dir", 
                      default=os.environ.get('FRAME_BASE_DIR', '/home/jason/Videos/screenRecordings'),
                      help="Base directory containing screen recording folders")
    parser.add_argument("--pattern", default="*.jpg", 
                      help="Glob pattern for image files (default: *.jpg)")
    parser.add_argument("--limit-folders", type=int, default=None,
                      help="Maximum number of folders to process")
    parser.add_argument("--batch-size", type=int, default=10,
                      help="Number of frames to process in each batch (default: 10)")
    
    args = parser.parse_args()
    
    try:
        # Log API key information
        logger.info(f"Using {len(GEMINI_API_KEYS)} Gemini API keys with rotation: {GEMINI_USE_KEY_ROTATION}")
        
        # Initialize processor
        processor = OCRProcessorAndUpsertToAirtable(batch_size=args.batch_size)
        
        # Process all folders
        results = await processor.process_all_folders(
            base_dir=args.base_dir,
            limit_folders=args.limit_folders,
            pattern=args.pattern
        )
        
        # Save final results
        final_output = os.path.join(OCR_RESULTS_DIR, f"ocr_processing_final_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        os.makedirs(os.path.dirname(final_output), exist_ok=True)
        
        with open(final_output, 'w') as f:
            json.dump({
                "processing_time": datetime.datetime.now().isoformat(),
                "parameters": vars(args),
                "results": results
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