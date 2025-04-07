"""
Test script to verify Airtable API connection.
"""

import os
import sys
from dotenv import load_dotenv
from src.integrations.airtable import AirtableClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_airtable")

# Load environment variables
load_dotenv()

def test_connection():
    """Test connection to Airtable API."""
    try:
        # Get Airtable configuration
        api_key = os.getenv('AIRTABLE_API_KEY')
        base_id = os.getenv('AIRTABLE_BASE_ID')
        table_name = os.getenv('AIRTABLE_TABLE_NAME', 'Frames')
        
        if not api_key or not base_id:
            logger.error("Airtable API key or base ID is missing in .env file")
            return False
            
        logger.info(f"Using Airtable configuration: base_id={base_id}, table={table_name}")
        
        # Initialize the Airtable client
        logger.info("Initializing Airtable client...")
        airtable_client = AirtableClient()
        
        # Fetch a sample of records to test connection
        logger.info("Fetching records to test connection...")
        records = airtable_client.get_records(max_records=5)
        
        # Print record information
        logger.info(f"Successfully retrieved {len(records)} records:")
        for i, record in enumerate(records, 1):
            record_id = record.get('id', 'Unknown ID')
            fields = record.get('fields', {})
            drive_file_id_field = os.getenv('DRIVE_FILE_ID_FIELD', 'DriveFileID')
            
            logger.info(f"  {i}. Record ID: {record_id}")
            logger.info(f"     Drive File ID: {fields.get(drive_file_id_field, 'N/A')}")
            logger.info(f"     Fields: {', '.join(fields.keys())}")
            
        logger.info("Airtable connection test successful!")
        return True
        
    except Exception as e:
        logger.error(f"Error testing Airtable connection: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Airtable connection...")
    success = test_connection()
    
    if success:
        print("✅ Connection successful! Your Airtable configuration is working.")
        sys.exit(0)
    else:
        print("❌ Connection failed. Please check the logs for details.")
        sys.exit(1) 