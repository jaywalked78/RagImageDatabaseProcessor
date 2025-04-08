#!/usr/bin/env python3
"""
Main entry point for the DatabaseAdvancedTokenizer application.
Processes frames, creates embeddings, and sends data to webhooks.
"""

import os
import sys
import json
import logging
import asyncio
import argparse
import csv
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import numpy as np
from PIL import Image
import time
import glob
import requests

# Configure logging
os.makedirs("output/logs/ocr", exist_ok=True)  # Create log directory if it doesn't exist
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("output/logs/ocr/ocr_data_processor.log")
    ]
)
logger = logging.getLogger("main")

# Load environment variables
load_dotenv()
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
WEBHOOK_TEST_URL = os.environ.get('WEBHOOK_TEST_URL')
FRAME_BASE_DIR = os.environ.get('FRAME_BASE_DIR', '/home/jason/Videos/screenRecordings')
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', 'tblFrameAnalysis')

# Import modules from the reorganized structure
from src.connectors.airtable import AirtableMetadataFinder
from src.connectors.webhook import WebhookConnector, send_webhook_payload
from src.utils.chunking import MetadataChunker
from src.embeddings.chunk_embedder import ChunkEmbedder

# Import frame processing functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.processors.frame_processor import FrameProcessor
from src.utils.logging_utils import configure_logging

# Function to save payload to CSV
def save_payload_to_csv(payload: Dict[str, Any], csv_file: str = "webhook_payloads.csv"):
    """
    Save webhook payload data to a CSV file for local record keeping.
    
    Args:
        payload: The webhook payload dictionary
        csv_file: CSV file path to save to
    """
    # Determine if we need to write headers (if file doesn't exist)
    file_exists = os.path.isfile(csv_file)
    
    # Define the fields we want to capture in the CSV
    csv_fields = [
        'timestamp', 'date_time', 'airtable_id', 'frame_name', 
        'folder_name', 'folder_path', 'chunk_count', 'webhook_source', 
        'json_path', 'success', 'embedding_model', 'embedding_dimension',
        'metadata_description', 'metadata_context', 'metadata_stage'
    ]
    
    # Create a row for the CSV
    timestamp = payload.get('timestamp', asyncio.get_event_loop().time())
    date_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    # Extract embedding info if available
    embedding_model = "unknown"
    embedding_dimension = 0
    try:
        if payload.get('embeddings'):
            embeddings_data = json.loads(payload.get('embeddings', '{}'))
            embedding_model = embeddings_data.get('model', 'unknown')
            embedding_dimension = embeddings_data.get('dimension', 0)
    except:
        pass
    
    # Extract useful metadata fields if available
    metadata = payload.get('metadata', {})
    metadata_description = metadata.get('Summary', '')
    metadata_context = metadata.get('ActionsDetected', '')
    metadata_stage = metadata.get('StageOfWork', '')
    
    csv_row = {
        'timestamp': timestamp,
        'date_time': date_time,
        'airtable_id': payload.get('airtable_id', ''),
        'frame_name': payload.get('frame_name', ''),
        'folder_name': payload.get('folder_name', ''),
        'folder_path': payload.get('folder_path', ''),
        'chunk_count': payload.get('chunk_count', 0),
        'webhook_source': payload.get('webhook_source', ''),
        'json_path': f"webhook_payload_{payload.get('frame_name', '').split('.')[0]}.json" if payload.get('frame_name') else '',
        'success': 'pending',  # Will be updated later
        'embedding_model': embedding_model,
        'embedding_dimension': embedding_dimension,
        'metadata_description': metadata_description[:100] + '...' if len(metadata_description) > 100 else metadata_description,
        'metadata_context': metadata_context[:100] + '...' if len(metadata_context) > 100 else metadata_context,
        'metadata_stage': metadata_stage
    }
    
    # Write to CSV file, creating if it doesn't exist
    with open(csv_file, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        if not file_exists:
            writer.writeheader()
        writer.writerow(csv_row)
    
    logger.info(f"Saved payload record to CSV: {csv_file}")
    return csv_row

# Update CSV with webhook send result
def update_csv_status(csv_file: str, airtable_id: str, frame_name: str, success: bool):
    """
    Update the success status in the CSV for a specific payload.
    
    Args:
        csv_file: CSV file path
        airtable_id: Airtable ID to match
        frame_name: Frame name to match
        success: Whether webhook send was successful
    """
    if not os.path.isfile(csv_file):
        logger.warning(f"CSV file not found: {csv_file}")
        return
    
    # Read current CSV content
    rows = []
    with open(csv_file, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Update matching row
            if row.get('airtable_id') == airtable_id and row.get('frame_name') == frame_name:
                row['success'] = 'success' if success else 'failed'
            rows.append(row)
    
    # Write updated content back
    with open(csv_file, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    
    logger.info(f"Updated webhook status in CSV for {frame_name}: {'success' if success else 'failed'}")

async def process_frame_direct(
    frame_path: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    max_chunks: Optional[int] = None,
    use_test_webhook: bool = True,
    save_payload: bool = True,
    csv_file: str = "payloads/csv/webhook_payloads.csv",
    local_only: bool = False,
    local_storage_dir: Optional[str] = None,
    overwrite_airtable: bool = False
) -> bool:
    """
    Directly process a frame and send to webhook.
    
    Args:
        frame_path: Path to the frame file
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        max_chunks: Maximum number of chunks to process
        use_test_webhook: Whether to use the test webhook URL
        save_payload: Whether to save the payload to a file
        csv_file: CSV file to save payload records to
        local_only: If True, only store locally and don't send to webhook
        local_storage_dir: Directory to store local payload files
        overwrite_airtable: Whether to overwrite existing OCR Data and Flagged fields in Airtable
        
    Returns:
        True if successfully processed and sent
    """
    logger.info(f"Processing frame: {frame_path}")
    
    try:
        # Step 1: Load the frame image
        logger.info(f"Loading image: {frame_path}")
        img = Image.open(frame_path)
        logger.info(f"Frame loaded: {img.size}px {img.format}")
        
        # Step 2: Find metadata for the frame
        logger.info("Finding Airtable metadata...")
        metadata_finder = AirtableMetadataFinder(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        record = metadata_finder.find_record_by_frame_path(frame_path)
        
        if not record:
            logger.error(f"No metadata found for frame: {frame_path}")
            return False
        
        # Extract fields from the record
        metadata = record.get('fields', {})
        airtable_id = record.get('id')
        logger.info(f"Found metadata for frame with ID: {airtable_id}")
        
        # Check if this frame has already been processed and has OCR data
        ocr_data_exists = metadata.get('OCRData')
        if ocr_data_exists and not overwrite_airtable:
            logger.info(f"Frame already has OCR data and overwrite is not enabled: {frame_path}")
            return False
            
        # Step 3: Initialize the metadata chunker
        logger.info(f"Initializing metadata chunker (chunk_size={chunk_size}, overlap={chunk_overlap})...")
        chunker = MetadataChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        # Step 4: Process metadata into chunks
        logger.info("Processing metadata into chunks...")
        chunks = chunker.process_metadata(metadata, airtable_id, frame_path)
        logger.info(f"Generated {len(chunks)} chunks")
        
        # Limit the number of chunks if specified
        if max_chunks is not None and max_chunks > 0:
            original_chunks = len(chunks)
            chunks = chunks[:max_chunks]
            logger.info(f"Limiting to first {max_chunks} chunks out of {original_chunks}")
        
        # SKIP EMBEDDINGS: Using placeholder instead of real embeddings
        logger.info("Skipping embedding generation as requested")
        
        # Initialize embedded_chunks with placeholder data
        embedded_chunks = []
        for i, chunk in enumerate(chunks):
            embedded_chunks.append({
                "chunk": chunk,
                "embedding": []  # Empty embedding
            })
            
        # Format embedding data for JSON (minimal version)
        embedding_data = {
            "model": "OCR-only",
            "dimension": 0,
            "count": len(chunks),
            "created_at": int(asyncio.get_event_loop().time()),
            "chunks": [],
            "vectors": []
        }
        
        # Add chunk data without embeddings
        for i, embed_chunk in enumerate(embedded_chunks):
            chunk_data = {
                "sequence_id": embed_chunk["chunk"]["chunk_sequence_id"],
                "text_length": len(embed_chunk["chunk"]["chunk_text"]),
                "text": embed_chunk["chunk"]["chunk_text"],
                "text_preview": embed_chunk["chunk"]["chunk_text"][:100] + "..." if len(embed_chunk["chunk"]["chunk_text"]) > 100 else embed_chunk["chunk"]["chunk_text"],
                "embedding_preview": []
            }
            embedding_data["chunks"].append(chunk_data)
            embedding_data["vectors"].append([])
        
        # Convert to JSON string for the webhook
        embeddings_json = json.dumps(embedding_data)
        
        # Get frame name and folder information
        frame_name = os.path.basename(frame_path)
        folder_path = os.path.dirname(frame_path)
        folder_name = os.path.basename(folder_path)
        timestamp = asyncio.get_event_loop().time()
        
        # Prepare minimal payload (no embeddings)
        webhook_payload = {
            "airtable_id": airtable_id,
            "frame_name": frame_name,
            "folder_path": folder_path,
            "folder_name": folder_name,
            "chunk_count": len(chunks),
            "metadata": metadata,
            "timestamp": timestamp
        }
        
        # Create directories if needed
        os.makedirs(os.path.dirname(csv_file), exist_ok=True)  # Ensure CSV directory exists
        
        # Create storage directory if needed
        if local_storage_dir:
            os.makedirs(local_storage_dir, exist_ok=True)
        
        # Save minimal CSV data
        csv_row = save_payload_to_csv(webhook_payload, csv_file)
        
        # Update Airtable record - THIS IS THE MAIN GOAL
        if overwrite_airtable:
            logger.info(f"Updating Airtable record with OCR data for frame: {frame_name}")
            try:
                # Prepare OCR data summary (no embeddings)
                ocr_summary = {
                    "chunks_count": len(chunks),
                    "embedding_model": "OCR-only",
                    "embedding_dimension": 0,
                    "processed_at": datetime.datetime.now().isoformat(),
                    "status": "processed",
                    "chunk_texts": [chunk["chunk_text"] for chunk in chunks]
                }
                
                # Update Airtable record
                update_data = {
                    "OCRData": json.dumps(ocr_summary),
                    "Flagged": False  # Reset flag
                }
                
                metadata_finder.update_record(airtable_id, update_data)
                logger.info(f"Successfully updated Airtable record for {frame_path}")
            except Exception as e:
                logger.error(f"Failed to update Airtable record for {frame_path}: {e}")
                # Continue processing - don't fail the whole operation
        
        # Always return success for local mode
        return True
            
    except Exception as e:
        logger.error(f"Error processing frame {frame_path}: {e}")
        import traceback
        logger.error(f"Exception details: {traceback.format_exc()}")
        return False

async def process_multiple_frames(
    input_path: str,
    pattern: str = "*.jpg",
    limit: Optional[int] = None,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    max_chunks: Optional[int] = None,
    sequential: bool = True,
    use_test_webhook: bool = True,
    save_payload: bool = True,
    csv_file: str = "payloads/csv/webhook_payloads.csv",
    local_only: bool = False,
    local_storage_dir: Optional[str] = None,
    overwrite_airtable: bool = False,
    skip_processed: bool = False
) -> Dict[str, Any]:
    """
    Process multiple frames and send to webhook.
    
    Args:
        input_path: Path to directory containing frames or a single frame
        pattern: File pattern to match (if input_path is a directory)
        limit: Maximum number of frames to process
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        max_chunks: Maximum number of chunks per frame
        sequential: Whether to process frames sequentially
        use_test_webhook: Whether to use the test webhook URL (not used in OCR-only mode)
        save_payload: Whether to save the payloads to disk (not used in OCR-only mode)
        csv_file: CSV file to save payload records to
        local_only: If True, only store locally and don't send to webhook (always true in OCR-only mode)
        local_storage_dir: Directory to store local payload files
        overwrite_airtable: Whether to overwrite existing OCR Data and Flagged fields in Airtable
        skip_processed: Whether to skip frames that have already been processed (have OCR Data)
        
    Returns:
        Dictionary with processing results
    """
    import glob
    
    # Create storage directory if provided
    if local_storage_dir:
        os.makedirs(local_storage_dir, exist_ok=True)
    
    # Validate input path
    input_path = Path(input_path)
    if not input_path.exists():
        logger.error(f"Input path does not exist: {input_path}")
        return {"success": False, "error": f"Input path does not exist: {input_path}"}
    
    # Get list of files to process
    files = []
    if input_path.is_dir():
        # Process all files matching pattern in directory
        pattern_path = os.path.join(str(input_path), pattern)
        files = sorted(glob.glob(pattern_path))
        logger.info(f"Found {len(files)} files matching pattern '{pattern}' in {input_path}")
    else:
        # Process a single file
        files = [str(input_path)]
        logger.info(f"Processing single file: {input_path}")
    
    # Apply limit if specified
    if limit and len(files) > limit:
        logger.info(f"Limiting to {limit} files (out of {len(files)})")
        files = files[:limit]
    
    results = {
        "total_files": len(files),
        "processed_files": 0,
        "successful_files": 0,
        "failed_files": 0,
        "files": []
    }
    
    # Create a summary file if using local storage
    if local_storage_dir:
        summary_file = os.path.join(local_storage_dir, "processing_summary.json")
        # Initialize summary with processing parameters
        summary_data = {
            "processing_parameters": {
                "input_path": str(input_path),
                "pattern": pattern,
                "limit": limit,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "max_chunks": max_chunks,
                "sequential": sequential,
                "use_test_webhook": use_test_webhook,
                "local_only": local_only,
                "overwrite_airtable": overwrite_airtable,
                "skip_processed": skip_processed
            },
            "start_time": datetime.datetime.now().isoformat(),
            "files": []
        }
    
    if sequential:
        # Process files sequentially
        for file_path in files:
            # Check if frame has already been processed
            if skip_processed:
                # Check if the frame has already been processed by looking at Airtable
                logger.info(f"Checking if frame has already been processed: {file_path}")
                metadata_finder = AirtableMetadataFinder(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
                record = metadata_finder.find_record_by_frame_path(file_path)
                
                if record and record.get('fields', {}).get('OCRData'):
                    logger.info(f"Skipping already processed frame with OCR data: {file_path}")
                    results["processed_files"] += 1
                    results["successful_files"] += 1  # Count as successful since it's already done
                    
                    file_result = {
                        "path": file_path,
                        "success": True,
                        "status": "skipped",
                        "reason": "Frame has already been processed with OCR data"
                    }
                    results["files"].append(file_result)
                    
                    # Add to summary if using local storage
                    if local_storage_dir:
                        summary_data["files"].append({
                            "path": file_path,
                            "frame_name": os.path.basename(file_path),
                            "success": True,
                            "status": "skipped",
                            "reason": "Frame has already been processed with OCR data",
                            "timestamp": datetime.datetime.now().isoformat()
                        })
                        # Update summary file after each frame
                        with open(summary_file, 'w') as f:
                            json.dump(summary_data, f, indent=2)
                    
                    logger.info(f"Processed {results['processed_files']}/{results['total_files']} files (skipped: {file_path})")
                    continue
            
            # Process the frame if we didn't skip it
            success = await process_frame_direct(
                frame_path=file_path,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                max_chunks=max_chunks,
                use_test_webhook=use_test_webhook,
                save_payload=save_payload,
                csv_file=csv_file,
                local_only=True,  # Force local-only mode for OCR-only processing
                local_storage_dir=local_storage_dir,
                overwrite_airtable=overwrite_airtable
            )
            
            results["processed_files"] += 1
            if success:
                results["successful_files"] += 1
            else:
                results["failed_files"] += 1
                
            file_result = {
                "path": file_path,
                "success": success
            }
            results["files"].append(file_result)
            
            # Add to summary if using local storage
            if local_storage_dir:
                summary_data["files"].append({
                    "path": file_path,
                    "frame_name": os.path.basename(file_path),
                    "success": success,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                # Update summary file after each frame
                with open(summary_file, 'w') as f:
                    json.dump(summary_data, f, indent=2)
            
            logger.info(f"Processed {results['processed_files']}/{results['total_files']} files")
    else:
        # If skip_processed is true, pre-filter files that have already been processed
        files_to_process = []
        if skip_processed:
            metadata_finder = AirtableMetadataFinder(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
            
            for file_path in files:
                # Check if the frame has already been processed
                record = metadata_finder.find_record_by_frame_path(file_path)
                if record and record.get('fields', {}).get('OCRData'):
                    logger.info(f"Skipping already processed frame with OCR data: {file_path}")
                    results["processed_files"] += 1
                    results["successful_files"] += 1  # Count as successful since it's already done
                    
                    file_result = {
                        "path": file_path,
                        "success": True,
                        "status": "skipped",
                        "reason": "Frame has already been processed with OCR data"
                    }
                    results["files"].append(file_result)
                    
                    # Add to summary if using local storage
                    if local_storage_dir:
                        summary_data["files"].append({
                            "path": file_path,
                            "frame_name": os.path.basename(file_path),
                            "success": True,
                            "status": "skipped",
                            "reason": "Frame has already been processed with OCR data",
                            "timestamp": datetime.datetime.now().isoformat()
                        })
                else:
                    files_to_process.append(file_path)
        else:
            files_to_process = files
            
        if not files_to_process:
            logger.info("No files to process after filtering already processed frames")
        else:
            logger.info(f"Processing {len(files_to_process)} files in parallel")
            
            # Create tasks for processing (in OCR-only mode)
            tasks = []
            for file_path in files_to_process:
                task = process_frame_direct(
                    frame_path=file_path,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    max_chunks=max_chunks,
                    use_test_webhook=use_test_webhook,
                    save_payload=save_payload,
                    csv_file=csv_file,
                    local_only=True,  # Force local-only mode for OCR-only processing
                    local_storage_dir=local_storage_dir,
                    overwrite_airtable=overwrite_airtable
                )
                tasks.append(task)
                
            # Wait for all tasks to complete
            frame_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(frame_results):
                file_path = files_to_process[i]
                
                results["processed_files"] += 1
                
                if isinstance(result, Exception):
                    logger.error(f"Error processing {file_path}: {result}")
                    results["failed_files"] += 1
                    
                    file_result = {
                        "path": file_path,
                        "success": False,
                        "error": str(result)
                    }
                    results["files"].append(file_result)
                    
                    # Add to summary if using local storage
                    if local_storage_dir:
                        summary_data["files"].append({
                            "path": file_path,
                            "frame_name": os.path.basename(file_path),
                            "success": False,
                            "error": str(result),
                            "timestamp": datetime.datetime.now().isoformat()
                        })
                else:
                    if result:
                        results["successful_files"] += 1
                    else:
                        results["failed_files"] += 1
                        
                    file_result = {
                        "path": file_path,
                        "success": result
                    }
                    results["files"].append(file_result)
                    
                    # Add to summary if using local storage
                    if local_storage_dir:
                        summary_data["files"].append({
                            "path": file_path,
                            "frame_name": os.path.basename(file_path),
                            "success": result,
                            "timestamp": datetime.datetime.now().isoformat()
                        })
    
    # Final update to summary if using local storage
    if local_storage_dir:
        summary_data["end_time"] = datetime.datetime.now().isoformat()
        summary_data["results"] = {
            "total_files": results["total_files"],
            "processed_files": results["processed_files"],
            "successful_files": results["successful_files"],
            "failed_files": results["failed_files"]
        }
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2)
    
    # Print summary
    logger.info(f"Processing complete: {results['successful_files']} successful, "
               f"{results['failed_files']} failed out of {results['total_files']} files")
    
    return results

# Create a compatibility function that uses FrameProcessor class
async def process_frame(frame_path, **kwargs):
    """Compatibility function that uses FrameProcessor class"""
    processor = FrameProcessor()
    return await processor.process_frame(frame_path, **kwargs)

async def main():
    """Entry point for the application."""
    parser = argparse.ArgumentParser(description="Database Advanced Tokenizer - Process frames and create embeddings")
    
    # Input options
    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument("--input", required=True, help="Input file or directory path")
    input_group.add_argument("--pattern", default="*.jpg", help="Glob pattern for image files (default: *.jpg)")
    input_group.add_argument("--limit", type=int, default=3, help="Maximum number of files to process (default: 3)")
    
    # Processing options
    processing_group = parser.add_argument_group("Processing Options")
    processing_group.add_argument("--chunk-size", type=int, default=500, help="Size of text chunks (default: 500)")
    processing_group.add_argument("--chunk-overlap", type=int, default=50, help="Overlap between chunks (default: 50)")
    processing_group.add_argument("--max-chunks", type=int, default=5, help="Maximum number of chunks per frame (default: 5)")
    processing_group.add_argument("--sequential", action="store_true", help="Process files sequentially (default: True)")
    
    # Webhook options
    webhook_group = parser.add_argument_group("Webhook Options")
    webhook_group.add_argument("--production", action="store_true", help="Use production webhook (default: test webhook)")
    webhook_group.add_argument("--no-save", action="store_true", help="Don't save payload files (default: save)")
    webhook_group.add_argument("--csv-file", default="payloads/csv/webhook_payloads.csv", help="CSV file to store payload records (default: payloads/csv/webhook_payloads.csv)")
    
    # Local storage options
    local_group = parser.add_argument_group("Local Storage Options")
    local_group.add_argument("--local-only", action="store_true", help="Only store locally, don't send to webhook")
    local_group.add_argument("--local-storage-dir", default="frame_embeddings", help="Directory to store local payload and embedding files (default: frame_embeddings)")
    
    # Airtable options
    airtable_group = parser.add_argument_group("Airtable Options")
    airtable_group.add_argument("--overwrite-airtable", action="store_true", 
                               help="Overwrite existing OCR Data and Flagged fields in Airtable even if they already exist")
    airtable_group.add_argument("--skip-processed", action="store_true", 
                               help="Skip frames that already have OCR Data in Airtable (faster processing for incremental updates)")
    
    args = parser.parse_args()
    
    # Process frames
    results = await process_multiple_frames(
        input_path=args.input,
        pattern=args.pattern,
        limit=args.limit,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        max_chunks=args.max_chunks,
        sequential=True,  # Always sequential for now to avoid webhook race conditions
        use_test_webhook=not args.production,
        save_payload=not args.no_save,
        csv_file=args.csv_file,
        local_only=args.local_only,
        local_storage_dir=args.local_storage_dir if not args.no_save else None,
        overwrite_airtable=args.overwrite_airtable,
        skip_processed=args.skip_processed
    )
    
    # Print summary
    print(f"\nProcessing summary:")
    print(f"  Total files: {results['total_files']}")
    print(f"  Successfully processed and sent: {results['successful_files']}")
    print(f"  Failed: {results['failed_files']}")
    
    if args.local_only:
        print(f"\nData stored locally in: {args.local_storage_dir}")
        print(f"CSV record: {args.csv_file}")
    
    if args.overwrite_airtable:
        print(f"\nAirtable records were updated with OCR data and Flagged status reset")
    
    if args.skip_processed:
        skipped_count = sum(1 for file in results['files'] if file.get('status') == 'skipped')
        if skipped_count > 0:
            print(f"\nSkipped {skipped_count} already processed frames with existing OCR data")
    
    # Return exit code
    return 0 if results["failed_files"] == 0 else 1

if __name__ == "__main__":
    asyncio.run(main()) 