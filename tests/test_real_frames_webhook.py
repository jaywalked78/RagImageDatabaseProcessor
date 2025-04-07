#!/usr/bin/env python3
"""
Script to process a few real frames and send actual data to the webhook.
Combines functionality from test_chunk_embedding.py and our webhook testing scripts.
"""

import os
import sys
import json
import logging
import asyncio
import argparse
import glob
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import numpy as np

# Import from existing modules
from test_chunk_embedding import process_frame, ChunkEmbedder, AirtableEmbeddingStore
from test_webhook import send_webhook_payload

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("real_frames_test")

# Load environment variables
load_dotenv()
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
WEBHOOK_TEST_URL = os.environ.get('WEBHOOK_TEST_URL')
FRAME_BASE_DIR = os.environ.get('FRAME_BASE_DIR', '/home/jason/Videos/screenRecordings')

# Create a custom AirtableEmbeddingStore that will capture the embeddings instead of sending them
class CapturingEmbeddingStore(AirtableEmbeddingStore):
    def __init__(self):
        print("Initializing CapturingEmbeddingStore")
        super().__init__(use_webhook=False)
        self.captured_data = None
        self.embedded_chunks = None
        
    def _format_embeddings_json(self, embeddings):
        """Format embedding vectors for storage in Airtable.
        Overriding to also store the original embeddings for our use.
        """
        print(f"_format_embeddings_json called with {len(embeddings)} embeddings")
        # Store the original embeddings
        self.embedded_chunks = embeddings
        
        # Call the parent method to format JSON
        json_data = super()._format_embeddings_json(embeddings)
        print(f"JSON data formatted, length: {len(json_data)}")
        return json_data
    
    async def save_embeddings(self, record_id, embeddings, frame_path=None):
        """Capture the embeddings instead of sending them to Airtable."""
        print(f"save_embeddings called with record_id: {record_id}, embeddings: {len(embeddings)}")
        # Format embeddings the same way AirtableEmbeddingStore would
        embeddings_json = self._format_embeddings_json(embeddings)
        chunk_count = len(embeddings)
        
        # Extract frame details
        frame_name = os.path.basename(frame_path) if frame_path else "unknown"
        folder_path = str(Path(frame_path).parent) if frame_path else ""
        folder_name = Path(frame_path).parent.name if frame_path else ""
        
        # Save the data
        self.captured_data = {
            "airtable_id": record_id,
            "embeddings": embeddings_json,
            "chunk_count": chunk_count,
            "frame_path": frame_path,
            "frame_name": frame_name,
            "folder_path": folder_path,
            "folder_name": folder_name,
            "webhook_source": "test",
            "timestamp": asyncio.get_event_loop().time(),
            "raw_embeddings": [
                {
                    "chunk_text": chunk_data["chunk"]["chunk_text"],
                    "embedding": chunk_data["embedding"].tolist() if isinstance(chunk_data["embedding"], np.ndarray) else chunk_data["embedding"],
                    "chunk_sequence_id": chunk_data["chunk"]["chunk_sequence_id"]
                }
                for chunk_data in embeddings
            ]
        }
        
        # Log success
        print(f"Captured data stored with {chunk_count} chunks")
        logger.info(f"Captured embeddings for {record_id}: {chunk_count} chunks")
        return True

async def process_and_send(
    frame_path: str, 
    chunk_size: int = 500, 
    chunk_overlap: int = 50,
    max_chunks: Optional[int] = None,
    use_test_webhook: bool = True,
    save_payloads: bool = True
) -> bool:
    """
    Process a single frame and send the real data to the webhook.
    
    Args:
        frame_path: Path to the frame file
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        max_chunks: Maximum number of chunks to process
        use_test_webhook: Whether to use the test webhook URL
        save_payloads: Whether to save the payloads to disk
        
    Returns:
        True if successfully processed and sent
    """
    logger.info(f"Processing frame: {frame_path}")
    
    try:
        # Create our capturing store
        print("Creating CapturingEmbeddingStore instance")
        embedding_store = CapturingEmbeddingStore()
        
        # Process the frame - this will find metadata in Airtable, chunk it, and create embeddings
        print("Calling process_frame with our custom embedding store")
        success = await process_frame(
            frame_path=frame_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            max_chunks=max_chunks,
            force_reprocess=True,
            save_to_airtable=False,  # Don't save to Airtable directly
            save_to_postgres=False,  # Don't save to Postgres
            airtable_store=embedding_store,  # Use our capturing store
            use_webhook=False  # We'll handle the webhook ourselves
        )
        print(f"process_frame returned: {success}")
        
        if not success:
            logger.error(f"Failed to process frame: {frame_path}")
            return False
        
        # Ensure we captured data
        print(f"Checking captured_data: {embedding_store.captured_data is not None}")
        if not embedding_store.captured_data:
            print(f"embedded_chunks attribute: {embedding_store.embedded_chunks is not None}")
            if embedding_store.embedded_chunks:
                print(f"We have embedded_chunks but no captured_data: {len(embedding_store.embedded_chunks)} chunks")
                # Try to manually create the captured_data
                record = None
                metadata_finder = None
                try:
                    from test_chunk_embedding import AirtableMetadataFinder
                    import os
                    metadata_finder = AirtableMetadataFinder()
                    record = metadata_finder.find_record_by_frame_path(frame_path)
                    print(f"Found record: {record is not None}")
                except Exception as e:
                    print(f"Error finding record: {e}")
                
                if record and embedding_store.embedded_chunks:
                    airtable_id = record.get('id')
                    embeddings = embedding_store.embedded_chunks
                    embeddings_json = embedding_store._format_embeddings_json(embeddings)
                    
                    # Manually create captured_data
                    embedding_store.captured_data = {
                        "airtable_id": airtable_id,
                        "embeddings": embeddings_json,
                        "chunk_count": len(embeddings),
                        "frame_path": frame_path,
                        "frame_name": os.path.basename(frame_path),
                        "folder_path": str(Path(frame_path).parent),
                        "folder_name": Path(frame_path).parent.name,
                        "webhook_source": "test",
                        "manually_created": True
                    }
                    print("Manually created captured_data")
            
            logger.error(f"No data captured for frame: {frame_path}")
            return False
        
        # Get the payload
        payload = embedding_store.captured_data
        print(f"Payload keys: {list(payload.keys())}")
        
        # Save the payload to a JSON file if requested
        if save_payloads:
            frame_name = os.path.basename(frame_path)
            payload_file = f"webhook_payload_{frame_name.split('.')[0]}.json"
            with open(payload_file, 'w') as f:
                json.dump(payload, f, indent=2)
            logger.info(f"Saved webhook payload to: {payload_file}")
        
        # Get the appropriate webhook URL
        webhook_url = WEBHOOK_TEST_URL if use_test_webhook else WEBHOOK_URL
        if not webhook_url:
            logger.error("No webhook URL configured. Set WEBHOOK_TEST_URL or WEBHOOK_URL in environment.")
            return False
        
        # Send to webhook
        logger.info(f"Sending data to webhook: {webhook_url}")
        webhook_payload = {
            "airtable_id": payload["airtable_id"],
            "frame_name": payload["frame_name"],
            "folder_path": payload["folder_path"],
            "folder_name": payload["folder_name"],
            "chunk_count": payload["chunk_count"],
            "embeddings": payload["embeddings"],
            "timestamp": payload["timestamp"],
            "webhook_source": payload["webhook_source"]
        }
        success = await send_webhook_payload(webhook_url, webhook_payload)
        
        if success:
            logger.info(f"Successfully sent data to webhook for {frame_path}")
            return True
        else:
            logger.error(f"Failed to send data to webhook for {frame_path}")
            return False
        
    except Exception as e:
        logger.error(f"Error processing and sending frame {frame_path}: {e}")
        import traceback
        print(f"Exception traceback: {traceback.format_exc()}")
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
    save_payloads: bool = True
) -> Dict[str, Any]:
    """
    Process multiple frames and send each to the webhook.
    
    Args:
        input_path: Path to directory containing frames or a single frame
        pattern: File pattern to match (if input_path is a directory)
        limit: Maximum number of frames to process
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        max_chunks: Maximum number of chunks per frame
        sequential: Whether to process frames sequentially
        use_test_webhook: Whether to use the test webhook URL
        save_payloads: Whether to save the payloads to disk
        
    Returns:
        Dictionary with processing results
    """
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
                success = await process_and_send(
                    frame_path=file_path,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    max_chunks=max_chunks,
                    use_test_webhook=use_test_webhook,
                    save_payloads=save_payloads
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
        # Process files in parallel
        tasks = []
        for file_path in files:
            task = process_and_send(
                frame_path=file_path,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                max_chunks=max_chunks,
                use_test_webhook=use_test_webhook,
                save_payloads=save_payloads
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
    parser = argparse.ArgumentParser(description="Process real frames and send to webhook")
    
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
        save_payloads=not args.no_save
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