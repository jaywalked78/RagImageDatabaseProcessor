#!/usr/bin/env python3
"""
Script to directly process a frame, create embeddings, and send to webhook.
This script takes a more direct approach instead of relying on process_frame.
"""

import os
import sys
import json
import logging
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import numpy as np
import aiohttp
from PIL import Image
import csv
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("direct_frame_webhook")

# Load environment variables
load_dotenv()
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
WEBHOOK_TEST_URL = os.environ.get('WEBHOOK_TEST_URL')
FRAME_BASE_DIR = os.environ.get('FRAME_BASE_DIR', '/home/jason/Videos/screenRecordings')
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', 'tblFrameAnalysis')

# Import key components we need
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from test_chunk_embedding import ChunkEmbedder, MetadataChunker, AirtableMetadataFinder
from test_webhook import send_webhook_payload

# Add function to save payload to CSV
def save_payload_to_csv(payload: Dict[str, Any], csv_file: str = "payloads/csv/webhook_payloads.csv"):
    """
    Save webhook payload data to a CSV file for local record keeping.
    
    Args:
        payload: The webhook payload dictionary
        csv_file: CSV file path to save to
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    
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
    csv_file: str = "payloads/csv/webhook_payloads.csv"
) -> bool:
    """
    Directly process a frame and send to webhook without using process_frame.
    
    Args:
        frame_path: Path to the frame file
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        max_chunks: Maximum number of chunks to process
        use_test_webhook: Whether to use the test webhook URL
        save_payload: Whether to save the payload to a file
        csv_file: CSV file to save payload records to
        
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
        
        # Step 5: Initialize the chunk embedder
        logger.info("Initializing chunk embedder...")
        embedder = ChunkEmbedder(use_key_rotation=True)
        
        # Step 6: Create embeddings for all chunks
        logger.info("Creating embeddings for chunks...")
        embedded_chunks = await embedder.embed_chunks(chunks, img)
        
        # Step 7: Prepare webhook payload
        if not embedded_chunks:
            logger.error("Failed to create embeddings")
            return False
            
        logger.info(f"Successfully embedded {len(embedded_chunks)} out of {len(chunks)} chunks")
        
        # Format embedding vectors for JSON
        embedding_data = {
            "model": "voyage-multimodal-3",
            "dimension": len(embedded_chunks[0]["embedding"]) if embedded_chunks else 0,
            "count": len(embedded_chunks),
            "created_at": int(asyncio.get_event_loop().time()),
            "chunks": [],
            "vectors": []
        }
        
        # Add each chunk's data
        for i, embed_chunk in enumerate(embedded_chunks):
            # Convert numpy arrays to lists if needed
            embedding_vector = embed_chunk["embedding"]
            if isinstance(embedding_vector, np.ndarray):
                embedding_vector = embedding_vector.tolist()
                
            # Add chunk metadata
            chunk_data = {
                "sequence_id": embed_chunk["chunk"]["chunk_sequence_id"],
                "text_length": len(embed_chunk["chunk"]["chunk_text"]),
                "text_preview": embed_chunk["chunk"]["chunk_text"][:100] + "..." if len(embed_chunk["chunk"]["chunk_text"]) > 100 else embed_chunk["chunk"]["chunk_text"],
                "embedding_preview": embedding_vector[:5] + ["..."] + embedding_vector[-5:],
            }
            embedding_data["chunks"].append(chunk_data)
            
            # Add full vector to the vectors array
            embedding_data["vectors"].append(embedding_vector)
        
        # Convert to JSON string
        embeddings_json = json.dumps(embedding_data)
        
        # Get frame name and folder information
        frame_name = os.path.basename(frame_path)
        folder_path = os.path.dirname(frame_path)
        folder_name = os.path.basename(folder_path)
        
        # Prepare webhook payload
        webhook_payload = {
            "airtable_id": airtable_id,
            "frame_name": frame_name,
            "folder_path": folder_path,
            "folder_name": folder_name,
            "chunk_count": len(embedded_chunks),
            "embeddings": embeddings_json,
            "metadata": metadata,
            "webhook_source": "test" if use_test_webhook else "production",
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Save payload to file if requested
        if save_payload:
            # Ensure directory exists
            os.makedirs("payloads/json", exist_ok=True)
            
            payload_file = f"payloads/json/webhook_payload_{frame_name.split('.')[0]}.json"
            with open(payload_file, 'w') as f:
                json.dump(webhook_payload, f, indent=2)
            
            logger.info(f"Saved payload to {payload_file}")
        
        # Save payload record to CSV
        csv_row = save_payload_to_csv(webhook_payload, csv_file)
        
        # Send to webhook
        webhook_url = WEBHOOK_TEST_URL if use_test_webhook else WEBHOOK_URL
        if not webhook_url:
            logger.error("No webhook URL configured")
            return False
            
        logger.info(f"Sending data to webhook: {webhook_url}")
        success = await send_webhook_payload(webhook_url, webhook_payload)
        
        if success:
            logger.info(f"Successfully sent data to webhook for {frame_path}")
            # Update CSV with success status
            update_csv_status(csv_file, airtable_id, frame_name, True)
            return True
        else:
            logger.error(f"Failed to send data to webhook for {frame_path}")
            # Update CSV with failure status
            update_csv_status(csv_file, airtable_id, frame_name, False)
            return False
            
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
    csv_file: str = "payloads/csv/webhook_payloads.csv"
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
        use_test_webhook: Whether to use the test webhook URL
        save_payload: Whether to save the payloads to disk
        csv_file: CSV file to save payload records to
        
    Returns:
        Dictionary with processing results
    """
    import glob
    
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
    
    if sequential:
        # Process files sequentially
        for file_path in files:
            try:
                success = await process_frame_direct(
                    frame_path=file_path,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    max_chunks=max_chunks,
                    use_test_webhook=use_test_webhook,
                    save_payload=save_payload,
                    csv_file=csv_file
                )
                
                results["processed_files"] += 1
                if success:
                    results["successful_files"] += 1
                else:
                    results["failed_files"] += 1
                    
                results["files"].append({
                    "path": file_path,
                    "success": success
                })
                
                logger.info(f"Processed {results['processed_files']}/{results['total_files']} files")
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                results["failed_files"] += 1
                results["processed_files"] += 1
                results["files"].append({
                    "path": file_path,
                    "success": False,
                    "error": str(e)
                })
    else:
        # Process files in parallel (with limited concurrency)
        tasks = []
        for file_path in files:
            task = process_frame_direct(
                frame_path=file_path,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                max_chunks=max_chunks,
                use_test_webhook=use_test_webhook,
                save_payload=save_payload,
                csv_file=csv_file
            )
            tasks.append(task)
            
        # Wait for all tasks to complete
        frame_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(frame_results):
            file_path = files[i]
            
            results["processed_files"] += 1
            
            if isinstance(result, Exception):
                logger.error(f"Error processing {file_path}: {result}")
                results["failed_files"] += 1
                results["files"].append({
                    "path": file_path,
                    "success": False,
                    "error": str(result)
                })
            else:
                if result:
                    results["successful_files"] += 1
                else:
                    results["failed_files"] += 1
                    
                results["files"].append({
                    "path": file_path,
                    "success": result
                })
    
    # Print summary
    logger.info(f"Processing complete: {results['successful_files']} successful, "
               f"{results['failed_files']} failed out of {results['total_files']} files")
    
    return results

async def main():
    """Entry point for the script."""
    parser = argparse.ArgumentParser(description="Process frames and send to webhook")
    
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
        csv_file=args.csv_file
    )
    
    # Print summary
    print(f"\nProcessing summary:")
    print(f"  Total files: {results['total_files']}")
    print(f"  Successfully processed and sent: {results['successful_files']}")
    print(f"  Failed: {results['failed_files']}")
    
    # Return exit code
    return 0 if results["failed_files"] == 0 else 1

if __name__ == "__main__":
    asyncio.run(main()) 