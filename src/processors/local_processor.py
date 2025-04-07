#!/usr/bin/env python3
"""
Local frame processor that uses a local database to minimize API calls.
This script downloads frames from Google Drive, stores metadata locally,
and processes frames with embeddings, making only API calls to Voyage for embeddings.
"""

import os
import sys
import json
import time
import asyncio
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import tempfile
import shutil

import numpy as np
from PIL import Image
from dotenv import load_dotenv

# Import our local database
from local_database import LocalDatabase

# Import necessary components from the original scripts
try:
    from test_chunk_embedding import ChunkEmbedder, process_metadata_text
except ImportError:
    print("Error: Could not import from test_chunk_embedding.py")
    print("Make sure this file is in the same directory as test_chunk_embedding.py")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("local_processor")

# Load environment variables
load_dotenv()

class LocalFrameProcessor:
    """Processes frames using a local database to minimize API calls."""
    
    def __init__(self, db_path: str = "frames_local.db", 
                 api_keys: Optional[List[str]] = None,
                 output_dir: Optional[str] = None):
        """Initialize the frame processor.
        
        Args:
            db_path: Path to local database file
            api_keys: List of Voyage API keys (optional, defaults to env vars)
            output_dir: Directory for storing downloaded frames (optional)
        """
        # Initialize local database
        self.db = LocalDatabase(db_path=db_path)
        
        # Initialize embedder
        self.embedder = ChunkEmbedder(api_keys=api_keys)
        
        # Create output directory if needed
        if output_dir:
            self.output_dir = output_dir
            os.makedirs(output_dir, exist_ok=True)
        else:
            self.output_dir = tempfile.mkdtemp(prefix="frame_processor_")
            logger.info(f"Created temporary output directory: {self.output_dir}")
    
    def close(self):
        """Close the database connection."""
        self.db.close()
    
    async def load_from_google_drive(self, folder_id: str, credentials_path: Optional[str] = None,
                                   file_pattern: Optional[str] = None, limit: Optional[int] = None,
                                   download: bool = True) -> Tuple[int, int]:
        """Load frames from Google Drive and store metadata locally.
        
        Args:
            folder_id: Google Drive folder ID
            credentials_path: Path to Google API credentials (optional)
            file_pattern: Pattern to filter files by (optional)
            limit: Maximum number of frames to download (optional)
            download: Whether to download the frames immediately (default: True)
            
        Returns:
            tuple: (number of frames added, number of frames downloaded)
        """
        # Load frames from Google Drive folder
        frames_added, _, download_dir = self.db.load_google_drive_folder(
            folder_id,
            credentials_path=credentials_path,
            download_dir=self.output_dir,
            file_pattern=file_pattern
        )
        
        # Download frames if requested
        frames_downloaded = 0
        if download and frames_added > 0:
            frames_downloaded = self.db.download_pending_frames(
                credentials_path=credentials_path,
                download_dir=self.output_dir,
                limit=limit
            )
        
        return frames_added, frames_downloaded
    
    async def process_frame(self, frame_id: int, chunk_size: int = 500, chunk_overlap: int = 50,
                          max_chunks: Optional[int] = None, force_reprocess: bool = False) -> bool:
        """Process a single frame.
        
        Args:
            frame_id: ID of the frame in the database
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            max_chunks: Maximum number of chunks to process (optional)
            force_reprocess: Force reprocessing even if already processed
            
        Returns:
            bool: True if processing was successful
        """
        # Get frame info
        frame = self.db.get_frame_by_id(frame_id)
        if not frame:
            logger.error(f"Frame with ID {frame_id} not found")
            return False
        
        frame_name = frame['frame_name']
        local_path = frame['local_path']
        
        # Skip if already processed and not forced
        if frame['processed'] and not force_reprocess:
            logger.info(f"Frame {frame_name} already processed, skipping (use --force to reprocess)")
            return True
        
        # Check if frame is downloaded
        if not local_path or not os.path.exists(local_path):
            logger.error(f"Frame {frame_name} not downloaded or local path invalid")
            return False
        
        logger.info(f"Processing frame: {frame_name}")
        
        # Load image
        try:
            image = Image.open(local_path)
            logger.info(f"Loaded image: {frame_name} ({image.width}x{image.height})")
        except Exception as e:
            logger.error(f"Error loading image {frame_name}: {e}")
            return False
        
        # Get metadata for the frame
        metadata_entries = self.db.get_metadata_for_frame(frame_id, metadata_type='airtable')
        
        # If no metadata found, try to process without it
        if not metadata_entries:
            logger.warning(f"No metadata found for frame {frame_name}, using frame name only")
            metadata_text = f"Frame: {frame_name}"
        else:
            # Parse JSON metadata and extract relevant fields
            metadata = json.loads(metadata_entries[0]['content'])
            metadata_text = process_metadata_text(metadata)
            logger.info(f"Found metadata for frame {frame_name}")
        
        # Process metadata into chunks
        chunks = self._chunk_text(metadata_text, chunk_size, chunk_overlap)
        
        if not chunks:
            logger.warning(f"No chunks generated for frame {frame_name}")
            return False
        
        # Limit number of chunks if specified
        if max_chunks and len(chunks) > max_chunks:
            logger.info(f"Limiting to {max_chunks} chunks (out of {len(chunks)})")
            chunks = chunks[:max_chunks]
        
        logger.info(f"Generated {len(chunks)} chunks for frame {frame_name}")
        
        # Store chunks in database
        chunk_ids = []
        for i, chunk in enumerate(chunks):
            chunk_id = self.db.add_chunk(frame_id, i, chunk)
            if chunk_id:
                chunk_ids.append((chunk_id, chunk))
        
        # Create embeddings for chunks
        successful_embeddings = 0
        for chunk_id, chunk_text in chunk_ids:
            logger.info(f"Creating embedding for chunk {chunk_id} (length: {len(chunk_text)})")
            
            try:
                # Create embedding
                embedding = await self.embedder.create_embedding(chunk_text)
                
                if embedding is not None:
                    # Store embedding in database
                    embedding_id = self.db.add_embedding(
                        chunk_id, 
                        self.embedder.model_name, 
                        embedding
                    )
                    
                    if embedding_id:
                        successful_embeddings += 1
                        logger.info(f"Stored embedding {embedding_id} for chunk {chunk_id}")
                    else:
                        logger.error(f"Failed to store embedding for chunk {chunk_id}")
                else:
                    logger.error(f"Failed to create embedding for chunk {chunk_id}")
            
            except Exception as e:
                logger.error(f"Error creating embedding for chunk {chunk_id}: {e}")
        
        # Mark frame as processed
        if successful_embeddings > 0:
            self.db.mark_frame_processed(frame_id)
            logger.info(f"Successfully processed frame {frame_name} with {successful_embeddings} embeddings")
            return True
        else:
            logger.error(f"Failed to process frame {frame_name}: no embeddings created")
            return False
    
    def _chunk_text(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """Split text into chunks with overlap.
        
        Args:
            text: Text to split
            chunk_size: Size of chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            list: List of text chunks
        """
        if not text:
            return []
        
        # Split text into paragraphs
        paragraphs = text.split('\n')
        
        # Initialize chunks
        chunks = []
        current_chunk = ""
        
        # Process paragraphs
        for para in paragraphs:
            if len(current_chunk) + len(para) + 1 <= chunk_size:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n" + para
                else:
                    current_chunk = para
            else:
                # Current chunk is full, start a new one
                if current_chunk:
                    chunks.append(current_chunk)
                    
                    # Start new chunk with overlap
                    words = current_chunk.split()
                    if len(words) > chunk_overlap:
                        overlap_text = " ".join(words[-chunk_overlap:])
                        current_chunk = overlap_text + "\n" + para
                    else:
                        current_chunk = para
                else:
                    # Handle the case where a single paragraph is larger than chunk_size
                    chunks.append(para[:chunk_size])
                    current_chunk = para[max(0, chunk_size - chunk_overlap):]
        
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    async def process_unprocessed_frames(self, limit: Optional[int] = None, 
                                       chunk_size: int = 500, chunk_overlap: int = 50,
                                       max_chunks: Optional[int] = None, 
                                       force_reprocess: bool = False,
                                       parallel: int = 1) -> Tuple[int, int]:
        """Process frames that haven't been processed yet.
        
        Args:
            limit: Maximum number of frames to process (optional)
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            max_chunks: Maximum number of chunks to process (optional)
            force_reprocess: Force reprocessing even if already processed
            parallel: Number of frames to process in parallel
            
        Returns:
            tuple: (number of frames processed successfully, number of frames that failed)
        """
        # Get unprocessed frames
        frames = self.db.get_unprocessed_frames(limit)
        
        if not frames:
            logger.info("No unprocessed frames found")
            return 0, 0
        
        logger.info(f"Found {len(frames)} unprocessed frames")
        
        # Process frames
        successful = 0
        failures = 0
        
        if parallel > 1:
            logger.info(f"Processing {len(frames)} frames with parallelism {parallel}")
            
            # Create tasks
            tasks = []
            for frame in frames:
                frame_id = frame['id']
                task = asyncio.create_task(self.process_frame(
                    frame_id,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    max_chunks=max_chunks,
                    force_reprocess=force_reprocess
                ))
                tasks.append((frame['frame_name'], task))
            
            # Wait for tasks in batches
            for i in range(0, len(tasks), parallel):
                batch = tasks[i:i+parallel]
                logger.info(f"Processing batch {i//parallel + 1} with {len(batch)} frames")
                
                for frame_name, task in batch:
                    try:
                        result = await task
                        if result:
                            successful += 1
                            logger.info(f"✅ Successfully processed frame {frame_name}")
                        else:
                            failures += 1
                            logger.error(f"❌ Failed to process frame {frame_name}")
                    except Exception as e:
                        failures += 1
                        logger.error(f"❌ Error processing frame {frame_name}: {e}")
        else:
            logger.info(f"Processing {len(frames)} frames sequentially")
            
            for frame in frames:
                frame_id = frame['id']
                frame_name = frame['frame_name']
                
                try:
                    result = await self.process_frame(
                        frame_id,
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap,
                        max_chunks=max_chunks,
                        force_reprocess=force_reprocess
                    )
                    
                    if result:
                        successful += 1
                        logger.info(f"✅ Successfully processed frame {frame_name}")
                    else:
                        failures += 1
                        logger.error(f"❌ Failed to process frame {frame_name}")
                        
                except Exception as e:
                    failures += 1
                    logger.error(f"❌ Error processing frame {frame_name}: {e}")
        
        logger.info(f"Processed {successful + failures} frames: {successful} successful, {failures} failed")
        return successful, failures
    
    async def export_to_postgres(self, batch_size: int = 20) -> Dict[str, int]:
        """Export embeddings to PostgreSQL.
        
        Args:
            batch_size: Number of embeddings to export in a batch
            
        Returns:
            dict: Stats about the export operation
        """
        from test_chunk_embedding import PostgresVectorStore
        
        logger.info("Exporting embeddings to PostgreSQL")
        
        # Initialize PostgreSQL store
        postgres_store = PostgresVectorStore()
        
        # Get pending uploads
        pending = self.db.get_pending_uploads('postgres')
        
        if not pending:
            logger.info("No pending uploads for PostgreSQL")
            return {'total': 0, 'success': 0, 'error': 0}
        
        logger.info(f"Found {len(pending)} embeddings to export to PostgreSQL")
        
        # Export in batches
        total = len(pending)
        success_count = 0
        error_count = 0
        
        for i in range(0, total, batch_size):
            batch = pending[i:i+batch_size]
            logger.info(f"Exporting batch {i//batch_size + 1}/{(total+batch_size-1)//batch_size}: {len(batch)} embeddings")
            
            for entry in batch:
                try:
                    # Extract data
                    embedding_id = entry['embedding_id']
                    frame_name = entry['frame_name']
                    chunk_content = entry['chunk_content']
                    frame_path = entry['frame_path']
                    folder_path = entry['folder_path']
                    embedding = entry['embedding']
                    
                    # Store in PostgreSQL
                    result = await postgres_store.store_vector_embedding(
                        embedding_id=str(embedding_id),
                        reference_id=str(entry['frame_id']),
                        reference_type='frame',
                        text_content=chunk_content,
                        image_url=frame_path,
                        embedding=embedding.tolist(),
                        model_name='voyage-2'
                    )
                    
                    if result:
                        # Mark as uploaded
                        self.db.mark_embedding_uploaded(embedding_id, 'postgres')
                        success_count += 1
                    else:
                        error_count += 1
                        logger.error(f"Failed to store embedding {embedding_id} in PostgreSQL")
                
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error storing embedding in PostgreSQL: {e}")
            
            logger.info(f"Completed batch {i//batch_size + 1}: {success_count} successful, {error_count} failed")
        
        logger.info(f"Export to PostgreSQL complete: {success_count} successful, {error_count} failed")
        return {'total': total, 'success': success_count, 'error': error_count}
    
    async def export_to_webhook(self, batch_size: int = 20) -> Dict[str, int]:
        """Export embeddings to n8n webhook.
        
        Args:
            batch_size: Number of embeddings to export in a batch
            
        Returns:
            dict: Stats about the export operation
        """
        import requests
        
        # Get webhook URL from environment
        webhook_url = os.environ.get('WEBHOOK_URL')
        webhook_test_url = os.environ.get('WEBHOOK_TEST_URL')
        use_test_webhook = os.environ.get('USE_TEST_WEBHOOK', 'false').lower() == 'true'
        
        url = webhook_test_url if use_test_webhook else webhook_url
        
        if not url:
            logger.error("Webhook URL not configured in environment variables")
            return {'total': 0, 'success': 0, 'error': 0}
        
        logger.info(f"Using webhook URL: {url}")
        
        # Get pending uploads
        pending = self.db.get_pending_uploads('webhook')
        
        if not pending:
            logger.info("No pending uploads for webhook")
            return {'total': 0, 'success': 0, 'error': 0}
        
        logger.info(f"Found {len(pending)} embeddings to export to webhook")
        
        # Export in batches
        total = len(pending)
        success_count = 0
        error_count = 0
        
        for i in range(0, total, batch_size):
            batch = pending[i:i+batch_size]
            logger.info(f"Exporting batch {i//batch_size + 1}/{(total+batch_size-1)//batch_size}: {len(batch)} embeddings")
            
            for entry in batch:
                try:
                    # Extract data
                    embedding_id = entry['embedding_id']
                    frame_name = entry['frame_name']
                    chunk_content = entry['chunk_content']
                    frame_path = entry['frame_path']
                    folder_path = entry['folder_path']
                    folder_name = entry['folder_name']
                    airtable_record_id = entry['airtable_record_id']
                    
                    # Format the folder path to make it more readable
                    formatted_path = folder_path
                    if '/home/' in formatted_path:
                        # Make it relative to home
                        formatted_path = formatted_path.split('/home/')[1]
                        parts = formatted_path.split('/')
                        if len(parts) > 1:
                            # Remove username
                            formatted_path = '/'.join(parts[1:])
                    
                    # Prepare payload
                    payload = {
                        'environment': 'test' if use_test_webhook else 'production',
                        'frame_name': frame_name,
                        'folder_path': formatted_path,
                        'folder_name': folder_name,
                        'chunk_content': chunk_content,
                        'airtable_record_id': airtable_record_id,
                        'embedding_id': str(embedding_id)
                    }
                    
                    # Send to webhook
                    response = requests.post(url, json=payload)
                    
                    if response.status_code == 200:
                        # Mark as uploaded
                        self.db.mark_embedding_uploaded(embedding_id, 'webhook')
                        success_count += 1
                        logger.info(f"Successfully sent embedding {embedding_id} to webhook")
                    else:
                        error_count += 1
                        logger.error(f"Failed to send embedding {embedding_id} to webhook: {response.status_code} - {response.text}")
                
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error sending embedding to webhook: {e}")
            
            logger.info(f"Completed batch {i//batch_size + 1}: {success_count} successful, {error_count} failed")
        
        logger.info(f"Export to webhook complete: {success_count} successful, {error_count} failed")
        return {'total': total, 'success': success_count, 'error': error_count}

async def main():
    """Main entry point for the local processor."""
    parser = argparse.ArgumentParser(description='Process frames using local database')
    
    # Database and output options
    parser.add_argument('--db-path', default='frames_local.db', 
                        help='Path to local database file (default: frames_local.db)')
    parser.add_argument('--output-dir', help='Directory for storing downloaded frames')
    
    # Google Drive options
    parser.add_argument('--drive-folder', help='Google Drive folder ID to process frames from')
    parser.add_argument('--credentials', help='Path to Google API credentials')
    parser.add_argument('--pattern', help='Pattern to filter files by (e.g., "frame_")')
    
    # Processing options
    parser.add_argument('--limit', type=int, help='Maximum number of frames to process')
    parser.add_argument('--chunk-size', type=int, default=500, help='Size of text chunks (default: 500)')
    parser.add_argument('--chunk-overlap', type=int, default=50, help='Overlap between chunks (default: 50)')
    parser.add_argument('--max-chunks', type=int, help='Maximum number of chunks per frame')
    parser.add_argument('--force', action='store_true', help='Force reprocessing even if already processed')
    parser.add_argument('--parallel', type=int, default=1, 
                        help='Number of frames to process in parallel (default: 1)')
    
    # Export options
    parser.add_argument('--export-postgres', action='store_true', help='Export embeddings to PostgreSQL')
    parser.add_argument('--export-webhook', action='store_true', help='Export embeddings to webhook')
    parser.add_argument('--batch-size', type=int, default=20, 
                        help='Batch size for exports (default: 20)')
    
    # Add an action mode
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--load', action='store_true', help='Load frames from Google Drive')
    group.add_argument('--process', action='store_true', help='Process frames')
    group.add_argument('--export', action='store_true', help='Export embeddings')
    group.add_argument('--all', action='store_true', help='Load, process, and export')
    
    args = parser.parse_args()
    
    # Print usage example when no arguments are provided
    if len(sys.argv) <= 1:
        parser.print_help()
        print("\nUsage examples:")
        print(f"  # Load frames from Google Drive")
        print(f"  python {sys.argv[0]} --load --drive-folder FOLDER_ID --credentials creds.json")
        print(f"\n  # Process frames")
        print(f"  python {sys.argv[0]} --process --limit 10 --parallel 5 --max-chunks 2")
        print(f"\n  # Export embeddings")
        print(f"  python {sys.argv[0]} --export --export-postgres --export-webhook")
        print(f"\n  # Do everything in one go")
        print(f"  python {sys.argv[0]} --all --drive-folder FOLDER_ID --credentials creds.json --parallel 5")
        return
    
    # Create processor
    processor = LocalFrameProcessor(
        db_path=args.db_path,
        output_dir=args.output_dir
    )
    
    try:
        # Load frames
        if args.load or args.all:
            if not args.drive_folder:
                logger.error("--drive-folder is required for --load or --all")
                return
            
            logger.info(f"Loading frames from Google Drive folder: {args.drive_folder}")
            frames_added, frames_downloaded = await processor.load_from_google_drive(
                args.drive_folder,
                credentials_path=args.credentials,
                file_pattern=args.pattern,
                limit=args.limit,
                download=True
            )
            
            logger.info(f"Added {frames_added} frames, downloaded {frames_downloaded} frames")
        
        # Process frames
        if args.process or args.all:
            logger.info("Processing unprocessed frames")
            successful, failures = await processor.process_unprocessed_frames(
                limit=args.limit,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap,
                max_chunks=args.max_chunks,
                force_reprocess=args.force,
                parallel=args.parallel
            )
            
            logger.info(f"Processed {successful + failures} frames: {successful} successful, {failures} failed")
        
        # Export embeddings
        if args.export or args.all:
            # Export to PostgreSQL
            if args.export_postgres or args.all:
                logger.info("Exporting embeddings to PostgreSQL")
                postgres_stats = await processor.export_to_postgres(batch_size=args.batch_size)
                
                logger.info(f"PostgreSQL export: {postgres_stats['success']}/{postgres_stats['total']} successful")
            
            # Export to webhook
            if args.export_webhook or args.all:
                logger.info("Exporting embeddings to webhook")
                webhook_stats = await processor.export_to_webhook(batch_size=args.batch_size)
                
                logger.info(f"Webhook export: {webhook_stats['success']}/{webhook_stats['total']} successful")
        
    finally:
        # Close processor
        processor.close()

if __name__ == "__main__":
    # Run main
    asyncio.run(main()) 