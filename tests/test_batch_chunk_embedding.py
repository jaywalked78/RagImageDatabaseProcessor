#!/usr/bin/env python3
"""
Batch processing script for embedding multiple frames.
This processes frames from a directory or Google Drive folder, finds their metadata,
chunks it, creates embeddings, and saves them to Airtable and PostgreSQL.
Supports parallel processing, batch mode for Airtable updates, and Google Drive integration.
"""

import os
import sys
import glob
import logging
import logging.config
import argparse
import asyncio
import time
import shutil
import datetime
from pathlib import Path
from dotenv import load_dotenv
import random

# Import our process_frame function
from test_chunk_embedding import process_frame, ChunkEmbedder, AirtableEmbeddingStore

# Import Google Drive downloader if available
try:
    from google_drive_downloader import GoogleDriveDownloader
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'filename': 'batch_embedding.log',
            'mode': 'a',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("batch_embedding")

# Load environment variables
load_dotenv()

async def process_frames_parallel(frames, chunk_size=500, chunk_overlap=50, max_chunks=None, 
                               force_reprocess=False, save_to_airtable=True, save_to_postgres=True,
                               max_concurrent=30, batch_mode=True, airtable_chunk_size=20,
                               use_webhook=False):
    """Process multiple frames in parallel with rate limiting.
    
    Args:
        frames: List of frame paths to process
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        max_chunks: Maximum chunks per frame
        force_reprocess: Force reprocessing
        save_to_airtable: Save to Airtable
        save_to_postgres: Save to PostgreSQL
        max_concurrent: Max concurrent frames
        batch_mode: Use batch mode for Airtable updates
        airtable_chunk_size: Size of batches for Airtable updates
        use_webhook: Use n8n webhook instead of direct Airtable updates
    """
    total = len(frames)
    successful = 0
    failures = 0
    
    logger.info(f"Processing {total} frames with up to {max_concurrent} frames in parallel")
    
    # Initialize Airtable batch mode if enabled
    airtable_store = None
    if save_to_airtable and batch_mode and not use_webhook:
        airtable_store = AirtableEmbeddingStore()
        airtable_store.enable_batch_mode()
        logger.info("Enabled batch mode for Airtable updates")
    elif save_to_airtable and use_webhook:
        airtable_store = AirtableEmbeddingStore(use_webhook=True)
        logger.info("Using n8n webhook for Airtable updates")
    
    # Process frames in batches to limit concurrency
    for i in range(0, total, max_concurrent):
        batch = frames[i:i+max_concurrent]
        batch_size = len(batch)
        logger.info(f"Processing batch {i//max_concurrent + 1} with {batch_size} frames (frames {i+1}-{i+batch_size}/{total})")
        
        # Create tasks for all frames in this batch
        tasks = []
        for frame_path in batch:
            frame_name = os.path.basename(frame_path)
            logger.info(f"Queueing frame: {frame_name}")
            task = asyncio.create_task(
                process_frame(
                    frame_path,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    max_chunks=max_chunks,
                    force_reprocess=force_reprocess,
                    save_to_airtable=save_to_airtable,  # Always pass the save_to_airtable flag
                    save_to_postgres=save_to_postgres,
                    airtable_store=airtable_store,  # Pass the shared store instance
                    use_webhook=use_webhook
                )
            )
            tasks.append((frame_name, frame_path, task))
        
        # Wait for all tasks in this batch to complete
        for frame_name, frame_path, task in tasks:
            try:
                start_time = time.time()
                result = await task
                elapsed = time.time() - start_time
                
                if result:
                    successful += 1
                    logger.info(f"✅ Successfully processed frame {frame_name} in {elapsed:.2f} seconds")
                else:
                    failures += 1
                    logger.error(f"❌ Failed to process frame {frame_name}")
            except Exception as e:
                failures += 1
                logger.error(f"❌ Error processing frame {frame_name}: {e}")
        
        # Log batch completion
        logger.info(f"Completed batch {i//max_concurrent + 1}: {successful} successful, {failures} failed")
    
    # If using batch mode, commit all Airtable updates now
    if save_to_airtable and batch_mode and airtable_store and not use_webhook:
        batch_size = airtable_store.get_batch_size()
        if batch_size > 0:
            logger.info(f"Committing {batch_size} updates to Airtable...")
            results = await airtable_store.commit_batch_updates(chunk_size=airtable_chunk_size)
            logger.info(f"Airtable batch update complete: {results['success_count']} successful, {results['error_count']} failed")
    
    return successful, failures

async def process_frames_sequentially(frames, chunk_size=500, chunk_overlap=50, max_chunks=None, 
                                 force_reprocess=False, save_to_airtable=True, save_to_postgres=True,
                                 frame_delay=3, use_webhook=False):
    """Process multiple frames sequentially with rate limiting."""
    successful = 0
    failures = 0
    
    logger.info(f"Processing {len(frames)} frames sequentially")
    
    for i, frame_path in enumerate(frames):
        frame_name = os.path.basename(frame_path)
        logger.info(f"Processing frame {i+1}/{len(frames)}: {frame_name}")
        
        try:
            start_time = time.time()
            result = await process_frame(
                frame_path,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                max_chunks=max_chunks,
                force_reprocess=force_reprocess,
                save_to_airtable=save_to_airtable,
                save_to_postgres=save_to_postgres,
                use_webhook=use_webhook
            )
            elapsed = time.time() - start_time
            
            if result:
                successful += 1
                logger.info(f"✅ Successfully processed frame {frame_name} in {elapsed:.2f} seconds")
            else:
                failures += 1
                logger.error(f"❌ Failed to process frame {frame_name}")
                
            # Add delay between frames to avoid rate limiting
            if i < len(frames) - 1:
                logger.info(f"Waiting {frame_delay} seconds before processing next frame...")
                await asyncio.sleep(frame_delay)
                
        except Exception as e:
            failures += 1
            logger.error(f"❌ Error processing frame {frame_name}: {e}")
    
    return successful, failures

async def download_from_google_drive(folder_id, limit=None, sample=None, pattern=None, credentials_path=None):
    """Download frames from Google Drive folder to a temporary directory.
    
    Args:
        folder_id: Google Drive folder ID
        limit: Maximum number of frames to download
        sample: Number of random frames to sample
        pattern: Filter pattern for frame files
        credentials_path: Path to Google API credentials
        
    Returns:
        tuple: (temp_dir, list of downloaded file paths)
    """
    if not GOOGLE_DRIVE_AVAILABLE:
        logger.error("Google Drive integration not available. Install the required dependencies.")
        logger.error("Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return None, []
    
    logger.info(f"Downloading frames from Google Drive folder {folder_id}")
    
    # Create Google Drive downloader
    downloader = GoogleDriveDownloader(credentials_path=credentials_path)
    
    # Prepare filter pattern for Google Drive
    drive_filter = None
    if pattern:
        drive_filter = f"name contains '{pattern}'"
    
    # Calculate effective limit
    effective_limit = None
    if limit and sample:
        # Download more than we need for sampling
        effective_limit = max(limit, sample * 2)
    elif limit:
        effective_limit = limit
    elif sample:
        # Download more than we need for sampling
        effective_limit = sample * 2
    
    # Download to temp directory
    temp_dir, files = downloader.download_frames_to_temp(
        folder_id, 
        file_filter=drive_filter,
        limit=effective_limit
    )
    
    if not files:
        logger.error("No files downloaded from Google Drive")
        return temp_dir, []
    
    # Apply sampling if requested
    if sample and len(files) > sample:
        sampled_files = random.sample(files, sample)
        logger.info(f"Selected random sample of {len(sampled_files)} files from {len(files)} downloaded")
        return temp_dir, sampled_files
    
    return temp_dir, files

async def main():
    """Main entry point for the batch processing script."""
    parser = argparse.ArgumentParser(description='Batch process frames with metadata embedding')
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--frames-dir', help='Directory containing frames to process')
    input_group.add_argument('--drive-folder', help='Google Drive folder ID containing frames')
    
    parser.add_argument('--glob', default='frame_*.jpg', help='Glob pattern to match frames (default: frame_*.jpg)')
    parser.add_argument('--limit', type=int, default=None, help='Maximum number of frames to process')
    parser.add_argument('--sample', type=int, default=None, help='Process a random sample of N frames')
    parser.add_argument('--chunk-size', type=int, default=500, help='Target size for text chunks')
    parser.add_argument('--chunk-overlap', type=int, default=50, help='Overlap between chunks')
    parser.add_argument('--max-chunks', type=int, default=None, help='Maximum number of chunks per frame')
    parser.add_argument('--force', action='store_true', help='Force reprocessing even if already processed')
    parser.add_argument('--no-save', action='store_true', help='Skip saving embeddings to Airtable')
    parser.add_argument('--no-postgres', action='store_true', help='Skip saving embeddings to PostgreSQL vector database')
    parser.add_argument('--frame-delay', type=int, default=3, help='Seconds to wait between processing frames (default: 3)')
    parser.add_argument('--parallel', type=int, default=30, help='Maximum number of frames to process in parallel (default: 30)')
    parser.add_argument('--no-batch', action='store_true', help='Disable batch mode for Airtable updates')
    parser.add_argument('--airtable-batch-size', type=int, default=20, help='Batch size for Airtable updates (default: 20)')
    parser.add_argument('--use-webhook', action='store_true', help='Use n8n webhook instead of direct Airtable updates')
    parser.add_argument('--credentials', help='Path to Google Drive API credentials (for --drive-folder)')
    parser.add_argument('--keep-temp', action='store_true', help='Keep temporary directory after processing (for --drive-folder)')
    args = parser.parse_args()
    
    # Print usage example when no arguments are provided
    if len(sys.argv) <= 1:
        print("\nUsage examples:")
        print(f"  python {sys.argv[0]} --frames-dir /path/to/frames --limit 10 --parallel 5 --max-chunks 2")
        print(f"  python {sys.argv[0]} --frames-dir /path/to/frames --use-webhook --sample 5 --force")
        print(f"  python {sys.argv[0]} --drive-folder FOLDER_ID --limit 10 --use-webhook --credentials creds.json")
        print("\nFor webhook integration, ensure these environment variables are set:")
        print("  WEBHOOK_URL=http://your-n8n-server/webhook/...")
        print("  WEBHOOK_TEST_URL=http://your-n8n-server/webhook-test/...")
        print("  USE_TEST_WEBHOOK=true|false")
        return
    
    # Setup logging
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger('batch_embedding')
    
    temp_dir = None
    frames_to_process = []
    
    try:
        # Handle Google Drive input
        if args.drive_folder:
            if not GOOGLE_DRIVE_AVAILABLE:
                logger.error("Google Drive integration not available. Install google-api-python-client.")
                return
                
            temp_dir, downloaded_frames = await download_from_google_drive(
                args.drive_folder,
                limit=args.limit,
                sample=args.sample,
                pattern=args.glob,
                credentials_path=args.credentials
            )
            
            if not downloaded_frames:
                logger.error("No frames downloaded from Google Drive. Exiting.")
                return
                
            frames_to_process = downloaded_frames
            logger.info(f"Will process {len(frames_to_process)} frames from Google Drive")
            
        # Handle local directory input
        elif args.frames_dir:
            frames_pattern = os.path.join(args.frames_dir, args.glob)
            all_frames = sorted(glob.glob(frames_pattern))
            
            if len(all_frames) == 0:
                logger.error(f"No frames found matching pattern '{args.glob}' in directory: {args.frames_dir}")
                sys.exit(1)
            
            logger.info(f"Found {len(all_frames)} frames matching pattern '{args.glob}'")
            
            # Limit the number of frames if specified
            frames_to_process = all_frames
            if args.sample and args.sample > 0 and args.sample < len(all_frames):
                # Process a random sample
                frames_to_process = random.sample(all_frames, args.sample)
                logger.info(f"Processing a random sample of {args.sample} frames")
            elif args.limit and args.limit > 0 and args.limit < len(all_frames):
                frames_to_process = all_frames[:args.limit]
                logger.info(f"Processing only the first {args.limit} frames")
        
        # Determine max concurrent frames - don't exceed total frames
        max_concurrent = min(args.parallel, len(frames_to_process))
        logger.info(f"Will process up to {max_concurrent} frames in parallel")
        
        # Determine batch mode
        batch_mode = not args.no_batch
        logger.info(f"Airtable batch mode: {'Enabled' if batch_mode and not args.use_webhook else 'Disabled'}")
        
        if args.use_webhook:
            logger.info("Using n8n webhook for Airtable updates")
        
        # Process frames
        start_time = time.time()
        
        # Choose between parallel and sequential processing
        if max_concurrent > 1:
            logger.info("Using parallel processing mode")
            successful, failures = await process_frames_parallel(
                frames_to_process,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap,
                max_chunks=args.max_chunks,
                force_reprocess=args.force,
                save_to_airtable=not args.no_save,
                save_to_postgres=not args.no_postgres,
                max_concurrent=max_concurrent,
                batch_mode=batch_mode,
                airtable_chunk_size=args.airtable_batch_size,
                use_webhook=args.use_webhook
            )
        else:
            logger.info("Using sequential processing mode")
            successful, failures = await process_frames_sequentially(
                frames_to_process,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap,
                max_chunks=args.max_chunks,
                force_reprocess=args.force,
                save_to_airtable=not args.no_save,
                save_to_postgres=not args.no_postgres,
                frame_delay=args.frame_delay,
                use_webhook=args.use_webhook
            )
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Calculate time per frame
        time_per_frame = elapsed / len(frames_to_process) if frames_to_process else 0
        
        logger.info(f"Batch processing complete. Successfully processed {successful} out of {len(frames_to_process)} frames.")
        logger.info(f"Total processing time: {datetime.timedelta(seconds=elapsed)}")
        logger.info(f"Average time per frame: {time_per_frame:.2f} seconds")
        
    finally:
        # Clean up temporary directory if we created one and --keep-temp wasn't specified
        if temp_dir and not args.keep_temp:
            logger.info(f"Cleaning up temporary directory: {temp_dir}")
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Error cleaning up temporary directory: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 