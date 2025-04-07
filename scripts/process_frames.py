#!/usr/bin/env python3
"""
Process Frames - Command line tool for processing frames and creating embeddings.

This script handles:
1. Loading frames from a directory
2. Processing frames (chunking metadata, creating embeddings)
3. Storing results in PostgreSQL database or sending to webhook
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
from src.processors.batch_processor import process_directory

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("process_frames")

async def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Process frames and create embeddings")
    
    # Input options
    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument("--input", required=True, help="Input file or directory path")
    input_group.add_argument("--pattern", default="*.jpg", help="Glob pattern for image files (default: *.jpg)")
    input_group.add_argument("--limit", type=int, default=None, help="Maximum number of files to process")
    input_group.add_argument("--google-drive-url", help="Google Drive URL to download frames from")
    
    # Processing options
    processing_group = parser.add_argument_group("Processing Options")
    processing_group.add_argument("--chunk-size", type=int, default=500, help="Size of text chunks (default: 500)")
    processing_group.add_argument("--chunk-overlap", type=int, default=50, help="Overlap between chunks (default: 50)")
    processing_group.add_argument("--max-chunks", type=int, default=None, help="Maximum number of chunks per frame")
    processing_group.add_argument("--sequential", action="store_true", help="Process files sequentially")
    processing_group.add_argument("--concurrency", type=int, default=4, help="Maximum number of concurrent processes (default: 4)")
    
    # Storage options
    storage_group = parser.add_argument_group("Storage Options")
    storage_group.add_argument("--no-airtable", action="store_true", help="Disable Airtable storage")
    storage_group.add_argument("--no-postgres", action="store_true", help="Disable PostgreSQL storage")
    storage_group.add_argument("--webhook", action="store_true", help="Enable webhook notifications")
    storage_group.add_argument("--production-webhook", action="store_true", help="Use production webhook instead of test webhook")
    
    # Local storage options 
    local_group = parser.add_argument_group("Local Storage Options")
    local_group.add_argument("--local-only", action="store_true", help="Only store locally, don't send to webhook or database")
    local_group.add_argument("--local-storage-dir", default="frame_embeddings", help="Directory to store local embedding files")
    
    args = parser.parse_args()
    
    # Process frames
    results = await process_directory(
        input_path=args.input,
        pattern=args.pattern,
        limit=args.limit,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        max_chunks=args.max_chunks,
        sequential=args.sequential,
        concurrency=args.concurrency,
        save_to_airtable=not args.no_airtable and not args.local_only,
        save_to_postgres=not args.no_postgres and not args.local_only,
        use_webhook=args.webhook and not args.local_only,
        use_test_webhook=not args.production_webhook
    )
    
    # Print summary
    print("\nProcessing summary:")
    print(f"  Total files: {results.get('total', 0)}")
    print(f"  Successfully processed: {results.get('successful', 0)}")
    print(f"  Failed: {results.get('failed', 0)}")
    
    if args.local_only:
        print(f"\nData stored locally in: {args.local_storage_dir}")
    
    # Return exit code
    return 0 if results.get('failed', 0) == 0 else 1

if __name__ == "__main__":
    asyncio.run(main()) 