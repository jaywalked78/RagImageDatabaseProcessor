"""
Script to run sequential processing of frames, sorted by folder path.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from src.integrations.google_drive import GoogleDriveClient
from src.integrations.airtable import AirtableClient
from src.integrations.sequential_processor import SequentialProcessor
from PIL import Image
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sequential_test")

# Load environment variables
load_dotenv()

# Simple dummy processor function for testing
async def dummy_process_frame(image, metadata):
    """Dummy processor that just logs information about the frame."""
    folder_path = metadata.get('FolderPath', 'Unknown Folder')
    logger.info(f"Processing frame from folder: {folder_path}")
    logger.info(f"Frame: {metadata.get('frame_number')} from video {metadata.get('video_id')}")
    logger.info(f"Image size: {image.size}, format: {image.format}")
    return True

async def run_sequential_test(max_frames=5):
    """Run sequential processing test, limited to a few frames."""
    try:
        # Initialize clients
        logger.info("Initializing Google Drive and Airtable clients...")
        google_drive_client = GoogleDriveClient()
        airtable_client = AirtableClient()
        
        # Create sequential processor with dummy processor
        logger.info("Creating sequential processor...")
        processor = SequentialProcessor(
            process_frame_func=dummy_process_frame,
            airtable_client=airtable_client,
            google_drive_client=google_drive_client,
            download_to_disk=False  # Process in memory
        )
        
        # Process frames sequentially
        logger.info(f"Starting sequential processing (limited to {max_frames} frames)...")
        result = await processor.process_frames(
            max_frames=max_frames,  # Process just a few frames
            update_airtable=False,  # Don't update Airtable (to avoid marking as processed)
            folder_path_field="FolderPath"  # Field to sort by
        )
        
        # Print results
        logger.info("Sequential processing completed:")
        logger.info(f"  Total frames: {result['total_frames']}")
        logger.info(f"  Successful: {result['successful']}")
        logger.info(f"  Failed: {result['failed']}")
        logger.info(f"  Elapsed time: {result['elapsed_seconds']:.2f} seconds")
        
        return result['total_frames'] > 0
        
    except Exception as e:
        logger.error(f"Error in sequential test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Testing sequential processing pipeline...")
    
    # Get max frames from command line if provided
    max_frames = 5
    if len(sys.argv) > 1:
        try:
            max_frames = int(sys.argv[1])
        except ValueError:
            print(f"Invalid max_frames value. Using default: {max_frames}")
    
    # Run the async test
    success = asyncio.run(run_sequential_test(max_frames))
    
    if success:
        print("✅ Sequential processing test successful!")
        sys.exit(0)
    else:
        print("❌ Sequential processing test failed. Please check the logs for details.")
        sys.exit(1) 