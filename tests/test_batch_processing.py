#!/usr/bin/env python3
"""
Batch Processing Script for Video Frames with Metadata Chunking

This script demonstrates how to process multiple video frames, find their metadata
in Airtable, and generate semantic chunks for each frame's metadata.
"""

import os
import sys
import glob
import logging
import argparse
import asyncio
from datetime import datetime
from PIL import Image
from pyairtable import Api
from metadata_chunker import MetadataChunker
from test_metadata_chunking import AirtableMetadataFinder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('batch_processor')

def process_frame(frame_path, airtable_finder, chunker):
    """Process a single frame with metadata chunking."""
    try:
        # Load the image to verify it exists
        frame_filename = os.path.basename(frame_path)
        logger.info(f"Processing frame: {frame_filename}")
        
        try:
            img = Image.open(frame_path)
            img_info = f"({img.width}, {img.height})px {img.format}"
            logger.info(f"Frame loaded: {img_info}")
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
            
        # Find metadata in Airtable
        record = airtable_finder.find_record_by_frame_path(frame_path)
        if not record:
            logger.warning(f"No metadata found for {frame_filename}")
            return None
            
        # Extract metadata from record
        metadata = record.get('fields', {})
        airtable_id = record.get('id')
        logger.info(f"Found metadata for frame with ID: {airtable_id}")
            
        # Process metadata into chunks
        logger.info(f"Processing metadata for frame {frame_filename}...")
        chunks = chunker.process_metadata(metadata, airtable_id, frame_path)
        
        logger.info(f"Generated {len(chunks)} chunks for {frame_filename}")
        return {
            'frame_path': frame_path,
            'metadata': metadata,
            'chunks': chunks
        }
    except Exception as e:
        logger.error(f"Error processing frame {frame_path}: {e}")
        return None

def batch_process(frames_directory, pattern="frame_*.jpg", limit=5, chunk_size=500, chunk_overlap=50):
    """Process a batch of frames from the directory."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    airtable_api_key = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    airtable_base_id = 'appewal2KEO5B02KV'  # Hardcode the base ID to ensure it works
    airtable_table_name = 'tblFrameAnalysis'  # Hardcode the table name to ensure it works
    
    if not airtable_api_key:
        logger.error("Missing AIRTABLE_PERSONAL_ACCESS_TOKEN environment variable")
        return
    
    # Initialize the metadata finder and chunker
    airtable_finder = AirtableMetadataFinder(airtable_api_key, airtable_base_id, airtable_table_name)
    chunker = MetadataChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    
    # Find frame files
    frame_pattern = os.path.join(frames_directory, pattern)
    all_frames = sorted(glob.glob(frame_pattern))
    logger.info(f"Found {len(all_frames)} frames matching pattern '{pattern}'")
    
    # Limit the number of frames to process
    frames_to_process = all_frames[:limit]
    
    # Process frames sequentially
    results = []
    for frame in frames_to_process:
        result = process_frame(frame, airtable_finder, chunker)
        if result:
            results.append(result)
    
    # Print summary
    logger.info(f"Batch processing complete. Successfully processed {len(results)} out of {len(frames_to_process)} frames.")
    
    # Generate some simple statistics
    total_chunks = sum(len(r['chunks']) for r in results)
    avg_chunks = total_chunks / len(results) if results else 0
    
    logger.info(f"Total chunks generated: {total_chunks}")
    logger.info(f"Average chunks per frame: {avg_chunks:.2f}")
    
    # Print chunk information for the first processed frame
    if results:
        first_result = results[0]
        logger.info(f"\nDetailed chunk information for first frame ({os.path.basename(first_result['frame_path'])}):")
        for i, chunk in enumerate(first_result['chunks']):
            logger.info(f"  Chunk {i+1}:")
            logger.info(f"    Sequence ID: {chunk['chunk_sequence_id']}")
            logger.info(f"    Text length: {len(chunk['chunk_text'])} characters")
            preview = chunk['chunk_text'][:100] + "..." if len(chunk['chunk_text']) > 100 else chunk['chunk_text']
            logger.info(f"    Preview: {preview}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Batch process video frames with metadata chunking")
    parser.add_argument("frames_directory", help="Directory containing frame images")
    parser.add_argument("--pattern", default="frame_*.jpg", help="Glob pattern for frame files (default: frame_*.jpg)")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of frames to process (default: 5)")
    parser.add_argument("--chunk-size", type=int, default=500, help="Size of text chunks (default: 500)")
    parser.add_argument("--chunk-overlap", type=int, default=50, help="Overlap between chunks (default: 50)")
    args = parser.parse_args()
    
    # Run the batch processing
    start_time = datetime.now()
    batch_process(
        args.frames_directory,
        pattern=args.pattern,
        limit=args.limit,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    end_time = datetime.now()
    logger.info(f"Total processing time: {end_time - start_time}")

if __name__ == "__main__":
    main() 