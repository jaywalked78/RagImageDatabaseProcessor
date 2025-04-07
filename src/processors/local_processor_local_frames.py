#!/usr/bin/env python3
"""
Local frame processor that uses locally stored frames with metadata from Airtable.
This script processes frames from a local directory, links them with Google Drive URLs,
and creates embeddings with minimal API calls.
"""

import os
import sys
import json
import time
import glob
import asyncio
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union

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

class LocalFramesProcessor:
    """Processes locally stored frames using a local database to minimize API calls."""
    
    def __init__(self, db_path: str = "frames_local.db", 
                 api_keys: Optional[List[str]] = None):
        """Initialize the frame processor.
        
        Args:
            db_path: Path to local database file
            api_keys: List of Voyage API keys (optional, defaults to env vars)
        """
        # Initialize local database
        self.db = LocalDatabase(db_path=db_path)
        
        # Initialize embedder
        self.embedder = ChunkEmbedder(api_keys=api_keys)
    
    def close(self):
        """Close the database connection."""
        self.db.close()
    
    def scan_local_frames_directory(self, base_dir: str, pattern: str = "**/*.jpg") -> List[Dict[str, Any]]:
        """Scan a local directory for frames.
        
        Args:
            base_dir: Base directory containing frames
            pattern: Glob pattern to match frames (default: **/*.jpg)
            
        Returns:
            list: List of frame dictionaries with paths
        """
        base_path = Path(base_dir)
        if not base_path.exists():
            logger.error(f"Base directory {base_dir} does not exist")
            return []
        
        # Find all matching files
        frame_paths = list(base_path.glob(pattern))
        
        logger.info(f"Found {len(frame_paths)} frames in {base_dir} matching pattern {pattern}")
        
        frames = []
        for path in frame_paths:
            # Get relative path from base_dir
            rel_path = path.relative_to(base_path)
            folder_path = str(rel_path.parent)
            frame_name = path.name
            
            frames.append({
                'frame_path': str(path),
                'folder_path': folder_path if folder_path != '.' else '',
                'frame_name': frame_name
            })
        
        return frames
    
    def load_local_frames(self, base_dir: str, pattern: str = "**/*.jpg", 
                        google_drive_folder_id: Optional[str] = None) -> int:
        """Load frames from a local directory into the database.
        
        Args:
            base_dir: Base directory containing frames
            pattern: Glob pattern to match frames (default: **/*.jpg)
            google_drive_folder_id: Google Drive folder ID for URLs (optional)
            
        Returns:
            int: Number of frames added to database
        """
        # Scan for local frames
        frames = self.scan_local_frames_directory(base_dir, pattern)
        
        if not frames:
            logger.warning(f"No frames found in {base_dir} matching pattern {pattern}")
            return 0
        
        # Add folders and frames to database
        frames_added = 0
        folders_added = 0
        folder_cache = {}
        
        for frame in frames:
            frame_path = frame['frame_path']
            folder_path = frame['folder_path']
            frame_name = frame['frame_name']
            
            # Generate folder ID and name
            if folder_path in folder_cache:
                folder_db_id = folder_cache[folder_path]
            else:
                folder_id = f"local_{folder_path.replace('/', '_')}"
                folder_name = os.path.basename(folder_path) if folder_path else 'root'
                
                # Add folder to database
                folder_db_id = self.db.add_folder(
                    folder_id=folder_id,
                    folder_path=folder_path,
                    source='local',
                    folder_name=folder_name
                )
                
                folder_cache[folder_path] = folder_db_id
                folders_added += 1
            
            # Generate frame ID
            frame_id = f"local_{folder_path.replace('/', '_')}_{frame_name}"
            
            # Generate Google Drive URL if folder ID is provided
            google_drive_url = None
            if google_drive_folder_id:
                google_drive_url = f"https://drive.google.com/drive/folders/{google_drive_folder_id}"
            
            # Add frame to database
            frame_db_id = self.db.add_frame(
                frame_id=frame_id,
                folder_id=folder_db_id,
                frame_name=frame_name,
                frame_path=frame_path,
                local_path=frame_path,
                google_drive_url=google_drive_url
            )
            
            if frame_db_id:
                # Mark as downloaded since it's already local
                self.db.update_frame_local_path(frame_db_id, frame_path)
                frames_added += 1
                
                # Add basic metadata
                metadata = {
                    'frame_name': frame_name,
                    'folder_path': folder_path,
                    'google_drive_url': google_drive_url
                }
                self.db.add_metadata(frame_db_id, 'local', json.dumps(metadata))
        
        logger.info(f"Added {frames_added} frames and {folders_added} folders from {base_dir}")
        return frames_added
    
    def load_airtable_metadata(self, airtable_data: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Load metadata from Airtable and associate with local frames.
        
        Args:
            airtable_data: List of Airtable records
            
        Returns:
            tuple: (number of frames updated, number of frames not found)
        """
        frames_updated = 0
        frames_not_found = 0
        
        for record in airtable_data:
            record_id = record['id']
            fields = record.get('fields', {})
            
            # Extract frame name and folder path
            frame_name = fields.get('Name', '')
            folder_path = fields.get('folderPath', '')
            
            if not frame_name:
                logger.warning(f"Skipping Airtable record {record_id} - no frame name")
                continue
            
            # Try to find the frame in the database
            cursor = self.db.conn.cursor()
            cursor.execute('''
            SELECT f.id, f.frame_name, f.frame_path, fo.folder_path
            FROM frames f
            JOIN folders fo ON f.folder_id = fo.id
            WHERE f.frame_name = ? AND fo.folder_path LIKE ?
            ''', (frame_name, f"%{folder_path}%"))
            
            result = cursor.fetchone()
            
            if result:
                frame_db_id = result['id']
                
                # Add Airtable metadata
                self.db.add_metadata(frame_db_id, 'airtable', json.dumps(fields))
                
                # Update Airtable record ID
                cursor.execute('''
                UPDATE frames
                SET airtable_record_id = ?
                WHERE id = ?
                ''', (record_id, frame_db_id))
                self.db.conn.commit()
                
                frames_updated += 1
            else:
                logger.warning(f"Frame not found for Airtable record {record_id}: {frame_name} in {folder_path}")
                frames_not_found += 1
        
        logger.info(f"Updated {frames_updated} frames with Airtable metadata, {frames_not_found} frames not found")
        return frames_updated, frames_not_found
    
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
        
        # Check if frame is available locally
        if not local_path or not os.path.exists(local_path):
            logger.error(f"Frame {frame_name} not available locally at {local_path}")
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
        
        # If no Airtable metadata found, try with local metadata
        if not metadata_entries:
            metadata_entries = self.db.get_metadata_for_frame(frame_id, metadata_type='local')
            
        # If still no metadata found, use frame name only
        if not metadata_entries:
            logger.warning(f"No metadata found for frame {frame_name}, using frame name only")
            metadata_text = f"Frame: {frame_name}"
        else:
            # Parse JSON metadata
            metadata = json.loads(metadata_entries[0]['content'])
            
            # If it's Airtable metadata, process it with the standard function
            if metadata_entries[0]['metadata_type'] == 'airtable':
                metadata_text = process_metadata_text(metadata)
            else:
                # For local metadata, create a simple text representation
                metadata_text = f"Frame: {metadata.get('frame_name', '')}\n"
                metadata_text += f"Folder: {metadata.get('folder_path', '')}\n"
                if 'google_drive_url' in metadata and metadata['google_drive_url']:
                    metadata_text += f"Google Drive URL: {metadata['google_drive_url']}\n"
            
            logger.info(f"Found {metadata_entries[0]['metadata_type']} metadata for frame {frame_name}")
        
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
                    
                    # Get Google Drive URL if available
                    google_drive_url = entry.get('google_drive_url', '')
                    
                    # Store in PostgreSQL
                    result = await postgres_store.store_vector_embedding(
                        embedding_id=str(embedding_id),
                        reference_id=str(entry['frame_id']),
                        reference_type='frame',
                        text_content=chunk_content,
                        image_url=google_drive_url or frame_path,  # Use Google Drive URL if available
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
                    
                    # Get Google Drive URL if available
                    google_drive_url = entry.get('google_drive_url', '')
                    
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
                        'embedding_id': str(embedding_id),
                        'google_drive_url': google_drive_url
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
    parser = argparse.ArgumentParser(description='Process local frames using database')
    
    # Database options
    parser.add_argument('--db-path', default='frames_local.db', 
                        help='Path to local database file (default: frames_local.db)')
    
    # Local frames options
    parser.add_argument('--frames-dir', default='/home/jason/Videos/screenRecordings',
                        help='Base directory containing local frames (default: /home/jason/Videos/screenRecordings)')
    parser.add_argument('--pattern', default='**/*.jpg',
                        help='Glob pattern to match frames (default: **/*.jpg)')
    parser.add_argument('--drive-folder-id',
                        help='Google Drive folder ID for URL references')
    
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
    group.add_argument('--load', action='store_true', help='Load frames from local directory')
    group.add_argument('--process', action='store_true', help='Process frames')
    group.add_argument('--export', action='store_true', help='Export embeddings')
    group.add_argument('--all', action='store_true', help='Load, process, and export')
    
    args = parser.parse_args()
    
    # Print usage example when no arguments are provided
    if len(sys.argv) <= 1:
        parser.print_help()
        print("\nUsage examples:")
        print(f"  # Load frames from local directory")
        print(f"  python {sys.argv[0]} --load --frames-dir /path/to/frames --pattern '**/*.jpg'")
        print(f"\n  # Process frames")
        print(f"  python {sys.argv[0]} --process --limit 10 --parallel 5 --max-chunks 2")
        print(f"\n  # Export embeddings")
        print(f"  python {sys.argv[0]} --export --export-postgres --export-webhook")
        print(f"\n  # Do everything in one go")
        print(f"  python {sys.argv[0]} --all --frames-dir /path/to/frames --drive-folder-id FOLDER_ID --parallel 5")
        return
    
    # Create processor
    processor = LocalFramesProcessor(db_path=args.db_path)
    
    try:
        # Load frames
        if args.load or args.all:
            logger.info(f"Loading frames from local directory: {args.frames_dir}")
            frames_added = processor.load_local_frames(
                base_dir=args.frames_dir,
                pattern=args.pattern,
                google_drive_folder_id=args.drive_folder_id
            )
            
            logger.info(f"Added {frames_added} frames from local directory")
        
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