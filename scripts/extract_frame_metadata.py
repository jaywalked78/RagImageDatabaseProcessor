#!/usr/bin/env python3
"""
Script to extract real metadata for a frame and generate an updated webhook payload.
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Import the metadata finder from our existing script
from process_frame_with_metadata import AirtableMetadataFinder, FRAME_ID_FIELD, FRAME_NUMBER_FIELD, \
    FOLDER_NAME_FIELD, FOLDER_PATH_FIELD, SUMMARY_FIELD, TOOLS_VISIBLE_FIELD, \
    ACTIONS_DETECTED_FIELD, TECHNICAL_DETAILS_FIELD, RELATIONSHIP_TO_PREVIOUS_FIELD, \
    STAGE_OF_WORK_FIELD

# Define additional fields
TIMESTAMP_FIELD = 'Timestamp'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("extract_metadata")

# Load environment variables
load_dotenv()
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID', "appewal2KEO5B02KV")
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', "tblFrameAnalysis")
FRAME_BASE_DIR = os.environ.get('FRAME_BASE_DIR', '/home/jason/Videos/screenRecordings')

# Get test frame path from environment or use default
TEST_FRAME_PATH = os.environ.get('TEST_FRAME_RELATIVE_PATH', 
                               "screen_recording_2025_03_03_at_3_39_52_am/frame_000051.jpg")

# Resolve the full path
if not os.path.isabs(TEST_FRAME_PATH):
    # Replace FRAME_BASE_DIR placeholder if present
    if TEST_FRAME_PATH.startswith('FRAME_BASE_DIR/'):
        TEST_FRAME_PATH = TEST_FRAME_PATH.replace('FRAME_BASE_DIR/', '')
    
    TEST_FRAME_PATH = os.path.join(FRAME_BASE_DIR, TEST_FRAME_PATH)

def create_webhook_payload(frame_path: str, record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a properly formatted webhook payload using real metadata.
    
    Args:
        frame_path: Path to the frame file
        record: Airtable record with metadata
        
    Returns:
        Dictionary payload for webhook
    """
    # Extract fields from the record
    fields = record.get('fields', {})
    
    # Get frame path components
    frame_file = Path(frame_path)
    frame_name = frame_file.name
    
    # Use folder path from Airtable if available, otherwise use local path
    folder_path = fields.get(FOLDER_PATH_FIELD, str(frame_file.parent))
    folder_name = fields.get(FOLDER_NAME_FIELD, frame_file.parent.name)
    
    # Ensure folder path includes frame name
    full_path = os.path.join(folder_path, frame_name) if folder_path else frame_path
    
    # Create the payload
    payload = {
        "airtable_id": record.get('id', ''),
        "frame_name": frame_name,
        "folder_path": folder_path,
        "folder_name": folder_name,
        "full_path": full_path,
        "timestamp": fields.get(TIMESTAMP_FIELD, ''),
        "embeddings": "[0.123, 0.456, 0.789, 0.321, 0.654]",  # Placeholder
        "chunk_count": 5,  # Placeholder
        "metadata": {
            "frame_number": fields.get(FRAME_NUMBER_FIELD, ''),
            "description": fields.get(SUMMARY_FIELD, 'No summary available'),
            "tools_visible": fields.get(TOOLS_VISIBLE_FIELD, []),
            "actions_detected": fields.get(ACTIONS_DETECTED_FIELD, []),
            "technical_details": fields.get(TECHNICAL_DETAILS_FIELD, ''),
            "relationship_to_previous": fields.get(RELATIONSHIP_TO_PREVIOUS_FIELD, ''),
            "stage_of_work": fields.get(STAGE_OF_WORK_FIELD, '')
        }
    }
    
    return payload

async def main():
    """Extract metadata and generate webhook payload."""
    # Validate required configuration
    if not all([AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME]):
        logger.error("Missing required Airtable configuration in environment variables.")
        sys.exit(1)
    
    # Check if frame exists
    if not os.path.exists(TEST_FRAME_PATH):
        logger.error(f"Frame file not found: {TEST_FRAME_PATH}")
        sys.exit(1)
    
    logger.info(f"Extracting metadata for frame: {TEST_FRAME_PATH}")
    
    # Find metadata for the frame
    metadata_finder = AirtableMetadataFinder(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
    record = metadata_finder.find_record_by_frame_path(TEST_FRAME_PATH)
    
    if not record:
        logger.error(f"No metadata found for frame: {TEST_FRAME_PATH}")
        sys.exit(1)
    
    logger.info(f"Found metadata for frame with ID: {record.get('id')}")
    
    # Print raw record for debugging
    logger.info("Raw record fields:")
    for key, value in record.get('fields', {}).items():
        logger.info(f"  {key}: {value}")
    
    # Create webhook payload
    payload = create_webhook_payload(TEST_FRAME_PATH, record)
    
    # Save to JSON file
    output_file = "correct_frame_payload.json"
    with open(output_file, 'w') as f:
        json.dump(payload, f, indent=2)
    
    logger.info(f"Generated webhook payload with real metadata saved to: {output_file}")
    
    # Print the payload
    logger.info("Webhook payload:")
    logger.info(json.dumps(payload, indent=2))

if __name__ == "__main__":
    asyncio.run(main()) 