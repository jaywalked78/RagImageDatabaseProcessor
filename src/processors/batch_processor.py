"""
Batch processor for handling multiple frames in sequential or parallel mode.
"""

import os
import sys
import time
import glob
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from pathlib import Path

# Import project modules
from src.processors.frame_processor import process_frame
from src.api.google_drive import GoogleDriveDownloader
from src.database.postgres_vector_store import PostgresVectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("BatchProcessor")

class BatchProcessor:
    """
    Process multiple frames in batch mode with parallel or sequential execution.
    """
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        max_chunks: Optional[int] = None,
        use_key_rotation: bool = True,
        save_to_airtable: bool = True,
        save_to_postgres: bool = True,
        postgres_connection_string: Optional[str] = None,
        webhook_url: Optional[str] = None,
        test_webhook_url: Optional[str] = None,
        sequential: bool = False,
        concurrency: int = 4
    ):
        """
        Initialize the batch processor.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
            max_chunks: Maximum number of chunks per frame
            use_key_rotation: Whether to rotate API keys
            save_to_airtable: Whether to save results to Airtable
            save_to_postgres: Whether to save results to PostgreSQL
            postgres_connection_string: PostgreSQL connection string
            webhook_url: Webhook URL for sending results
            test_webhook_url: Test webhook URL
            sequential: Whether to process files sequentially or in parallel
            concurrency: Maximum number of concurrent processes
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunks = max_chunks
        self.use_key_rotation = use_key_rotation
        self.save_to_airtable = save_to_airtable
        self.save_to_postgres = save_to_postgres
        self.postgres_connection_string = postgres_connection_string
        self.webhook_url = webhook_url
        self.test_webhook_url = test_webhook_url
        self.sequential = sequential
        self.concurrency = min(concurrency, mp.cpu_count())
        
        logger.info(f"Initialized BatchProcessor (sequential={sequential}, concurrency={self.concurrency})")
    
    async def process_files(
        self, 
        files: List[str],
        google_drive_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process multiple files either sequentially or in parallel.
        
        Args:
            files: List of file paths to process
            google_drive_url: Optional Google Drive URL to download files from
        
        Returns:
            Dictionary with processing results
        """
        results = {
            'total': len(files),
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'files': []
        }
        
        # Download files from Google Drive if URL provided
        if google_drive_url:
            logger.info(f"Downloading files from Google Drive: {google_drive_url}")
            downloader = GoogleDriveDownloader()
            download_dir = await downloader.download_folder(google_drive_url)
            if download_dir:
                logger.info(f"Downloaded files to: {download_dir}")
                # Update file paths to point to downloaded files
                files = sorted(glob.glob(os.path.join(download_dir, '*.jpg')))
                results['total'] = len(files)
            else:
                logger.error("Failed to download files from Google Drive")
                return results
        
        if self.sequential:
            # Process files sequentially
            logger.info(f"Processing {len(files)} files sequentially")
            for file_path in files:
                try:
                    success = await process_frame(
                        frame_path=file_path,
                        chunk_size=self.chunk_size,
                        chunk_overlap=self.chunk_overlap,
                        max_chunks=self.max_chunks,
                        use_key_rotation=self.use_key_rotation,
                        save_to_airtable=self.save_to_airtable,
                        save_to_postgres=self.save_to_postgres,
                        postgres_connection_string=self.postgres_connection_string,
                        webhook_url=self.webhook_url,
                        test_webhook_url=self.test_webhook_url
                    )
                    
                    results['processed'] += 1
                    if success:
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                    
                    logger.info(f"Progress: {results['processed']}/{results['total']} files processed")
                    
                    # Add file result
                    results['files'].append({
                        'path': file_path,
                        'success': success
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    results['processed'] += 1
                    results['failed'] += 1
                    results['files'].append({
                        'path': file_path,
                        'success': False,
                        'error': str(e)
                    })
        else:
            # Process files in parallel
            logger.info(f"Processing {len(files)} files in parallel (concurrency={self.concurrency})")
            tasks = []
            
            for file_path in files:
                task = asyncio.create_task(process_frame(
                    frame_path=file_path,
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    max_chunks=self.max_chunks,
                    use_key_rotation=self.use_key_rotation,
                    save_to_airtable=self.save_to_airtable,
                    save_to_postgres=self.save_to_postgres,
                    postgres_connection_string=self.postgres_connection_string,
                    webhook_url=self.webhook_url,
                    test_webhook_url=self.test_webhook_url
                ))
                tasks.append((file_path, task))
            
            # Process tasks with rate limiting
            chunk_size = self.concurrency
            for i in range(0, len(tasks), chunk_size):
                chunk = tasks[i:i+chunk_size]
                
                # Wait for the current chunk to complete
                for file_path, task in chunk:
                    try:
                        success = await task
                        
                        results['processed'] += 1
                        if success:
                            results['successful'] += 1
                        else:
                            results['failed'] += 1
                        
                        results['files'].append({
                            'path': file_path,
                            'success': success
                        })
                        
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
                        results['processed'] += 1
                        results['failed'] += 1
                        results['files'].append({
                            'path': file_path,
                            'success': False,
                            'error': str(e)
                        })
                
                logger.info(f"Progress: {results['processed']}/{results['total']} files processed")
        
        logger.info(f"Batch processing complete: {results['successful']} successful, {results['failed']} failed out of {results['total']} files")
        return results

async def process_directory(
    input_path: str,
    pattern: str = "*.jpg",
    limit: Optional[int] = None,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    max_chunks: Optional[int] = None,
    sequential: bool = True,
    concurrency: int = 4,
    save_to_airtable: bool = True,
    save_to_postgres: bool = True,
    use_webhook: bool = False,
    use_test_webhook: bool = True
) -> Dict[str, Any]:
    """
    Process all matching files in a directory.
    
    Args:
        input_path: Path to directory containing files
        pattern: Glob pattern to match files
        limit: Maximum number of files to process
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        max_chunks: Maximum number of chunks per frame
        sequential: Whether to process files sequentially
        concurrency: Maximum number of concurrent processes
        save_to_airtable: Whether to save results to Airtable
        save_to_postgres: Whether to save results to PostgreSQL
        use_webhook: Whether to send results to webhook
        use_test_webhook: Whether to use test webhook URL
    
    Returns:
        Dictionary with processing results
    """
    # Validate input path
    input_path = Path(input_path)
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        return {
            'success': False,
            'error': f"Input path does not exist: {input_path}"
        }
    
    # Get files to process
    if input_path.is_dir():
        # Process directory
        pattern_path = os.path.join(str(input_path), pattern)
        files = sorted(glob.glob(pattern_path))
        logger.info(f"Found {len(files)} files matching pattern '{pattern}' in {input_path}")
    else:
        # Process single file
        files = [str(input_path)]
        logger.info(f"Processing single file: {input_path}")
    
    # Apply limit
    if limit and len(files) > limit:
        logger.info(f"Limiting to first {limit} files")
        files = files[:limit]
    
    # Initialize batch processor
    batch_processor = BatchProcessor(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        max_chunks=max_chunks,
        save_to_airtable=save_to_airtable,
        save_to_postgres=save_to_postgres,
        webhook_url=os.environ.get('WEBHOOK_URL') if use_webhook else None,
        test_webhook_url=os.environ.get('WEBHOOK_TEST_URL') if use_webhook and use_test_webhook else None,
        sequential=sequential,
        concurrency=concurrency
    )
    
    # Process files
    return await batch_processor.process_files(files) 