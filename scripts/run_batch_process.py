"""
Script to run a small batch processing job to test the pipeline.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from src.integrations.google_drive import GoogleDriveClient
from src.integrations.airtable import AirtableClient
from src.integrations.batch_processor import BatchProcessor
from PIL import Image
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("batch_test")

# Load environment variables
load_dotenv()

# Simple dummy processor function for testing
async def dummy_process_frame(image, metadata):
    """Dummy processor that just logs information about the frame."""
    logger.info(f"Processing frame: {metadata.get('frame_number')} from video {metadata.get('video_id')}")
    logger.info(f"Image size: {image.size}, format: {image.format}")
    logger.info(f"Metadata: {metadata}")
    return True

async def run_batch_test():
    """Run a small batch processing job to test the pipeline."""
    try:
        # Initialize clients
        logger.info("Initializing Google Drive and Airtable clients...")
        google_drive_client = GoogleDriveClient()
        airtable_client = AirtableClient()
        
        # Create batch processor with dummy processor
        logger.info("Creating batch processor...")
        processor = BatchProcessor(
            process_frame_func=dummy_process_frame,
            airtable_client=airtable_client,
            google_drive_client=google_drive_client,
            download_to_disk=False  # Process in memory
        )
        
        # Process a small batch
        logger.info("Starting batch processing...")
        result = await processor.process_batch(
            batch_size=2,  # Process just 2 frames
            max_batches=1,  # Just one batch
            update_airtable=False  # Don't update Airtable (to avoid marking as processed)
        )
        
        # Print results
        logger.info("Batch processing completed:")
        logger.info(f"  Total frames: {result['total_frames']}")
        logger.info(f"  Successful: {result['successful']}")
        logger.info(f"  Failed: {result['failed']}")
        logger.info(f"  Elapsed time: {result['elapsed_seconds']:.2f} seconds")
        
        return result['total_frames'] > 0
        
    except Exception as e:
        logger.error(f"Error in batch test: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Testing batch processing pipeline...")
    
    # Run the async test
    success = asyncio.run(run_batch_test())
    
    if success:
        print("✅ Batch processing test successful!")
        sys.exit(0)
    else:
        print("❌ Batch processing test failed. Please check the logs for details.")
        sys.exit(1) 