"""
Batch processor for importing frames from Airtable and Google Drive.
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Callable
import asyncio
import concurrent.futures
from functools import partial
from io import BytesIO
from pathlib import Path
import tempfile
import json

from tqdm import tqdm
from PIL import Image
import numpy as np

from integrations.google_drive import GoogleDriveClient
from integrations.airtable import AirtableClient

# Get a logger for this module
logger = logging.getLogger("logicLoom")

# Required fields from Airtable (these should match the column names)
DRIVE_FILE_ID_FIELD = os.getenv('DRIVE_FILE_ID_FIELD', 'DriveFileID')
FRAME_NUMBER_FIELD = os.getenv('FRAME_NUMBER_FIELD', 'FrameNumber')
VIDEO_ID_FIELD = os.getenv('VIDEO_ID_FIELD', 'VideoID')
TIMESTAMP_FIELD = os.getenv('TIMESTAMP_FIELD', 'Timestamp')
TITLE_FIELD = os.getenv('TITLE_FIELD', 'Title')
PROCESSED_FIELD = os.getenv('PROCESSED_FIELD', 'Processed')

# Additional configuration
MAX_WORKERS = int(os.getenv('MAX_WORKERS', '4'))
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '20'))  # Process this many frames at once
TEMPDIR = os.getenv('TEMP_DIR', tempfile.gettempdir())


class BatchProcessor:
    """Processor for batches of frames from Airtable and Google Drive."""
    
    def __init__(self, process_frame_func: Callable, 
                 airtable_client: Optional[AirtableClient] = None, 
                 google_drive_client: Optional[GoogleDriveClient] = None,
                 download_to_disk: bool = False,
                 temp_dir: Optional[str] = None):
        """
        Initialize the batch processor.
        
        Args:
            process_frame_func: Function that processes a single frame
                                Signature: (image_data, metadata) -> bool
            airtable_client: Optional pre-initialized AirtableClient
            google_drive_client: Optional pre-initialized GoogleDriveClient
            download_to_disk: Whether to download files to disk (True) or memory (False)
            temp_dir: Directory to use for temporary files if download_to_disk is True
        """
        try:
            self.process_frame_func = process_frame_func
            self.airtable_client = airtable_client or AirtableClient()
            self.google_drive_client = google_drive_client or GoogleDriveClient()
            self.download_to_disk = download_to_disk
            self.temp_dir = temp_dir or TEMPDIR
            
            # Ensure temp directory exists
            if self.download_to_disk:
                os.makedirs(self.temp_dir, exist_ok=True)
                
            logger.info("BatchProcessor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize BatchProcessor: {str(e)}")
            raise

    async def process_batch(self, batch_size: int = BATCH_SIZE, 
                           max_batches: Optional[int] = None,
                           processed_field: str = PROCESSED_FIELD,
                           update_airtable: bool = True) -> Dict[str, Any]:
        """
        Process a batch of frames.
        
        Args:
            batch_size: Number of frames to process in each batch
            max_batches: Maximum number of batches to process
            processed_field: Field name in Airtable that indicates if a frame has been processed
            update_airtable: Whether to update the processed status in Airtable
            
        Returns:
            Dictionary with statistics about the batch processing
        """
        try:
            start_time = time.time()
            
            # Get batch of unprocessed frames from Airtable
            frames = self.airtable_client.get_frame_metadata_batch(
                batch_size=batch_size,
                processed_field=processed_field,
                processed_value=False,
                max_batches=max_batches
            )
            
            if not frames:
                logger.info("No unprocessed frames found")
                return {
                    "total_frames": 0,
                    "successful": 0,
                    "failed": 0,
                    "elapsed_seconds": time.time() - start_time
                }
            
            logger.info(f"Processing {len(frames)} frames")
            
            # Set up progress tracking
            successful = 0
            failed = 0
            
            # Use a thread pool for downloading and processing frames
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = []
                
                # Submit tasks to the thread pool
                for frame in frames:
                    future = executor.submit(
                        self._process_single_frame,
                        frame,
                        processed_field,
                        update_airtable
                    )
                    futures.append(future)
                
                # Process results as they complete
                for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing frames"):
                    result = future.result()
                    if result:
                        successful += 1
                    else:
                        failed += 1
            
            elapsed_time = time.time() - start_time
            logger.info(f"Batch processing completed in {elapsed_time:.2f} seconds")
            logger.info(f"Processed {len(frames)} frames: {successful} successful, {failed} failed")
            
            # Return statistics
            return {
                "total_frames": len(frames),
                "successful": successful,
                "failed": failed,
                "elapsed_seconds": elapsed_time
            }
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            raise

    def _process_single_frame(self, frame: Dict[str, Any], 
                              processed_field: str, 
                              update_airtable: bool) -> bool:
        """
        Process a single frame.
        
        Args:
            frame: Airtable record for the frame
            processed_field: Field name in Airtable that indicates if a frame has been processed
            update_airtable: Whether to update the processed status in Airtable
            
        Returns:
            True if successful, False otherwise
        """
        frame_id = frame['id']
        fields = frame['fields']
        
        # Check for required fields
        if DRIVE_FILE_ID_FIELD not in fields:
            logger.error(f"Frame {frame_id} missing required field: {DRIVE_FILE_ID_FIELD}")
            return False
        
        drive_file_id = fields[DRIVE_FILE_ID_FIELD]
        
        try:
            # Extract metadata for the frame
            metadata = {
                "airtable_id": frame_id,
                "frame_number": fields.get(FRAME_NUMBER_FIELD),
                "video_id": fields.get(VIDEO_ID_FIELD),
                "timestamp": fields.get(TIMESTAMP_FIELD),
                "title": fields.get(TITLE_FIELD),
                "source": "airtable",
                "drive_file_id": drive_file_id
            }
            
            # Download the image from Google Drive
            if self.download_to_disk:
                # Download to disk
                file_path = self.google_drive_client.download_file(
                    file_id=drive_file_id,
                    output_path=os.path.join(self.temp_dir, f"{drive_file_id}.jpg")
                )
                
                # Open the image file
                with Image.open(file_path) as img:
                    # Process the frame using the provided function
                    success = self.process_frame_func(img, metadata)
                    
                # Clean up the temp file
                try:
                    os.remove(file_path)
                except:
                    pass
            else:
                # Download to memory
                file_content, mime_type = self.google_drive_client.download_file_to_memory(
                    file_id=drive_file_id
                )
                
                # Open the image from memory
                img = Image.open(BytesIO(file_content))
                
                # Process the frame using the provided function
                success = self.process_frame_func(img, metadata)
                
                # Close the image
                img.close()
            
            # Update Airtable record if requested
            if update_airtable and success:
                self.airtable_client.update_record(
                    record_id=frame_id,
                    fields={processed_field: True}
                )
                
            return success
            
        except Exception as e:
            logger.error(f"Error processing frame {frame_id}: {str(e)}")
            return False
    
    async def process_all(self, batch_size: int = BATCH_SIZE, 
                         max_frames: Optional[int] = None,
                         processed_field: str = PROCESSED_FIELD,
                         update_airtable: bool = True) -> Dict[str, Any]:
        """
        Process all unprocessed frames.
        
        Args:
            batch_size: Number of frames to process in each batch
            max_frames: Maximum number of frames to process
            processed_field: Field name in Airtable that indicates if a frame has been processed
            update_airtable: Whether to update the processed status in Airtable
            
        Returns:
            Dictionary with statistics about the processing
        """
        start_time = time.time()
        total_processed = 0
        total_successful = 0
        total_failed = 0
        
        max_batches = None
        if max_frames:
            max_batches = (max_frames + batch_size - 1) // batch_size  # ceiling division
        
        batch_num = 1
        
        while True:
            logger.info(f"Processing batch {batch_num}")
            
            result = await self.process_batch(
                batch_size=batch_size,
                max_batches=1,  # Process one batch at a time
                processed_field=processed_field,
                update_airtable=update_airtable
            )
            
            # Update totals
            total_processed += result["total_frames"]
            total_successful += result["successful"]
            total_failed += result["failed"]
            
            # Check if we've processed all available frames
            if result["total_frames"] == 0:
                logger.info("No more unprocessed frames found")
                break
                
            # Check if we've reached the max_frames limit
            if max_frames and total_processed >= max_frames:
                logger.info(f"Reached maximum frames limit of {max_frames}")
                break
                
            # Increment batch number
            batch_num += 1
            
            # Check if we've reached the max_batches limit
            if max_batches and batch_num > max_batches:
                logger.info(f"Reached maximum batch limit of {max_batches}")
                break
                
            # Add a small delay between batches
            await asyncio.sleep(1)
        
        elapsed_time = time.time() - start_time
        logger.info(f"All processing completed in {elapsed_time:.2f} seconds")
        logger.info(f"Processed {total_processed} frames: {total_successful} successful, {total_failed} failed")
        
        # Return statistics
        return {
            "total_frames": total_processed,
            "successful": total_successful,
            "failed": total_failed,
            "elapsed_seconds": elapsed_time
        } 