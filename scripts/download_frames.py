#!/usr/bin/env python3
"""
Download Frames - Command line tool for downloading frames from Google Drive.

This script handles:
1. Downloading frames from Google Drive
2. Organizing downloaded frames in local directories
3. Optional preprocessing of downloaded frames
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Import project modules
from src.api.google_drive import GoogleDriveDownloader

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("download_frames")

async def download_from_drive(
    drive_url: str,
    output_dir: Optional[str] = None,
    file_pattern: str = "*",
    limit: Optional[int] = None,
    create_metadata: bool = False
) -> Dict[str, Any]:
    """
    Download frames from Google Drive.
    
    Args:
        drive_url: Google Drive URL to folder or shared link
        output_dir: Directory to save downloaded files
        file_pattern: Pattern to filter files
        limit: Maximum number of files to download
        create_metadata: Whether to create basic metadata files
        
    Returns:
        Dictionary with download results
    """
    # Initialize Google Drive downloader
    downloader = GoogleDriveDownloader()
    
    # Download files
    logger.info(f"Downloading files from Google Drive: {drive_url}")
    logger.info(f"File pattern: {file_pattern}, Limit: {limit or 'No limit'}")
    
    result = await downloader.download_folder(
        drive_url=drive_url,
        output_dir=output_dir,
        file_pattern=file_pattern,
        limit=limit
    )
    
    if not result:
        logger.error("Failed to download files from Google Drive")
        return {"success": False, "error": "Download failed"}
    
    # Get downloaded files info
    download_dir = result.get("download_dir")
    files = result.get("files", [])
    
    logger.info(f"Downloaded {len(files)} files to {download_dir}")
    
    # Optionally create basic metadata files
    if create_metadata:
        logger.info("Creating basic metadata files...")
        metadata_dir = os.path.join(download_dir, "metadata")
        os.makedirs(metadata_dir, exist_ok=True)
        
        for file_info in files:
            file_path = file_info.get("local_path")
            file_name = os.path.basename(file_path)
            file_id = file_info.get("id", "unknown")
            
            # Create a basic metadata file
            metadata_path = os.path.join(metadata_dir, f"{file_name.split('.')[0]}.json")
            with open(metadata_path, "w") as f:
                import json
                json.dump({
                    "file_name": file_name,
                    "drive_id": file_id,
                    "drive_url": f"https://drive.google.com/file/d/{file_id}/view",
                    "download_time": result.get("timestamp"),
                    "mime_type": file_info.get("mimeType", "unknown"),
                    "size": file_info.get("size", 0),
                    "created_time": file_info.get("createdTime", "unknown"),
                    "modified_time": file_info.get("modifiedTime", "unknown")
                }, f, indent=2)
    
    return {
        "success": True,
        "download_dir": download_dir,
        "files": files,
        "total_files": len(files)
    }

async def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Download frames from Google Drive")
    
    # Input options
    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument("--drive-url", required=True, help="Google Drive URL to folder or shared link")
    input_group.add_argument("--pattern", default="*.jpg", help="Pattern to filter files (default: *.jpg)")
    input_group.add_argument("--limit", type=int, help="Maximum number of files to download")
    
    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument("--output-dir", help="Directory to save downloaded files")
    output_group.add_argument("--create-metadata", action="store_true", help="Create basic metadata files for downloaded frames")
    
    args = parser.parse_args()
    
    # Download frames
    result = await download_from_drive(
        drive_url=args.drive_url,
        output_dir=args.output_dir,
        file_pattern=args.pattern,
        limit=args.limit,
        create_metadata=args.create_metadata
    )
    
    if result.get("success", False):
        print("\nDownload summary:")
        print(f"  Downloaded {result.get('total_files', 0)} files")
        print(f"  Download directory: {result.get('download_dir', 'unknown')}")
        return 0
    else:
        print("\nDownload failed:")
        print(f"  Error: {result.get('error', 'Unknown error')}")
        return 1

if __name__ == "__main__":
    asyncio.run(main()) 