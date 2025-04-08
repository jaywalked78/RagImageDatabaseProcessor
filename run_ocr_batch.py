#!/usr/bin/env python3
"""
Simple script to run OCR on a batch of frames using existing functionality.
"""

import os
import sys
import argparse
import asyncio
import logging
import glob
from pathlib import Path
from typing import List, Dict, Any
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('run_ocr_batch')

async def process_frames(folder_path: str, limit: int = 10, batch_size: int = 10):
    """
    Process frames from a specific folder using the existing process_frames_by_path.py script.
    
    Args:
        folder_path: Path to folder containing frames
        limit: Maximum number of frames to process
        batch_size: Batch size for processing
    """
    logger.info(f"Processing frames from folder: {folder_path}")
    logger.info(f"Limit: {limit}, Batch size: {batch_size}")
    
    cmd = [
        "python", "process_frames_by_path.py",
        "--folder-path-pattern", f"{folder_path}/*.jpg",
        "--batch-size", str(batch_size),
    ]
    
    if limit:
        cmd.extend(["--limit", str(limit)])
    
    logger.info(f"Running command: {' '.join(cmd)}")
    
    # Run the process_frames_by_path.py script
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        logger.error(f"Error processing frames: {stderr.decode()}")
        return False
    
    logger.info(f"OCR processing completed successfully")
    logger.info(stdout.decode())
    return True

async def update_flagged_fields(batch_size: int = 10):
    """
    Update Flagged fields based on OCR data using parse_ocr_data.js.
    
    Args:
        batch_size: Batch size for processing
    """
    logger.info(f"Updating Flagged fields with batch size: {batch_size}")
    
    # Run with onlyUnprocessed=false to process all records in the last batch
    # This ensures we use the correct sensitive content type concatenation format
    cmd = ["node", "parse_ocr_data.js", str(batch_size), "false"]
    
    logger.info(f"Running command: {' '.join(cmd)}")
    
    # Run the parse_ocr_data.js script
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        logger.error(f"Error updating Flagged fields: {stderr.decode()}")
        return False
    
    logger.info(f"Flagged fields updated successfully")
    logger.info(stdout.decode())
    return True

async def get_folders(base_dir: str) -> List[str]:
    """
    Get a list of folders containing frames, sorted chronologically.
    
    Args:
        base_dir: Base directory to search
        
    Returns:
        List of folder paths
    """
    # Get folders containing screen recordings
    folders = sorted(glob.glob(os.path.join(base_dir, "screen_recording_*")))
    logger.info(f"Found {len(folders)} folders in {base_dir}")
    return folders

async def process_specific_folder(folder_path: str, limit: int = 10, batch_size: int = 10):
    """
    Process all frames in a specific folder.
    
    Args:
        folder_path: Path to folder containing frames
        limit: Maximum number of frames to process
        batch_size: Batch size for processing
    """
    logger.info(f"Processing folder: {folder_path}")
    
    # Process frames in the folder
    success = await process_frames(folder_path, limit, batch_size)
    
    if not success:
        logger.error(f"Failed to process frames in folder: {folder_path}")
        return False
    
    # Update Flagged fields
    success = await update_flagged_fields(batch_size)
    
    if not success:
        logger.error(f"Failed to update Flagged fields for folder: {folder_path}")
        return False
    
    logger.info(f"Successfully processed folder: {folder_path}")
    return True

async def main():
    parser = argparse.ArgumentParser(description="Run OCR on a batch of frames")
    parser.add_argument("--folder", "-f", help="Specific folder to process")
    parser.add_argument("--base-dir", "-d", default="/home/jason/Videos/screenRecordings", 
                       help="Base directory containing screen recording folders")
    parser.add_argument("--limit", "-l", type=int, default=10, 
                       help="Maximum number of frames to process")
    parser.add_argument("--batch-size", "-b", type=int, default=10, 
                       help="Batch size for processing")
    
    args = parser.parse_args()
    
    if args.folder:
        # Process a specific folder
        await process_specific_folder(args.folder, args.limit, args.batch_size)
    else:
        # Get the most recent folder
        folders = await get_folders(args.base_dir)
        if not folders:
            logger.error(f"No folders found in {args.base_dir}")
            return 1
        
        # Process the most recent folder by default
        most_recent_folder = folders[-1]
        logger.info(f"Processing most recent folder: {most_recent_folder}")
        await process_specific_folder(most_recent_folder, args.limit, args.batch_size)
    
    return 0

if __name__ == "__main__":
    asyncio.run(main()) 