"""
Sequential processor for importing frames from Airtable and Google Drive.
This processes frames one at a time to ensure consistent embedding quality.
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Callable
import asyncio
from io import BytesIO
from pathlib import Path

from tqdm import tqdm
from PIL import Image

from src.integrations.google_drive import GoogleDriveClient
from src.integrations.airtable import AirtableClient
from src.config.settings import (
    TEMP_DIR,
    DRIVE_FILE_ID_FIELD,
    FRAME_NUMBER_FIELD,
    VIDEO_ID_FIELD,
    TIMESTAMP_FIELD,
    TITLE_FIELD,
    PROCESSED_FIELD,
    ConfigError
)

# Get a logger for this module
logger = logging.getLogger("logicLoom.integrations.sequential_processor")


class SequentialProcessor:
    """Processes frames from Airtable and Google Drive one at a time, sorted by folder path."""
    
    def __init__(self, process_frame_func: Callable, 
                 airtable_client: Optional[AirtableClient] = None, 
                 google_drive_client: Optional[GoogleDriveClient] = None,
                 download_to_disk: bool = False,
                 temp_dir: Optional[str] = None):
        """
        Initialize the sequential processor.
        
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
            self.temp_dir = temp_dir or TEMP_DIR
            
            # Ensure temp directory exists
            if self.download_to_disk:
                os.makedirs(self.temp_dir, exist_ok=True)
                
            logger.info("SequentialProcessor initialized")
        except ConfigError as e:
            logger.error(f"Configuration error in SequentialProcessor: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize SequentialProcessor: {str(e)}")
            raise
    
    async def process_frames(self, max_frames: Optional[int] = None,
                         processed_field: str = None,
                         update_airtable: bool = True,
                         folder_path_field: str = "FolderPath") -> Dict[str, Any]:
        """
        Process all unprocessed frames one at a time, sorted by folder path.
        
        Args:
            max_frames: Maximum number of frames to process in total
            processed_field: Field name in Airtable that tracks processing status
            update_airtable: Whether to update the processed status in Airtable
            folder_path_field: Field name in Airtable that contains the folder path
            
        Returns:
            Dictionary with statistics about the overall processing
        """
        try:
            # Use provided values or defaults from config
            processed_field = processed_field or PROCESSED_FIELD
            
            start_time = time.time()
            
            # Get all unprocessed frames from Airtable
            frames = self.airtable_client.get_frame_metadata_batch(
                processed_field=processed_field,
                processed_value=False,
                max_batches=None  # Get all unprocessed frames
            )
            
            if not frames:
                logger.info("No unprocessed frames found")
                return {
                    "total_frames": 0,
                    "successful": 0,
                    "failed": 0,
                    "elapsed_seconds": time.time() - start_time
                }
            
            # Sort frames by folder path
            frames.sort(key=lambda x: x.get('fields', {}).get(folder_path_field, ''))
            
            # Apply max_frames limit if specified
            if max_frames is not None and max_frames < len(frames):
                frames = frames[:max_frames]
                logger.info(f"Limited to processing {max_frames} frames")
            
            logger.info(f"Processing {len(frames)} frames sequentially, sorted by {folder_path_field}")
            
            # Process frames one at a time
            successful = 0
            failed = 0
            
            for frame in tqdm(frames, desc="Processing frames"):
                result = await self._process_single_frame(frame, processed_field, update_airtable)
                if result:
                    successful += 1
                else:
                    failed += 1
            
            elapsed_time = time.time() - start_time
            logger.info(f"Sequential processing completed in {elapsed_time:.2f} seconds")
            logger.info(f"Processed {len(frames)} frames: {successful} successful, {failed} failed")
            
            # Return statistics
            return {
                "total_frames": len(frames),
                "successful": successful,
                "failed": failed,
                "elapsed_seconds": elapsed_time
            }
            
        except Exception as e:
            logger.error(f"Error in sequential processing: {str(e)}")
            elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
            return {
                "total_frames": len(frames) if 'frames' in locals() else 0,
                "successful": successful if 'successful' in locals() else 0,
                "failed": failed if 'failed' in locals() else 0,
                "elapsed_seconds": elapsed_time,
                "error": str(e)
            }
    
    async def _process_single_frame(self, frame: Dict[str, Any], 
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
            
            # Add all other fields as extras
            for field_name, field_value in fields.items():
                if field_name not in {DRIVE_FILE_ID_FIELD, FRAME_NUMBER_FIELD, VIDEO_ID_FIELD, 
                                      TIMESTAMP_FIELD, TITLE_FIELD, PROCESSED_FIELD}:
                    metadata[field_name] = field_value
            
            # Download the image from Google Drive
            if self.download_to_disk:
                # Download to disk
                file_path = self.google_drive_client.download_file(
                    file_id=drive_file_id,
                    output_path=os.path.join(self.temp_dir, f"{drive_file_id}.jpg")
                )
                
                # Open the image file
                with Image.open(file_path) as img:
                    # Process the frame
                    success = await self.process_frame_func(img, metadata)
                
                # Clean up the file if desired
                # os.unlink(file_path)
            else:
                # Download to memory
                file_bytes, mime_type = self.google_drive_client.download_file_to_memory(drive_file_id)
                
                # Open the image from bytes
                with Image.open(BytesIO(file_bytes)) as img:
                    # Process the frame
                    success = await self.process_frame_func(img, metadata)
            
            # Update Airtable if successful and requested
            if success and update_airtable:
                self.airtable_client.mark_record_as_processed(frame_id, processed_field)
                
            return success
        except Exception as e:
            logger.error(f"Error processing frame {frame_id}: {str(e)}")
            return False 