#!/usr/bin/env python3
"""
Batch OCR Processing Script

This script:
1. Processes frames from specified folders using OCR
2. Analyzes OCR text with Gemini for content & sensitivity detection
3. Updates Airtable records with OCR data and sensitivity flags
"""

import os
import sys
import re
import json
import glob
import time
import logging
import asyncio
import argparse
from datetime import datetime
from urllib.parse import quote
from typing import Dict, List, Tuple, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import math

import cv2
import pytesseract
import google.generativeai as genai
import aiohttp
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"ocr_batch_process_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ocr_batch')

# Load environment variables
load_dotenv()

# Airtable configuration
AIRTABLE_PERSONAL_ACCESS_TOKEN = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'tblFrameAnalysis')
AIRTABLE_FOLDER_PATH_FIELD = os.getenv('AIRTABLE_FOLDER_PATH_FIELD', 'FolderPath')
AIRTABLE_OCR_DATA_FIELD = os.getenv('AIRTABLE_OCR_DATA_FIELD', 'OCRData')
AIRTABLE_FLAGGED_FIELD = os.getenv('AIRTABLE_FLAGGED_FIELD', 'Flagged')
AIRTABLE_TECHNICAL_DETAILS_FIELD = os.getenv('AIRTABLE_TECHNICAL_DETAILS_FIELD', 'TechnicalDetails')

# Gemini configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-pro')

# Screen recordings directory
SCREEN_RECORDINGS_DIR = os.getenv('SCREEN_RECORDINGS_DIR', '/home/jason/Videos/screenRecordings')

# Target folders to process
TARGET_FOLDERS = [
    "screen_recording_2025_02_20_at_12_14_43_pm"
]

# Rate limiting settings
OCR_RATE_LIMIT_SECONDS = 0.1  # Time to sleep between OCR operations to prevent system overload
AIRTABLE_RATE_LIMIT_SECONDS = 0.2  # Time to sleep between Airtable API calls
GEMINI_RATE_LIMIT_SECONDS = 0.5  # Time to sleep between Gemini API calls

# Process limits
MAX_FRAMES_PER_FOLDER = 0  # 0 means no limit - process all frames in each folder
MAX_CONCURRENT_OCR = 4  # Maximum concurrent OCR operations
BATCH_SIZE = 10  # Process frames in batches of this size

# Batch size for processing
AIRTABLE_BATCH_SIZE = 10  # Number of records to update in one batch

# Sensitivity keywords to search for in OCR text
SENSITIVITY_KEYWORDS = [
    "password", "api key", "secret", "token", "credential", "private key", 
    "auth", "authentication", "confidential", "restricted", "sensitive"
]

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def calculate_batches_needed(total_frames: int, batch_size: int = BATCH_SIZE) -> int:
    """
    Calculate how many batches will be needed to process all frames in a folder.
    
    Args:
        total_frames: Total number of frames in the folder
        batch_size: Size of each batch (default is BATCH_SIZE)
        
    Returns:
        Number of batches needed (rounded up for partial batches)
    """
    return math.ceil(total_frames / batch_size)

def get_frames_from_folder(folder_path: str, limit: int = MAX_FRAMES_PER_FOLDER) -> List[Dict[str, str]]:
    """
    Get a list of frames from a folder.
    
    Args:
        folder_path: Path to the folder
        limit: Maximum number of frames to process (0 means no limit)
        
    Returns:
        List of frame information dictionaries
    """
    frames = []
    frame_files = sorted([f for f in os.listdir(folder_path) if f.startswith('frame_') and f.endswith('.jpg')])
    
    if limit and limit > 0:
        frame_files = frame_files[:limit]
    
    total_frames = len(frame_files)
    logger.info(f"Found {total_frames} frames in {os.path.basename(folder_path)}" + 
                (f" (limited to {limit})" if limit and limit > 0 and total_frames >= limit else ""))
    
    # Calculate number of batches needed
    batches_needed = calculate_batches_needed(total_frames)
    logger.info(f"Will require {batches_needed} batches to process all frames")
    
    for frame_file in frame_files:
        frame_path = os.path.join(folder_path, frame_file)
        frame_info = {
            'full_path': frame_path,
            'frame_name': frame_file,
            'folder_name': os.path.basename(folder_path)
        }
        frames.append(frame_info)
    
    return frames

def preprocess_image_for_ocr(image_path: str) -> Any:
    """
    Preprocess image for better OCR results.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Preprocessed image
    """
    image = cv2.imread(image_path)
    
    if image is None:
        logger.error(f"Could not read image: {image_path}")
        return None
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh

def perform_ocr(image_path: str) -> str:
    """
    Perform OCR on an image and return the text.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text from the image
    """
    try:
        # Preprocess the image
        preprocessed_image = preprocess_image_for_ocr(image_path)
        
        if preprocessed_image is None:
            return ""
        
        # Perform OCR using Tesseract
        text = pytesseract.image_to_string(preprocessed_image)
        
        # Remove any non-printable characters
        text = ''.join(char for char in text if char.isprintable())
        
        return text
    except Exception as e:
        logger.error(f"Error performing OCR on {image_path}: {str(e)}")
        return ""

def check_sensitivity(ocr_text: str) -> Tuple[bool, List[str]]:
    """
    Check if the OCR text contains sensitive information.
    
    Args:
        ocr_text: Text extracted from OCR
        
    Returns:
        Tuple of (is_sensitive, matched_keywords)
    """
    matched_keywords = []
    
    for keyword in SENSITIVITY_KEYWORDS:
        if re.search(rf'\b{keyword}\b', ocr_text.lower()):
            matched_keywords.append(keyword)
    
    return len(matched_keywords) > 0, matched_keywords

async def analyze_with_gemini(ocr_text: str, frame_info: Dict[str, str], existing_summary: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze OCR text with Gemini for content summary and sensitivity detection.
    Also extracts and cleans up meaningful text from the OCR output.
    
    Args:
        ocr_text: Text extracted from OCR
        frame_info: Information about the frame
        existing_summary: Existing summary from Airtable, if available
        
    Returns:
        Analysis results from Gemini
    """
    if not ocr_text.strip():
        return {
            "summary": existing_summary or "No text content detected in image.",
            "cleaned_text": "",
            "is_sensitive": False,
            "sensitive_content": [],
            "technical_details": {
                "ocr_status": "empty",
                "word_count": 0,
                "char_count": 0
            }
        }
    
    # Build the prompt
    summary_context = ""
    if existing_summary:
        summary_context = f"""
    EXISTING SUMMARY FROM PREVIOUS ANALYSIS:
    {existing_summary}
    
    Use this existing summary as context when analyzing the OCR text. It may provide helpful context about what's in the image.
    If the existing summary is accurate and consistent with the OCR text, you can maintain similar wording.
    """
    
    prompt = f"""
    You are analyzing OCR text extracted from a screen recording frame.
    Frame: {frame_info['frame_name']} from folder {frame_info['folder_name']}
    
    {summary_context}
    
    OCR TEXT:
    {ocr_text}
    
    Please analyze this text and provide the following:
    1. A brief summary of the content (1-2 sentences)
       - If there is an existing summary and it's accurate, you can refine it rather than creating a completely new one
    
    2. Extract and clean up ONLY the semantically and contextually meaningful text from the OCR output.
       IMPORTANT CLEANING INSTRUCTIONS:
       - You MUST be extremely aggressive in filtering out garbled, nonsensical, or erroneous text
       - Remove ANY text that doesn't make perfect semantic and logical sense
       - Remove ANY phrases that seem like OCR errors, even if they contain some real words
       - Remove ALL gibberish like "fermentor Bait to cha 2 CC" completely
       - Focus ONLY on keeping text that forms complete, coherent, and logical phrases
       - UI elements should only be kept if they form clear, complete labels or instructions
       - When in doubt, exclude rather than include
       - The final output must read naturally as if it was written by a human
       - It's better to return LESS text that is 100% coherent than more text with errors
    
    3. Detect if there is any sensitive information (e.g., passwords, API keys, tokens, etc.)
    4. List any sensitive information found
    
    Format your response as a JSON object with the following structure:
    {{
        "summary": "Brief summary of content",
        "cleaned_text": "Only the meaningful, cleaned text with perfect semantic and contextual coherence",
        "is_sensitive": true/false,
        "sensitive_content": ["list", "of", "sensitive", "items"],
        "technical_details": {{
            "ocr_status": "success or failed",
            "content_type": "type of content (e.g., code, text, UI)",
            "word_count": number of words,
            "char_count": number of characters
        }}
    }}
    
    Respond ONLY with the JSON. No additional text before or after.
    """
    
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )
        
        # Parse the response
        text_response = response.text
        
        # If the response looks like it contains JSON, extract it
        if '{' in text_response and '}' in text_response:
            # Find the first '{' and the last '}'
            start_idx = text_response.find('{')
            end_idx = text_response.rfind('}') + 1
            json_str = text_response[start_idx:end_idx]
            
            # Parse the JSON
            analysis = json.loads(json_str)
            
            # Ensure we have a cleaned_text field
            if "cleaned_text" not in analysis:
                analysis["cleaned_text"] = analysis.get("summary", "")
                
            return analysis
        else:
            # Fallback if no JSON is found
            return {
                "summary": existing_summary or "Failed to analyze OCR text with Gemini.",
                "cleaned_text": "",
                "is_sensitive": False,
                "sensitive_content": [],
                "technical_details": {
                    "ocr_status": "analysis_failed",
                    "word_count": len(ocr_text.split()),
                    "char_count": len(ocr_text)
                }
            }
    except Exception as e:
        logger.error(f"Error analyzing with Gemini: {str(e)}")
        return {
            "summary": existing_summary or "Error analyzing OCR text with Gemini.",
            "cleaned_text": "",
            "is_sensitive": False,
            "sensitive_content": [],
            "technical_details": {
                "ocr_status": "analysis_error",
                "error": str(e),
                "word_count": len(ocr_text.split()),
                "char_count": len(ocr_text)
            }
        }

async def fetch_airtable_record(frame_path: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a record from Airtable based on the frame path.
    
    Args:
        frame_path: Full path to the frame file
        
    Returns:
        Airtable record or None if not found
    """
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PERSONAL_ACCESS_TOKEN or AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Create the filter formula
    filter_formula = f"({{{AIRTABLE_FOLDER_PATH_FIELD}}} = '{frame_path}')"
    encoded_filter = quote(filter_formula)
    
    # Fields we want to retrieve, including the Summary field if it exists
    fields = [AIRTABLE_FOLDER_PATH_FIELD, AIRTABLE_OCR_DATA_FIELD, AIRTABLE_FLAGGED_FIELD, AIRTABLE_TECHNICAL_DETAILS_FIELD, "Summary"]
    
    # Build the URL with multiple fields[] parameters
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}?filterByFormula={encoded_filter}"
    for field in fields:
        url += f"&fields[]={quote(field)}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to fetch Airtable record: {error_text}")
                    return None
                
                data = await response.json()
                records = data.get('records', [])
                
                if not records:
                    logger.warning(f"No Airtable record found matching {frame_path}")
                    return None
                
                # Return the first matching record
                return records[0]
    except Exception as e:
        logger.error(f"Error fetching Airtable record: {str(e)}")
        return None

async def create_airtable_record(frame_info: Dict[str, str]) -> Optional[str]:
    """
    Create a new Airtable record for a frame.
    
    Args:
        frame_info: Information about the frame
        
    Returns:
        Record ID if created successfully, None otherwise
    """
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PERSONAL_ACCESS_TOKEN or AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Extract frame path
    frame_path = frame_info['full_path']
    
    # Create payload with only the FolderPath field 
    # Airtable API requires at least one field to be present
    payload = {
        "fields": {
            AIRTABLE_FOLDER_PATH_FIELD: frame_path
        }
    }
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status not in (200, 201):
                    error_text = await response.text()
                    logger.error(f"Failed to create Airtable record: {error_text}")
                    return None
                
                data = await response.json()
                record_id = data.get('id')
                logger.info(f"Created new Airtable record {record_id} for {frame_path}")
                return record_id
    except Exception as e:
        logger.error(f"Error creating Airtable record: {str(e)}")
        return None

async def should_process_frame(frame_info: Dict[str, str]) -> Tuple[bool, Optional[str]]:
    """
    Check if a frame should be processed (has empty OCRData field in Airtable or no Airtable record).
    If no Airtable record exists, create one.
    
    Args:
        frame_info: Information about the frame
        
    Returns:
        Tuple of (should_process, record_id)
    """
    frame_path = frame_info['full_path']
    
    # Fetch Airtable record
    airtable_record = await fetch_airtable_record(frame_path)
    
    if not airtable_record:
        logger.info(f"No Airtable record found for {frame_path} - creating one")
        # Create a new Airtable record for this frame
        record_id = await create_airtable_record(frame_info)
        if record_id:
            logger.info(f"Created new Airtable record for {frame_path}")
            return True, record_id
        else:
            logger.error(f"Failed to create Airtable record for {frame_path}")
            return False, None
    
    record_id = airtable_record.get("id")
    fields = airtable_record.get("fields", {})
    
    # Check if OCRData field is empty
    ocr_data = fields.get(AIRTABLE_OCR_DATA_FIELD, "")
    if ocr_data and ocr_data.strip():
        logger.info(f"Skipping frame {frame_path} - already has OCR data")
        return False, record_id
    
    return True, record_id

async def update_airtable_record(record_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update an Airtable record with OCR data and analysis.
    
    Args:
        record_id: Airtable record ID
        updates: Dictionary of field updates
        
    Returns:
        Success status
    """
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PERSONAL_ACCESS_TOKEN or AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}/{record_id}"
    
    data = {
        "fields": updates
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.patch(url, headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to update Airtable record: {error_text}")
                    return False
                
                logger.info(f"Successfully updated Airtable record: {record_id}")
                return True
    except Exception as e:
        logger.error(f"Error updating Airtable record: {str(e)}")
        return False

async def process_frame(frame_info: Dict[str, str]) -> Dict[str, Any]:
    """
    Process a single frame with OCR and analysis.
    
    Args:
        frame_info: Information about the frame
        
    Returns:
        Processing results
    """
    frame_path = frame_info['full_path']
    logger.info(f"Processing frame: {frame_path}")
    
    # Fetch Airtable record for existing summary if available
    existing_summary = None
    airtable_record = await fetch_airtable_record(frame_path)
    if airtable_record and "fields" in airtable_record:
        fields = airtable_record["fields"]
        if "Summary" in fields and fields["Summary"]:
            existing_summary = fields["Summary"]
            logger.info(f"Found existing summary for {frame_path}")
    
    # Step 1: Perform OCR
    ocr_text = await asyncio.to_thread(perform_ocr, frame_path)
    
    if not ocr_text:
        logger.warning(f"No OCR text extracted from {frame_path}")
    else:
        logger.debug(f"Extracted {len(ocr_text)} characters from {frame_path}")
    
    # Step 2: Check for sensitive information
    is_sensitive, sensitive_keywords = check_sensitivity(ocr_text)
    
    if is_sensitive:
        logger.warning(f"Sensitive information detected in {frame_path}: {', '.join(sensitive_keywords)}")
    
    # Step 3: Analyze with Gemini, passing the existing summary
    time.sleep(GEMINI_RATE_LIMIT_SECONDS)  # Rate limiting
    analysis = await analyze_with_gemini(ocr_text, frame_info, existing_summary)
    
    # Merge our sensitivity check with Gemini's analysis
    if is_sensitive and not analysis.get("is_sensitive", False):
        analysis["is_sensitive"] = True
        analysis["sensitive_content"] = sensitive_keywords + analysis.get("sensitive_content", [])
    
    # Complete result
    result = {
        "frame_info": frame_info,
        "ocr_text": ocr_text,
        "cleaned_text": analysis.get("cleaned_text", ""),
        "analysis": analysis,
        "is_sensitive": analysis.get("is_sensitive", False) or is_sensitive,
        "sensitive_keywords": list(set(sensitive_keywords + analysis.get("sensitive_content", []))),
        "summary": analysis.get("summary", "No summary available")
    }
    
    logger.info(f"Completed processing frame: {frame_path}")
    logger.info(f"Summary: {result['summary']}")
    logger.info(f"Sensitive: {result['is_sensitive']}")
    
    return result

async def process_batch(frames_batch: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Process a batch of frames with OCR and analysis.
    
    Args:
        frames_batch: List of frame information dictionaries
        
    Returns:
        List of processing results
    """
    if not frames_batch:
        return []

    batch_folder = frames_batch[0]["folder_name"]
    batch_size = len(frames_batch)
    logger.info(f"Processing batch of {batch_size} frames from {batch_folder}")
    
    processing_results = []
    skipped_frames = 0
    frames_with_new_airtable = 0
    
    # First check which frames need processing (have empty OCRData field or no Airtable record)
    frames_to_process = []
    record_ids = {}  # Store record IDs to avoid fetching again later
    
    for frame_info in frames_batch:
        should_process, record_id = await should_process_frame(frame_info)
        if should_process:
            frames_to_process.append(frame_info)
            if record_id:
                record_ids[frame_info['full_path']] = record_id
                # Check if this is a newly created record
                if await fetch_airtable_record(frame_info['full_path']) is None:
                    frames_with_new_airtable += 1
        else:
            skipped_frames += 1
    
    logger.info(f"Skipping {skipped_frames}/{batch_size} frames that already have OCR data")
    logger.info(f"Processing {len(frames_to_process)}/{batch_size} frames with empty OCR data")
    logger.info(f"Created {frames_with_new_airtable} new Airtable records")
    
    if not frames_to_process:
        logger.info(f"No frames to process in this batch")
        return []
    
    # Use semaphore to limit concurrent OCR operations
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_OCR)
    
    async def process_with_semaphore(frame_info):
        async with semaphore:
            return await process_frame(frame_info)
    
    # Process frames in parallel within the batch
    tasks = [process_with_semaphore(frame) for frame in frames_to_process]
    processing_results = await asyncio.gather(*tasks)
    
    # Attach record IDs to results
    for result in processing_results:
        frame_path = result["frame_info"]["full_path"]
        if frame_path in record_ids:
            result["record_id"] = record_ids[frame_path]
            result["has_airtable_record"] = True
        else:
            result["has_airtable_record"] = False
    
    # Save batch results to JSON file with enhanced details
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f"ocr_results_{batch_folder}_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "folder": batch_folder,
            "total_frames": len(processing_results),
            "skipped_frames": skipped_frames,
            "new_airtable_records": frames_with_new_airtable,
            "results": [
                {
                    "frame": r["frame_info"]["full_path"],
                    "frame_name": r["frame_info"]["frame_name"],
                    "folder": r["frame_info"]["folder_name"],
                    "raw_ocr_text": r["ocr_text"],
                    "cleaned_text": r["cleaned_text"],
                    "is_sensitive": r["is_sensitive"],
                    "sensitive_keywords": r["sensitive_keywords"] if r["is_sensitive"] else [],
                    "summary": r["summary"],
                    "has_airtable_record": r.get("has_airtable_record", False),
                    "record_id": r.get("record_id", "")
                }
                for r in processing_results
            ]
        }, f, indent=2)
    
    logger.info(f"Saved batch processing results to {results_file}")
    
    # Summary of OCR processing for this batch
    sensitive_count = sum(1 for r in processing_results if r["is_sensitive"])
    sensitivity_percentage = (sensitive_count / len(processing_results) * 100) if processing_results else 0
    
    logger.info(f"\n===== Batch OCR Processing Summary =====")
    logger.info(f"Folder: {batch_folder}")
    logger.info(f"Total frames in batch: {batch_size}")
    logger.info(f"Skipped frames (already processed): {skipped_frames}")
    logger.info(f"New Airtable records created: {frames_with_new_airtable}")
    logger.info(f"Frames processed: {len(processing_results)}")
    logger.info(f"Frames with sensitive content: {sensitive_count}")
    logger.info(f"Sensitive content percentage: {sensitivity_percentage:.2f}%")
    
    return processing_results

async def update_airtable_with_results(processing_results: List[Dict[str, Any]]) -> Tuple[int, int]:
    """
    Update Airtable records with OCR processing results.
    
    Args:
        processing_results: List of processing results for frames
        
    Returns:
        Tuple of (success_count, total_count)
    """
    success_count = 0
    total_count = len(processing_results)
    
    if not total_count:
        logger.info("No records to update in Airtable")
        return 0, 0
    
    logger.info(f"Updating {total_count} Airtable records with OCR results")
    
    # Calculate overall sensitivity percentage based on all processed frames
    sensitive_count = sum(1 for r in processing_results if r["is_sensitive"])
    sensitivity_percentage = (sensitive_count / len(processing_results) * 100) if processing_results else 0
    
    for result in processing_results:
        # Each result should now have a record_id since we create records when missing
        record_id = result.get("record_id")
        if not record_id:
            frame_path = result["frame_info"]["full_path"]
            logger.error(f"Missing record_id for {frame_path} - cannot update Airtable")
            continue
        
        # Prepare updates for Airtable - only OCRData and Flagged fields
        # Format the Flagged field with sensitivity info
        flagged_value = f"Yes - Sensitive content detected" if result["is_sensitive"] else f"No"
        
        # Add overall sensitivity percentage to all records
        flagged_value += f" (Overall sensitivity: {sensitivity_percentage:.2f}%)"
        
        # Use the cleaned text from LLM instead of raw OCR text
        updates = {
            AIRTABLE_OCR_DATA_FIELD: result["cleaned_text"],
            AIRTABLE_FLAGGED_FIELD: flagged_value
        }
        
        # Update Airtable record
        time.sleep(AIRTABLE_RATE_LIMIT_SECONDS)  # Rate limiting
        success = await update_airtable_record(record_id, updates)
        
        if success:
            success_count += 1
    
    return success_count, total_count

def get_all_folders(base_dir: str = SCREEN_RECORDINGS_DIR) -> List[str]:
    """
    Get all screen recording folders, sorted chronologically.
    
    Args:
        base_dir: Base directory containing folders
        
    Returns:
        List of folder paths sorted chronologically
    """
    folders = []
    
    # Find all directories that match the screen recording pattern
    for item in os.listdir(base_dir):
        if item.startswith("screen_recording_") and os.path.isdir(os.path.join(base_dir, item)):
            folders.append(item)
    
    # Sort chronologically based on the timestamp in the folder name
    # Format is typically screen_recording_YYYY_MM_DD_at_HH_MM_SS_am/pm
    folders.sort()
    
    logger.info(f"Found {len(folders)} screen recording folders")
    return folders

async def main(args):
    """Main function for batch OCR processing"""
    logger.info("Starting batch OCR processing")
    
    # Get folders to process
    folders = []
    if args.folder:
        # Use specific folders if provided
        folders = args.folder
        logger.info(f"Processing specified folders: {', '.join(folders)}")
    else:
        # Get all folders sorted chronologically
        folders = get_all_folders()
        logger.info(f"Processing {len(folders)} folders in chronological order")
    
    total_frames_processed = 0
    total_success_count = 0
    total_records_attempted = 0
    total_new_airtable_records = 0
    all_batch_results = []
    
    # Process each folder
    for folder_name in folders:
        folder_path = os.path.join(SCREEN_RECORDINGS_DIR, folder_name)
        all_frames = get_frames_from_folder(folder_path, args.limit)
        
        if not all_frames:
            logger.warning(f"No frames found in {folder_name}, skipping to next folder")
            continue
        
        total_batches = calculate_batches_needed(len(all_frames))
        logger.info(f"Processing {len(all_frames)} frames from {folder_name} in {total_batches} batches of {BATCH_SIZE}")
        
        folder_results = []
        
        # Process frames in batches
        for i in range(0, len(all_frames), BATCH_SIZE):
            batch_frames = all_frames[i:i+BATCH_SIZE]
            batch_number = (i // BATCH_SIZE) + 1
            
            logger.info(f"Processing batch {batch_number}/{total_batches} from {folder_name}")
            
            # Process the batch
            processing_results = await process_batch(batch_frames)
            
            if not processing_results:
                logger.warning(f"No results for batch {batch_number}/{total_batches}, skipping")
                continue
            
            total_frames_processed += len(processing_results)
            # Count new Airtable records - fixing the async issue
            batch_new_records = 0  # Initialize counter
            for r in processing_results:
                # Check if this has a record_id (which means it has an Airtable record)
                if r.get("record_id"):
                    # We can't directly use 'await' in a generator expression or list comprehension with 'sum'
                    # So we need to check each record individually
                    existing_record = await fetch_airtable_record(r["frame_info"]["full_path"])
                    # If this record was just created this run, increment counter
                    if not existing_record or existing_record.get("id") != r.get("record_id"):
                        batch_new_records += 1
            
            total_new_airtable_records += batch_new_records
            folder_results.extend(processing_results)
            
            # Update Airtable records if enabled
            if args.update_airtable:
                logger.info(f"Updating Airtable records for batch {batch_number}/{total_batches}")
                success_count, attempt_count = await update_airtable_with_results(processing_results)
                
                total_success_count += success_count
                total_records_attempted += attempt_count
                
                logger.info(f"\n===== Batch Airtable Update Summary =====")
                logger.info(f"Folder: {folder_name}, Batch: {batch_number}/{total_batches}")
                logger.info(f"Records attempted: {attempt_count}")
                logger.info(f"Successfully updated: {success_count}")
                logger.info(f"Failed updates: {attempt_count - success_count}")
                
                if attempt_count > 0:
                    logger.info(f"Success rate: {success_count / attempt_count * 100:.2f}%")
            
            # Optional delay between batches to prevent rate limiting
            if args.batch_delay > 0 and batch_number < total_batches:
                logger.info(f"Waiting for {args.batch_delay} seconds before next batch...")
                await asyncio.sleep(args.batch_delay)
        
        # Add folder results to all results
        all_batch_results.extend(folder_results)
        
        logger.info(f"Completed processing all frames from {folder_name}")
        
        # Optional delay between folders
        if args.folder_delay > 0 and folder_name != folders[-1]:
            logger.info(f"Waiting for {args.folder_delay} seconds before next folder...")
            await asyncio.sleep(args.folder_delay)
    
    # Save comprehensive results to a single JSON file with all processed frames
    if all_batch_results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        comprehensive_file = f"ocr_comprehensive_results_{timestamp}.json"
        
        with open(comprehensive_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "total_folders_processed": len(folders),
                "total_frames_processed": total_frames_processed,
                "total_new_airtable_records": total_new_airtable_records,
                "sensitive_frames": sum(1 for r in all_batch_results if r["is_sensitive"]),
                "results": [
                    {
                        "frame": r["frame_info"]["full_path"],
                        "frame_name": r["frame_info"]["frame_name"],
                        "folder": r["frame_info"]["folder_name"],
                        "raw_ocr_text": r["ocr_text"],
                        "cleaned_text": r["cleaned_text"],
                        "is_sensitive": r["is_sensitive"],
                        "sensitive_keywords": r["sensitive_keywords"] if r["is_sensitive"] else [],
                        "summary": r["summary"],
                        "has_airtable_record": r.get("has_airtable_record", True),
                        "record_id": r.get("record_id", "")
                    }
                    for r in all_batch_results
                ]
            }, f, indent=2)
        
        logger.info(f"Saved comprehensive processing results to {comprehensive_file}")
    
    # Overall processing summary
    logger.info("\n===== Overall OCR Processing Summary =====")
    logger.info(f"Folders processed: {len(folders)}")
    logger.info(f"Total frames processed: {total_frames_processed}")
    logger.info(f"New Airtable records created: {total_new_airtable_records}")
    
    if args.update_airtable and total_records_attempted > 0:
        logger.info("\n===== Overall Airtable Update Summary =====")
        logger.info(f"Total records attempted: {total_records_attempted}")
        logger.info(f"Successfully updated: {total_success_count}")
        logger.info(f"Failed updates: {total_records_attempted - total_success_count}")
        logger.info(f"Overall success rate: {total_success_count / total_records_attempted * 100:.2f}%")
    
    logger.info("Batch OCR processing completed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch OCR Processing Script")
    parser.add_argument("--limit", type=int, default=MAX_FRAMES_PER_FOLDER, 
                        help=f"Maximum frames to process per folder (default: {MAX_FRAMES_PER_FOLDER})")
    parser.add_argument("--update-airtable", action="store_true", 
                        help="Update Airtable records with OCR results")
    parser.add_argument("--folder", type=str, action="append", 
                        help="Target folder name (can specify multiple times)")
    parser.add_argument("--batch-delay", type=int, default=5,
                        help="Seconds to wait between batches (default: 5)")
    parser.add_argument("--folder-delay", type=int, default=10,
                        help="Seconds to wait between folders (default: 10)")
    
    args = parser.parse_args()
    
    asyncio.run(main(args)) 