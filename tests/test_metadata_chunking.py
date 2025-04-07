"""
Test script for metadata chunking pipeline.
This script demonstrates finding frame metadata from Airtable 
and then chunking it for RAG processing.
"""

import os
import sys
import logging
import argparse
import asyncio
from PIL import Image
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import pyairtable
from pyairtable.api import Api

# Import our custom modules
from metadata_chunker import MetadataChunker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_chunking")

# Load environment variables directly
load_dotenv()
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = "appewal2KEO5B02KV"  # Hard-coded to ensure it works
AIRTABLE_TABLE_NAME = "tblFrameAnalysis"

# Field mappings (confirmed from testing)
FRAME_ID_FIELD = 'FrameID'
FRAME_NUMBER_FIELD = 'FrameNumber'
FOLDER_NAME_FIELD = 'FolderName'
FOLDER_PATH_FIELD = 'FolderPath'
TIMESTAMP_FIELD = 'Timestamp'
SUMMARY_FIELD = 'Summary'
TOOLS_VISIBLE_FIELD = 'ToolsVisible'
ACTIONS_DETECTED_FIELD = 'ActionsDetected'
TECHNICAL_DETAILS_FIELD = 'TechnicalDetails'
RELATIONSHIP_TO_PREVIOUS_FIELD = 'RelationshipToPrevious'
STAGE_OF_WORK_FIELD = 'StageOfWork'

class AirtableMetadataFinder:
    """Class to find and retrieve metadata from Airtable for a frame."""
    
    def __init__(self, api_key: str, base_id: str, table_name: str):
        """Initialize with Airtable credentials."""
        self.api_key = api_key
        self.base_id = base_id
        self.table_name = table_name
        self.api = Api(api_key)
        self.table = self.api.table(base_id, table_name)
        logger.info(f"Initialized AirtableMetadataFinder for table {table_name} in base {base_id}")
    
    def find_record_by_frame_path(self, frame_path: str) -> Optional[Dict[str, Any]]:
        """Find an Airtable record that matches the given frame path."""
        frame_file = Path(frame_path)
        filename = frame_file.name
        dir_name = frame_file.parent.name
        frame_num = None
        
        # Try to extract frame number from filename
        if filename.startswith('frame_') and '.' in filename:
            try:
                frame_num = int(filename.split('.')[0].split('_')[1])
            except (IndexError, ValueError):
                logger.warning(f"Couldn't extract frame number from filename: {filename}")
        
        logger.info(f"Looking for metadata for frame: {filename} (number: {frame_num})")
        
        try:
            # Method 1: Match by frame number (most reliable based on testing)
            if frame_num is not None:
                logger.info(f"Searching by frame number: {frame_num}")
                records = self.table.all(
                    fields=[FRAME_ID_FIELD, FRAME_NUMBER_FIELD, FOLDER_NAME_FIELD, FOLDER_PATH_FIELD, 
                            SUMMARY_FIELD, TOOLS_VISIBLE_FIELD, ACTIONS_DETECTED_FIELD, 
                            TECHNICAL_DETAILS_FIELD, RELATIONSHIP_TO_PREVIOUS_FIELD, STAGE_OF_WORK_FIELD],
                    formula=f"{{{FRAME_NUMBER_FIELD}}} = {frame_num}"
                )
                
                if records:
                    if len(records) > 1:
                        # If multiple records with same frame number, try to narrow by folder name
                        logger.info(f"Found {len(records)} records with frame number {frame_num}, trying to narrow by folder name")
                        for record in records:
                            fields = record.get('fields', {})
                            if dir_name == fields.get(FOLDER_NAME_FIELD):
                                logger.info(f"Found exact match with folder name: {dir_name}")
                                return record
                        
                        # If no exact folder match, return the first record
                        logger.info(f"No exact folder match, using first record with frame number {frame_num}")
                        return records[0]
                    else:
                        logger.info(f"Found single record with frame number {frame_num}")
                        return records[0]
            
            # Method 2: Try matching on folder name as fallback
            logger.info(f"Searching by folder name: {dir_name}")
            records = self.table.all(
                fields=[FRAME_ID_FIELD, FRAME_NUMBER_FIELD, FOLDER_NAME_FIELD, FOLDER_PATH_FIELD,
                        SUMMARY_FIELD, TOOLS_VISIBLE_FIELD, ACTIONS_DETECTED_FIELD,
                        TECHNICAL_DETAILS_FIELD, RELATIONSHIP_TO_PREVIOUS_FIELD, STAGE_OF_WORK_FIELD],
                formula=f"{{{FOLDER_NAME_FIELD}}} = '{dir_name}'"
            )
            
            if records:
                # If we found records by folder, try to find the specific frame number
                if frame_num is not None:
                    for record in records:
                        fields = record.get('fields', {})
                        record_frame_num = fields.get(FRAME_NUMBER_FIELD)
                        if record_frame_num == frame_num or record_frame_num == str(frame_num):
                            logger.info(f"Found matching frame {frame_num} in folder {dir_name}")
                            return record
                
                logger.warning(f"No exact frame match in folder {dir_name}")
                return None
            
            logger.warning(f"No matching records found for frame {filename} in folder {dir_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching Airtable: {e}")
            return None

async def process_frame_with_chunking(frame_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    """
    Complete pipeline to process a frame:
    1. Find metadata from Airtable
    2. Chunk the metadata for RAG processing
    3. Display the chunks (in a real pipeline, these would be embedded and stored)
    
    Args:
        frame_path: Path to the frame image file
        chunk_size: Target size for text chunks
        chunk_overlap: Overlap between chunks
    """
    # Check if frame exists
    if not os.path.exists(frame_path):
        logger.error(f"Frame file not found: {frame_path}")
        return False
    
    try:
        # Load the image
        logger.info(f"Loading image: {frame_path}")
        img = Image.open(frame_path)
        logger.info(f"Frame loaded: {img.size}px {img.format}")
        
        # Step 1: Find metadata for the frame
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
        
        # Step 2: Initialize the metadata chunker
        logger.info(f"Initializing metadata chunker (chunk_size={chunk_size}, overlap={chunk_overlap})...")
        chunker = MetadataChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        # Step 3: Process metadata into chunks
        logger.info("Processing metadata into chunks...")
        chunks = chunker.process_metadata(metadata, airtable_id, frame_path)
        
        # Step 4: Display the chunk information (in production, these would be embedded and stored)
        logger.info(f"Generated {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks):
            logger.info(f"\nChunk {i+1}:")
            logger.info(f"  Sequence ID: {chunk['chunk_sequence_id']}")
            logger.info(f"  Text length: {len(chunk['chunk_text'])} characters")
            logger.info(f"  Preview: {chunk['chunk_text'][:150]}...")
        
        # In the full pipeline, you would now:
        # 1. Generate embeddings for each chunk using voyageai
        # 2. Store chunks and embeddings in your vector database
        
        return True
    except Exception as e:
        logger.error(f"Error in processing pipeline: {e}")
        return False

async def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Test metadata chunking pipeline')
    parser.add_argument('frame_path', help='Path to the frame image file')
    parser.add_argument('--chunk-size', type=int, default=500, help='Target size for text chunks')
    parser.add_argument('--chunk-overlap', type=int, default=50, help='Overlap between chunks')
    args = parser.parse_args()
    
    if not AIRTABLE_TOKEN:
        logger.error("AIRTABLE_PERSONAL_ACCESS_TOKEN not set in environment variables.")
        sys.exit(1)
    
    success = await process_frame_with_chunking(
        args.frame_path, 
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    
    if success:
        logger.info("✅ Frame processing and chunking completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Frame processing and chunking failed.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 