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
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.integrations.google_drive import GoogleDriveClient
from src.integrations.airtable import AirtableClient
from src.db.database_client import DatabaseClient # Assuming DatabaseClient is correctly referenced
from src.processing.metadata_processor import generate_structured_metadata, create_text_representation_for_embedding
from src.models.embedding_client import get_embeddings, get_embedding_dimension
from src.config.settings import (
    DRIVE_FILE_ID_FIELD,
    FRAME_FILENAME_FIELD, # Use this field from config
    PROCESSED_FIELD,
    MAX_WORKERS,
    BATCH_SIZE,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    FRAME_BASE_DIR, # Use this for local file path construction
    TEMP_DIR
)

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Processor for batches of frames from Airtable and Google Drive."""
    
    def __init__(self, 
                 airtable_client: Optional[AirtableClient] = None, 
                 google_drive_client: Optional[GoogleDriveClient] = None,
                 db_client: Optional[DatabaseClient] = None,
                 download_to_disk: bool = False,
                 temp_dir: Optional[str] = None):
        """
        Initialize the batch processor.
        
        Args:
            airtable_client: Optional pre-initialized AirtableClient.
            google_drive_client: Optional pre-initialized GoogleDriveClient.
            db_client: Optional pre-initialized DatabaseClient.
            download_to_disk: Whether to download files to disk (True) or memory (False).
            temp_dir: Directory to use for temporary files if download_to_disk is True.
        """
        try:
            self.airtable_client = airtable_client or AirtableClient()
            self.google_drive_client = google_drive_client or GoogleDriveClient()
            # Ensure DB client is initialized here or passed in
            self.db_client = db_client or DatabaseClient()
            if not self.db_client.check_connection(): # Check if already connected
                 self.db_client.connect() # Connect only if not already connected

            self.download_to_disk = download_to_disk
            self.temp_dir = temp_dir or TEMP_DIR
            
            # Initialize Text Splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                length_function=len,
                is_separator_regex=False,
            )
            
            # Ensure temp directory exists
            if self.download_to_disk:
                os.makedirs(self.temp_dir, exist_ok=True)
                
            logger.info(f"BatchProcessor initialized. Download to disk: {self.download_to_disk}, Temp dir: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize BatchProcessor: {e}", exc_info=True)
            # Close db connection if initialization fails after opening
            if self.db_client:
                 self.db_client.close()
            raise

    async def process_batch(self, batch_size: int = BATCH_SIZE, 
                           max_batches: Optional[int] = None,
                           processed_field: str = PROCESSED_FIELD,
                           update_airtable: bool = True) -> Dict[str, Any]:
        """
        Process a batch of frames from Airtable.
        Fetches records, processes them concurrently, and updates status.
        """
        start_time = time.time()
        total_processed = 0
        total_succeeded = 0
        total_failed = 0
        airtable_records_processed = set()

        try:
            # Fetch batch of unprocessed frames from Airtable
            # Note: AirtableClient might need adjustment if max_batches logic changes
            frames_to_process = self.airtable_client.get_frame_metadata_batch(
                batch_size=batch_size,
                processed_field=processed_field,
                processed_value=False,
                max_batches=max_batches
            )
            
            if not frames_to_process:
                logger.info("No unprocessed frames found in Airtable.")
                return {
                    "total_frames_fetched": 0,
                    "total_frames_processed": 0,
                    "successful_frames": 0,
                    "failed_frames": 0,
                    "elapsed_seconds": time.time() - start_time
                }
            
            total_frames_fetched = len(frames_to_process)
            logger.info(f"Fetched {total_frames_fetched} frames from Airtable for processing.")
            
            # Process frames concurrently
            loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                # Pass necessary clients/objects to the processing function
                # Use partial to pre-fill arguments for the synchronous function
                process_func = partial(self._process_single_item_sync, 
                                       db_client=self.db_client, # Pass the db_client instance
                                       google_drive_client=self.google_drive_client)

                futures = [
                    loop.run_in_executor(executor, process_func, frame)
                    for frame in frames_to_process
                ]
                
                results = []
                # Use tqdm for progress bar
                for future in tqdm(asyncio.as_completed(futures), total=len(futures), desc="Processing Frames"):
                    try:
                        result = await future
                        results.append(result)
                    except Exception as e:
                        # Log errors from the future execution itself
                        logger.error(f"Error processing frame future: {e}", exc_info=True)
                        results.append((None, False)) # Indicate failure with None ID

            # Tally results
            for airtable_id, success in results:
                if airtable_id:
                    airtable_records_processed.add(airtable_id)
                    if success:
                        total_succeeded += 1
                    else:
                        total_failed += 1
                else:
                    # This indicates a failure within the future execution, not tied to a specific ID
                    total_failed += 1 # Count as failure, ID might be logged separately
            
            total_processed = total_succeeded + total_failed
            logger.info(f"Processing complete for batch. Succeeded: {total_succeeded}, Failed: {total_failed} out of {total_frames_fetched} fetched.")

            # Update Airtable status if requested
            if update_airtable and total_succeeded > 0:
                logger.info(f"Updating {total_succeeded} successfully processed records in Airtable...")
                updates = []
                for airtable_id, success in results:
                     if airtable_id and success:
                         updates.append({'id': airtable_id, 'fields': {processed_field: True}})
                
                if updates:
                    # Consider making Airtable update async or handle potential blocking
                    update_success = self.airtable_client.batch_update_records(updates)
                    if update_success:
                        logger.info("Airtable records updated successfully.")
                    else:
                        logger.error("Failed to update some records in Airtable.")
                        # Potentially retry failed updates or log specific IDs

        except Exception as e:
            logger.error(f"Error during batch processing execution: {e}", exc_info=True)
            # Fall through to finally block for cleanup
        finally:
            # Ensure DB connection is closed after processing completes or fails
            if self.db_client:
                 self.db_client.close()
                 logger.info("Database connection closed.")

        return {
            "total_frames_fetched": total_frames_fetched,
            "total_frames_processed": total_processed, # Reflects items attempted
            "successful_frames": total_succeeded,
            "failed_frames": total_failed,
            "elapsed_seconds": time.time() - start_time
        }

    # Note: This is now a static or class method if it doesn't need self directly,
    # but keeping it as an instance method allows easy access to self.text_splitter.
    # It now accepts db_client and google_drive_client as arguments.
    def _process_single_item_sync(self, airtable_record: Dict[str, Any], 
                                  db_client: DatabaseClient, 
                                  google_drive_client: GoogleDriveClient) -> Tuple[Optional[str], bool]:
        """Synchronous function to process a single Airtable record. Designed for ThreadPoolExecutor."""
        airtable_id = airtable_record.get('id')
        if not airtable_id:
             logger.error("Airtable record missing 'id'. Cannot process.")
             return None, False # Return None ID for error tracking
        try:
            logger.debug(f"Starting processing for Airtable record: {airtable_id}")
            raw_metadata = airtable_record.get('fields', {})
            
            # --- 1. Get Frame Path/Identifier --- 
            relative_frame_path = raw_metadata.get(FRAME_FILENAME_FIELD)
            if not relative_frame_path:
                logger.warning(f"Skipping record {airtable_id}: Missing '{FRAME_FILENAME_FIELD}' field.")
                return airtable_id, False

            # --- 2. Load Frame Data --- 
            drive_file_id = raw_metadata.get(DRIVE_FILE_ID_FIELD)
            frame_data_bytes: Optional[bytes] = None # Store raw bytes for embedding input
            # Decide load strategy (Drive vs Local)
            if drive_file_id:
                 try:
                     logger.debug(f"Attempting to load frame from Google Drive: {drive_file_id}")
                     frame_data_bytes, mime_type = google_drive_client.download_file_to_memory(drive_file_id)
                     logger.debug(f"Loaded frame data bytes ({len(frame_data_bytes)} bytes) for {airtable_id} (Drive ID: {drive_file_id}) Type: {mime_type}")
                 except Exception as drive_err:
                     logger.error(f"Failed to load frame from Google Drive {drive_file_id} for {airtable_id}: {drive_err}")
                     return airtable_id, False
            elif FRAME_BASE_DIR and relative_frame_path:
                 local_path = Path(FRAME_BASE_DIR) / relative_frame_path
                 if local_path.exists():
                     try:
                         logger.debug(f"Attempting to load frame from local path: {local_path}")
                         with open(local_path, 'rb') as f:
                             frame_data_bytes = f.read() # Load as bytes
                         logger.debug(f"Loaded frame data bytes ({len(frame_data_bytes)} bytes) for {airtable_id} from {local_path}")
                     except Exception as local_err:
                         logger.error(f"Failed to load frame from local path {local_path} for {airtable_id}: {local_err}")
                         return airtable_id, False
                 else:
                      logger.warning(f"Skipping {airtable_id}: Local frame path not found {local_path}")
                      return airtable_id, False
            else:
                 logger.warning(f"Skipping {airtable_id}: Neither Drive ID nor local path info available/valid.")
                 return airtable_id, False
            
            # Ensure frame_data_bytes is not None before proceeding
            if frame_data_bytes is None:
                logger.error(f"Frame data bytes are None for {airtable_id} after loading attempts.")
                return airtable_id, False
                
            # --- 3. Generate Structured Metadata (using LLM) --- 
            logger.debug(f"Generating structured metadata for {airtable_id}...")
            # Pass frame_data_bytes to the metadata processor. It can decide how to handle them (e.g., load into PIL if needed by LLM).
            structured_metadata = generate_structured_metadata(
                frame_data=frame_data_bytes, 
                raw_metadata=raw_metadata,
                airtable_id=airtable_id,
                frame_path_rel=relative_frame_path
            )

            # --- 4. Create Text Representation for Embedding --- 
            text_to_embed = create_text_representation_for_embedding(structured_metadata)
            if not text_to_embed:
                logger.warning(f"Skipping {airtable_id}: No text generated for embedding.")
                return airtable_id, False
            logger.debug(f"Generated text for embedding (length {len(text_to_embed)}) for {airtable_id}.")

            # --- 5. Perform Chunking --- 
            chunks = self.text_splitter.split_text(text_to_embed)
            logger.debug(f"Split text into {len(chunks)} chunks for {airtable_id}.")
            if not chunks:
                 logger.warning(f"Skipping {airtable_id}: Text splitting resulted in no chunks.")
                 return airtable_id, False

            # --- 6. Generate Embeddings for Chunks + Image --- 
            # Prepare the single input tuple for the batch embedding function
            multimodal_input = [(chunks, frame_data_bytes)] # List containing one tuple: ([chunk list], image_bytes)
            
            embedding_results = get_embeddings(multimodal_input)
            
            # Check if embedding generation was successful and returned the expected single embedding
            if not embedding_results or len(embedding_results) != 1:
                logger.error(f"Failed to generate multimodal embedding for {airtable_id} or unexpected result format. Embedding result: {embedding_results}")
                return airtable_id, False
            
            # Since we sent one item, we expect one embedding vector back
            # Note: The current RAG plan implies one embedding per *chunk*. 
            # However, the voyage-multimodal-3 API call processes the *entire* input sequence 
            # (image + all chunks) into a *single* vector representing the whole sequence.
            # We need to decide how to store this. Storing the single vector with each chunk might be redundant.
            # Option 1: Store the single vector with EACH chunk record (as implemented below).
            # Option 2: Store the single vector once, perhaps in a separate frame metadata table (requires schema change).
            # Option 3: Generate separate embeddings for each chunk (text-only) and maybe one for the image.
            # Let's proceed with Option 1 for now, storing the combined embedding with each chunk.
            combined_embedding = embedding_results[0]
            logger.debug(f"Generated 1 combined multimodal embedding for {airtable_id}.")

            # --- 7. Prepare Data for Batch Insert --- 
            chunks_to_insert = []
            for i, chunk_text in enumerate(chunks):
                chunk_insert_data = (
                    airtable_id,
                    relative_frame_path, # Store relative path
                    i, # chunk_sequence_id (0-indexed)
                    chunk_text,
                    structured_metadata, # Store the full structured metadata with each chunk
                    combined_embedding # Store the single combined embedding for this frame with each chunk
                )
                chunks_to_insert.append(chunk_insert_data)
            
            # --- 8. Batch Insert Chunks --- 
            if not db_client or not db_client.check_connection():
                 logger.error(f"Database connection lost for worker processing {airtable_id}. Cannot insert chunks.")
                 return airtable_id, False 
                      
            insert_success = db_client.batch_insert_frame_chunks(chunks_to_insert)
            if not insert_success:
                logger.error(f"Failed to insert chunks into database for {airtable_id}.")
                return airtable_id, False

            logger.info(f"Successfully processed and stored {len(chunks)} chunks for Airtable record: {airtable_id}")
            return airtable_id, True

        except Exception as e:
            # Catch any unexpected error during the processing of this single item
            logger.error(f"Unhandled error processing Airtable record {airtable_id}: {e}", exc_info=True)
            return airtable_id, False # Return ID and failure status

    async def process_all(self, batch_size: int = None, 
                         max_frames: Optional[int] = None,
                         processed_field: str = None,
                         update_airtable: bool = True) -> Dict[str, Any]:
        """
        Process all unprocessed frames, potentially in multiple batches.
        
        Args:
            batch_size: Number of frames to process in each batch
            max_frames: Maximum number of frames to process in total
            processed_field: Field name in Airtable that tracks processing status
            update_airtable: Whether to update the processed status in Airtable
            
        Returns:
            Dictionary with statistics about the overall processing
        """
        # Use provided values or defaults from config
        batch_size = batch_size or BATCH_SIZE
        processed_field = processed_field or PROCESSED_FIELD
        
        # Calculate max_batches if max_frames is provided
        max_batches = None
        if max_frames is not None:
            max_batches = (max_frames + batch_size - 1) // batch_size  # Ceiling division
        
        start_time = time.time()
        total_processed = 0
        total_successful = 0
        total_failed = 0
        batches_processed = 0
        
        # Process in batches
        while True:
            # Check max_batches limit
            if max_batches is not None and batches_processed >= max_batches:
                 logger.info(f"Reached maximum batch limit of {max_batches}. Stopping.")
                 break
                 
            logger.info(f"Starting batch {batches_processed + 1}...")
            # Process a batch
            # Pass max_batches=1 to process_batch to handle one Airtable fetch at a time
            batch_result = await self.process_batch(
                batch_size=batch_size,
                max_batches=1, # Fetch one batch worth of records from Airtable
                processed_field=processed_field,
                update_airtable=update_airtable
            )
            batches_processed += 1
            
            # Update totals
            total_processed += batch_result['total_frames_processed']
            total_successful += batch_result['successful_frames']
            total_failed += batch_result['failed_frames']
            
            # Break if no frames were fetched in the last batch call
            if batch_result['total_frames_fetched'] == 0:
                logger.info("No more frames fetched from Airtable. Stopping.")
                break
                
            # Break if we've processed enough frames based on max_frames limit
            # Use total_processed which reflects items attempted within the batches run so far.
            if max_frames is not None and total_processed >= max_frames:
                logger.info(f"Processed {total_processed} frames, reaching or exceeding maximum frames limit of {max_frames}. Stopping.")
                break
                
            # Sleep briefly between batches to avoid overwhelming downstream systems
            await asyncio.sleep(1.0) # Increased sleep time between full batches
        
        elapsed_time = time.time() - start_time
        logger.info(f"All processing completed in {elapsed_time:.2f} seconds across {batches_processed} batches.")
        logger.info(f"Total frames attempted: {total_processed}. Successful: {total_successful}, Failed: {total_failed}")
        
        # Return overall statistics
        return {
            "total_frames_processed": total_processed,
            "successful_frames": total_successful,
            "failed_frames": total_failed,
            "elapsed_seconds": elapsed_time
        } 