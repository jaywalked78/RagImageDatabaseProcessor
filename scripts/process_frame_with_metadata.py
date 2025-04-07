"""
Demonstration script showing how to process a frame with its Airtable metadata.
Uses the correct field mappings discovered during testing.
"""

import os
import sys
import logging
import argparse
import asyncio
from PIL import Image
from pathlib import Path
from io import BytesIO
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv
import pyairtable
from pyairtable.api import Api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("frame_processor")

# Load environment variables directly
load_dotenv()
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
# Override with the correct base ID that we confirmed works
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

async def process_frame(frame_path: str, metadata: Dict[str, Any]) -> bool:
    """
    Process a single frame with its metadata.
    This is a demonstration function that would be replaced with your actual processing logic.
    
    Args:
        frame_path: Path to the frame image file
        metadata: Dictionary of metadata from Airtable
        
    Returns:
        True if processing was successful, False otherwise
    """
    try:
        logger.info(f"Processing frame: {frame_path}")
        logger.info(f"Metadata summary: {metadata.get(SUMMARY_FIELD, 'No summary available')}")
        
        # Load the image
        img = Image.open(frame_path)
        logger.info(f"Loaded image: {img.size}px {img.format}")
        
        # Example processing steps:
        # 1. Generate text description from metadata
        description = f"Frame {metadata.get(FRAME_NUMBER_FIELD)} from {metadata.get(FOLDER_NAME_FIELD)}"
        if metadata.get(SUMMARY_FIELD):
            description += f": {metadata.get(SUMMARY_FIELD)}"
        
        # 2. Simulate some processing time
        logger.info(f"Processing with description: {description}")
        await asyncio.sleep(0.5)  # Simulate processing time
        
        # 3. Output processing results
        logger.info("Processing complete!")
        logger.info(f"  Frame number: {metadata.get(FRAME_NUMBER_FIELD)}")
        logger.info(f"  Tools visible: {metadata.get(TOOLS_VISIBLE_FIELD, 'None')}")
        logger.info(f"  Actions detected: {metadata.get(ACTIONS_DETECTED_FIELD, 'None')}")
        logger.info(f"  Stage of work: {metadata.get(STAGE_OF_WORK_FIELD, 'Unknown')}")
        
        return True
    except Exception as e:
        logger.error(f"Error processing frame: {e}")
        return False

async def main(frame_path: str):
    """Main entry point for the script."""
    if not all([AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME]):
        logger.error("Missing required Airtable configuration in environment variables.")
        sys.exit(1)
    
    # Check if frame exists
    if not os.path.exists(frame_path):
        logger.error(f"Frame file not found: {frame_path}")
        sys.exit(1)
    
    # Find metadata for the frame
    metadata_finder = AirtableMetadataFinder(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
    record = metadata_finder.find_record_by_frame_path(frame_path)
    
    if not record:
        logger.error(f"No metadata found for frame: {frame_path}")
        sys.exit(1)
    
    # Extract fields from the record
    metadata = record.get('fields', {})
    logger.info(f"Found metadata for frame with ID: {record.get('id')}")
    
    # Process the frame with its metadata
    success = await process_frame(frame_path, metadata)
    
    if success:
        logger.info("✅ Frame processing completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Frame processing failed.")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a frame with its Airtable metadata')
    parser.add_argument('frame_path', help='Path to the frame image file')
    args = parser.parse_args()
    
    asyncio.run(main(args.frame_path)) 