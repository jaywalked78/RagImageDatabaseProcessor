"""
Test script for matching a frame file with its Airtable metadata.
Avoids using settings.py to work around environment parsing issues.
"""

import os
import sys
import logging
import argparse
import requests
from PIL import Image
from pathlib import Path
from dotenv import load_dotenv
import pyairtable
from pyairtable.api import Api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_frame_airtable")

# Load environment variables directly
load_dotenv()
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME')

# Update field names to match actual Airtable structure
FRAME_ID_FIELD = 'FrameID'  # This field contains the full path to the frame
FRAME_NUMBER_FIELD = 'FrameNumber'
FOLDER_NAME_FIELD = 'FolderName'
FOLDER_PATH_FIELD = 'FolderPath'
TIMESTAMP_FIELD = 'Timestamp'

# Set test frame path directly
TEST_FRAME_PATH = "/home/jason/Videos/screenRecordings/screen_recording_2025_03_03_at_3_39_52_am/frame_000051.jpg"

def list_airtable_bases(api_key):
    """List available Airtable bases using REST API."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get("https://api.airtable.com/v0/meta/bases", headers=headers)
        response.raise_for_status()
        
        data = response.json()
        bases = data.get('bases', [])
        logger.info(f"Found {len(bases)} Airtable bases:")
        for base in bases:
            logger.info(f"  Base ID: {base.get('id')} - Name: {base.get('name')}")
        return bases
    except Exception as e:
        logger.error(f"Error listing Airtable bases: {str(e)}")
        return []

def list_airtable_tables(api_key, base_id):
    """List available tables in a base using REST API."""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"https://api.airtable.com/v0/meta/bases/{base_id}/tables", headers=headers)
        response.raise_for_status()
        
        data = response.json()
        tables = data.get('tables', [])
        logger.info(f"Found {len(tables)} tables in base {base_id}:")
        for table in tables:
            logger.info(f"  Table ID: {table.get('id')} - Name: {table.get('name')}")
            # Also display fields to help with mapping
            fields = table.get('fields', [])
            logger.info(f"    Fields: {', '.join([f.get('name') for f in fields[:10]])}")
            if len(fields) > 10:
                logger.info(f"    ... and {len(fields) - 10} more fields")
        return tables
    except Exception as e:
        logger.error(f"Error listing tables in base {base_id}: {str(e)}")
        return []

def find_airtable_record_by_filename(frame_path, base_id, table_name):
    """Find an Airtable record that matches the given frame filename."""
    # Extract filename and directory path
    frame_file = Path(frame_path)
    filename = frame_file.name
    dir_name = frame_file.parent.name
    full_path = str(frame_file)
    
    logger.info(f"Looking for Airtable record matching:")
    logger.info(f"  Filename: {filename}")
    logger.info(f"  Directory: {dir_name}")
    logger.info(f"  Full path: {full_path}")
    logger.info(f"  Using Airtable Base ID: {base_id}")
    logger.info(f"  Using Airtable Table: {table_name}")
    
    # Create Airtable client
    try:
        if not all([AIRTABLE_TOKEN, base_id, table_name]):
            raise ValueError("Missing required Airtable configuration")
        
        # Use the API approach
        api = Api(AIRTABLE_TOKEN)
        table = api.table(base_id, table_name)
        logger.info(f"Connected to Airtable table: {table_name} in base {base_id}")
        
        try:
            # First just try to get a single record to verify we can access the table
            try:
                first_record = table.first(max_records=1)
                if first_record:
                    logger.info(f"Successfully accessed table. Sample record: {first_record.get('id')}")
                    if 'fields' in first_record:
                        logger.info(f"Sample fields: {list(first_record['fields'].keys())}")
            except Exception as first_err:
                logger.error(f"Couldn't access first record: {str(first_err)}")
            
            # Try to get all records with relevant fields
            all_records = table.all(fields=[FRAME_ID_FIELD, FRAME_NUMBER_FIELD, FOLDER_NAME_FIELD, FOLDER_PATH_FIELD])
            logger.info(f"Successfully retrieved {len(all_records)} records from the table")
            
            # Method 1: Match by exact full path in FrameID field
            logger.info(f"Trying to match by full path in {FRAME_ID_FIELD}")
            for record in all_records:
                fields = record.get('fields', {})
                record_frame_id = fields.get(FRAME_ID_FIELD, '')
                if record_frame_id and full_path in record_frame_id:
                    logger.info("✅ Found match by full path!")
                    return record
            
            # Method 2: Match by just the filename part
            logger.info(f"Trying to match by filename in {FRAME_ID_FIELD}")
            for record in all_records:
                fields = record.get('fields', {})
                record_frame_id = fields.get(FRAME_ID_FIELD, '')
                if record_frame_id and filename in record_frame_id:
                    logger.info("✅ Found match by filename in FrameID!")
                    return record
            
            # Method 3: Try matching just the frame number
            if filename.startswith('frame_') and '.' in filename:
                try:
                    frame_num = int(filename.split('.')[0].split('_')[1])
                    logger.info(f"Trying match by frame number: {frame_num}")
                    
                    for record in all_records:
                        fields = record.get('fields', {})
                        record_frame_num = fields.get(FRAME_NUMBER_FIELD)
                        # Try both string and int comparison
                        if record_frame_num == frame_num or record_frame_num == str(frame_num):
                            logger.info("✅ Found match by frame number!")
                            return record
                except (IndexError, ValueError):
                    logger.warning("Couldn't extract frame number from filename")
            
            # Method 4: Try matching on directory name
            logger.info(f"Trying match by directory name: {dir_name}")
            for record in all_records:
                fields = record.get('fields', {})
                if dir_name == fields.get(FOLDER_NAME_FIELD):
                    logger.info("✅ Found match by folder name!")
                    return record
            
            logger.warning("❌ No matching record found in Airtable")
            return None
            
        except Exception as record_err:
            logger.error(f"Error retrieving records: {str(record_err)}")
            return None
        
    except Exception as e:
        logger.error(f"Error searching Airtable: {str(e)}")
        return None

def test_frame_airtable_match(base_id=None, table_name=None):
    """Test finding Airtable metadata for a frame file."""
    # Use provided values or fall back to environment variables
    base_id = base_id or AIRTABLE_BASE_ID
    table_name = table_name or AIRTABLE_TABLE_NAME
    
    logger.info(f"Testing frame-to-Airtable matching for: {TEST_FRAME_PATH}")
    logger.info(f"Airtable Personal Access Token: {AIRTABLE_TOKEN[:4]}...{AIRTABLE_TOKEN[-4:]}")
    logger.info(f"Base ID from env: {AIRTABLE_BASE_ID}")
    logger.info(f"Table name from env: {AIRTABLE_TABLE_NAME}")
    
    # Check if file exists
    frame_path = Path(TEST_FRAME_PATH)
    if not frame_path.exists():
        logger.error(f"Frame file not found: {TEST_FRAME_PATH}")
        return False
    
    try:
        # Load the image
        logger.info("Loading image...")
        img = Image.open(frame_path)
        
        # Display basic frame info
        logger.info(f"Frame loaded successfully!")
        logger.info(f"  Size: {img.size}")
        logger.info(f"  Format: {img.format}")
        
        # For debugging: list available bases and tables
        logger.info("Listing available Airtable bases for debugging...")
        bases = list_airtable_bases(AIRTABLE_TOKEN)
        
        if bases:
            logger.info(f"Found {len(bases)} bases. Try using one of these IDs.")
            # Try the first base if no base_id is specified
            if not base_id and bases:
                base_id = bases[0].get('id')
                logger.info(f"No base ID specified, using first available base: {base_id}")
            
            if base_id:
                logger.info(f"Listing tables in base {base_id}...")
                tables = list_airtable_tables(AIRTABLE_TOKEN, base_id)
                
                # Try the first table if no table_name is specified
                if not table_name and tables:
                    table_name = tables[0].get('name')
                    logger.info(f"No table name specified, using first available table: {table_name}")
        
        # Find matching Airtable record
        if base_id and table_name:
            logger.info("Searching for matching Airtable record...")
            record = find_airtable_record_by_filename(TEST_FRAME_PATH, base_id, table_name)
            
            if record:
                # Display found metadata
                fields = record.get('fields', {})
                logger.info("Found matching Airtable record:")
                logger.info(f"  Record ID: {record.get('id')}")
                logger.info(f"  Fields: {list(fields.keys())}")
                
                # Display specific important fields
                if FOLDER_NAME_FIELD in fields:
                    logger.info(f"  {FOLDER_NAME_FIELD}: {fields.get(FOLDER_NAME_FIELD)}")
                if FRAME_NUMBER_FIELD in fields:
                    logger.info(f"  {FRAME_NUMBER_FIELD}: {fields.get(FRAME_NUMBER_FIELD)}")
                if FRAME_ID_FIELD in fields:
                    logger.info(f"  {FRAME_ID_FIELD}: {fields.get(FRAME_ID_FIELD)}")
                
                return True
            else:
                logger.error("No matching Airtable record found.")
                return False
        else:
            logger.error("No valid Airtable base or table specified after exploration.")
            return False
            
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test frame to Airtable matching')
    parser.add_argument('--base', help='Airtable Base ID (overrides env variable)')
    parser.add_argument('--table', help='Airtable Table name (overrides env variable)')
    args = parser.parse_args()
    
    if not AIRTABLE_TOKEN:
        logger.error("AIRTABLE_PERSONAL_ACCESS_TOKEN not set in environment variables.")
        sys.exit(1)
    
    success = test_frame_airtable_match(base_id=args.base, table_name=args.table)
    if success:
        logger.info("✅ Test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Test failed")
        sys.exit(1) 