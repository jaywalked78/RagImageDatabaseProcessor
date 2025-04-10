#!/usr/bin/env python3
"""
Process JSON Files Script

This script:
1. Finds JSON files in a specified folder
2. Processes each file by chunking the metadata
3. Organizes data into a structured format for n8n processing
4. Sends the processed data to a webhook (test or production)

Usage:
    python process_json_files.py --folder <folder_name> [--test] [--file <specific_file>]
"""

import os
import sys
import json
import glob
import argparse
import logging
import requests
import traceback
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure logs and data directories exist
Path("logs").mkdir(exist_ok=True, parents=True)
Path("data").mkdir(exist_ok=True, parents=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/process_json.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
TEST_WEBHOOK_URL = os.getenv("TEST_WEBHOOK_URL", "")
PRODUCTION_WEBHOOK_URL = os.getenv("PRODUCTION_WEBHOOK_URL", "")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
FRAME_BASE_DIR = os.getenv("FRAME_BASE_DIR", "")

# Validate essential environment variables
if not FRAME_BASE_DIR:
    logger.error("FRAME_BASE_DIR not set in environment variables")
    sys.exit(1)

if not TEST_WEBHOOK_URL or not PRODUCTION_WEBHOOK_URL:
    logger.warning("TEST_WEBHOOK_URL or PRODUCTION_WEBHOOK_URL not set in environment")

def normalize_folder_name(folder_name: str) -> str:
    """
    Remove '_frames' suffix from folder name if present.
    """
    if folder_name and folder_name.endswith('_frames'):
        return folder_name[:-7]  # Remove the '_frames' suffix
    return folder_name

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load a JSON file and return its contents as a dictionary"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {e}")
        return {}

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into chunks with a specified size and overlap.
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        if end < text_length and end - start == chunk_size:
            # Find the last space in the chunk to avoid cutting words
            last_space = text[start:end].rfind(' ')
            if last_space != -1:
                end = start + last_space + 1
        
        chunks.append(text[start:end].strip())
        start = end - overlap if end - overlap > start else end
    
    return chunks

def get_frame_image_path(folder_name: str, frame_number: str) -> Optional[Path]:
    """
    Get the path to the frame image in the base directory.
    
    Args:
        folder_name: Name of the folder containing the frame
        frame_number: Frame number/name
        
    Returns:
        Path to the frame image or None if not found
    """
    # Normalize folder name
    folder_name = normalize_folder_name(folder_name)
    
    # Construct base folder path
    base_folder_path = Path(FRAME_BASE_DIR) / folder_name
    
    if not base_folder_path.exists():
        logger.error(f"Frame folder not found: {base_folder_path}")
        return None
    
    logger.info(f"Looking for frame in location: {base_folder_path}")
    
    # Try different extensions for the frame image
    extensions = ['.jpg', '.jpeg', '.png']
    
    for ext in extensions:
        # Try exact match first
        frame_path = base_folder_path / f"{frame_number}{ext}"
        if frame_path.exists():
            logger.info(f"Found frame image at: {frame_path}")
            return frame_path
        
        # Try with common frame name patterns
        patterns = [
            f"{frame_number}{ext}",
            f"frame_{frame_number}{ext}",
            f"frame_{frame_number.zfill(6)}{ext}"
        ]
        
        for pattern in patterns:
            for file_path in base_folder_path.glob(pattern):
                logger.info(f"Found frame image at: {file_path}")
                return file_path
    
    logger.error(f"Frame image not found for {folder_name}/{frame_number}")
    return None

def process_json_file(file_path: Path, test_mode: bool = False) -> Dict[str, Any]:
    """
    Process a JSON file:
    1. Extract metadata
    2. Chunk the text content
    3. Structure the output with nested arrays
    
    Args:
        file_path: Path to the JSON file
        test_mode: Whether to run in test mode
        
    Returns:
        Dictionary with processed data including chunks
    """
    data = load_json_file(file_path)
    if not data:
        logger.error(f"Failed to load JSON data from {file_path}")
        return {}
    
    # Extract relevant fields
    folder_path = data.get("folder_path", "")
    file_name = data.get("file_name", "")
    metadata = data.get("metadata", {})
    content = data.get("content", "")
    
    # Extract folder and frame names
    folder_name = Path(folder_path).name if folder_path else ""
    frame_number = Path(file_name).stem if file_name else ""
    airtable_record_id = metadata.get("RecordID", "")
    
    # Normalize folder name
    folder_name = normalize_folder_name(folder_name)
    
    # Check if we have necessary information
    if not folder_name or not frame_number:
        logger.error(f"Missing folder_name or frame_number in {file_path}")
        return {}
    
    # Combine metadata and content into a single text for chunking
    full_text = ""
    
    # Add metadata fields
    for key, value in metadata.items():
        if value:
            full_text += f"{key}: {value}\n\n"
    
    # Add content if available
    if content:
        full_text += f"Content: {content}\n\n"
    
    logger.info(f"Processing frame: {folder_name}/{frame_number}")
    
    # Chunk the text
    logger.info("Chunking text")
    chunks = chunk_text(full_text)
    logger.info(f"Created {len(chunks)} chunks from {file_path}")
    
    # Process each chunk
    all_chunks = []
    for i, chunk in enumerate(chunks):
        logger.info(f"Processing chunk {i+1}/{len(chunks)}")
        
        all_chunks.append({
            "id": f"{folder_name}_{frame_number}_chunk_{i}",
            "chunk_index": i,
            "text": chunk
        })
    
    # Create the frame result with the new structure
    frame_result = {
        "id": f"{folder_name}_{frame_number}",
        "folder_name": folder_name,
        "file_name": file_name,
        "frame_number": frame_number,
        "airtable_record_id": airtable_record_id,
        "metadata": metadata,
        "content": content,
        "chunks": all_chunks,
        "processed_at": datetime.now().isoformat(),
        "test_mode": test_mode
    }
    
    logger.info(f"Completed processing of {file_path}")
    return frame_result

def send_to_webhook(data: Dict[str, Any], test_mode: bool = False) -> bool:
    """
    Send processed data to webhook.
    
    Args:
        data: Data to send
        test_mode: Whether to use test webhook
        
    Returns:
        Success status (True/False)
    """
    webhook_url = TEST_WEBHOOK_URL if test_mode else PRODUCTION_WEBHOOK_URL
    
    if not webhook_url:
        logger.error(f"{'TEST' if test_mode else 'PRODUCTION'}_WEBHOOK_URL not set")
        return False
    
    try:
        logger.info(f"Sending data to {'test' if test_mode else 'production'} webhook: {webhook_url}")
        
        response = requests.post(
            webhook_url,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in (200, 201, 202):
            logger.info(f"Successfully sent data to webhook: {response.status_code}")
            return True
        else:
            logger.error(f"Error sending data to webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Exception sending data to webhook: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def find_json_files(folder_name: str) -> List[Path]:
    """
    Find JSON files for a specific folder in the data directory.
    
    Args:
        folder_name: Folder name to filter by
        
    Returns:
        List of paths to JSON files
    """
    # Normalize folder name
    normalized_name = normalize_folder_name(folder_name)
    
    # Define possible folder paths
    possible_folders = [
        Path("data") / normalized_name,  # Without '_frames'
        Path("data") / f"{normalized_name}_frames"  # With '_frames'
    ]
    
    files = []
    for folder_path in possible_folders:
        if folder_path.exists():
            logger.info(f"Looking for JSON files in {folder_path}")
            pattern = str(folder_path / "*.json")
            folder_files = [Path(p) for p in glob.glob(pattern)]
            files.extend(folder_files)
            
    if not files:
        logger.error(f"No JSON files found for folder {folder_name}")
        
    logger.info(f"Found {len(files)} JSON files for folder {folder_name}")
    return files

def process_folder(folder_name: str, test_mode: bool = False) -> Dict[str, Any]:
    """
    Process all JSON files in a specific folder.
    
    Args:
        folder_name: Name of the folder to process
        test_mode: Whether to run in test mode
        
    Returns:
        Summary of processing results
    """
    # Get JSON files for the folder
    files = find_json_files(folder_name)
    
    if not files:
        logger.error(f"No files found for folder {folder_name}")
        return {
            "status": "error",
            "message": f"No files found for folder {folder_name}",
            "folder_name": folder_name,
            "timestamp": datetime.now().isoformat()
        }
    
    # Initialize result arrays - frames
    frames = []
    
    # Process each file
    processed_count = 0
    error_count = 0
    
    for file_path in files:
        try:
            logger.info(f"Processing file {file_path}")
            
            # Process the file
            result = process_json_file(file_path, test_mode)
            
            if not result:
                logger.error(f"Failed to process {file_path}")
                error_count += 1
                continue
                
            # Add the frame to our frames array
            frames.append(result)
            
            processed_count += 1
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            logger.error(traceback.format_exc())
            error_count += 1
    
    # Create the final output structure
    output = {
        "folder_name": folder_name,
        "processed_at": datetime.now().isoformat(),
        "test_mode": test_mode,
        "frames": frames,
        "stats": {
            "total_files": len(files),
            "processed": processed_count,
            "errors": error_count
        }
    }
    
    # Send to webhook if we have frames
    if frames:
        logger.info(f"Sending {len(frames)} frames to webhook")
        send_to_webhook(output, test_mode)
    else:
        logger.warning("No frames to send to webhook")
    
    return output

def process_specific_file(folder_name: str, file_path: str, test_mode: bool = False) -> Dict[str, Any]:
    """
    Process a specific JSON file.
    
    Args:
        folder_name: Name of the folder (context only)
        file_path: Path to the JSON file
        test_mode: Whether to run in test mode
        
    Returns:
        Processing result
    """
    # Check if file exists
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return {
            "status": "error",
            "message": f"File not found: {file_path}",
            "folder_name": folder_name,
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        logger.info(f"Processing specific file: {file_path}")
        
        # Process the file
        result = process_json_file(path, test_mode)
        
        if not result:
            logger.error(f"Failed to process {file_path}")
            return {
                "status": "error",
                "message": f"Failed to process {file_path}",
                "folder_name": folder_name,
                "timestamp": datetime.now().isoformat()
            }
        
        # Create the output with just this frame
        output = {
            "folder_name": folder_name,
            "processed_at": datetime.now().isoformat(),
            "test_mode": test_mode,
            "frames": [result],
            "stats": {
                "total_files": 1,
                "processed": 1,
                "errors": 0
            }
        }
        
        # Send to webhook
        logger.info("Sending frame to webhook")
        send_to_webhook(output, test_mode)
        
        return output
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": f"Error processing {file_path}: {str(e)}",
            "folder_name": folder_name,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Process JSON files in a folder')
    parser.add_argument('--folder', '-f', required=True, help='Folder name to process')
    parser.add_argument('--test', '-t', action='store_true', help='Run in test mode')
    parser.add_argument('--file', help='Process a specific file')
    
    args = parser.parse_args()
    
    logger.info(f"Starting processing with arguments: {args}")
    
    # Process specific file or entire folder
    if args.file:
        result = process_specific_file(args.folder, args.file, args.test)
    else:
        result = process_folder(args.folder, args.test)
    
    logger.info(f"Processing complete: {result.get('stats', {})}")
    return result

if __name__ == "__main__":
    main() 