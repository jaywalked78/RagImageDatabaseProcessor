"""
Test script for the AirtableClient.find_record_by_relative_path method.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging (optional but helpful)
logging.basicConfig(level=logging.DEBUG, # Set to DEBUG to see detailed logs from the function
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_find_record")

# Load environment variables from .env file
load_dotenv()

# Attempt to import necessary components
try:
    from src.config.settings import TEST_FRAME_RELATIVE_PATH, TITLE_FIELD, FRAME_NUMBER_FIELD, FRAME_FILENAME_FIELD
    from src.integrations.airtable import AirtableClient
except ImportError as e:
    logger.error(f"Failed to import necessary modules: {e}")
    logger.error("Ensure your PYTHONPATH is set correctly or run this script from the project root.")
    sys.exit(1)

def run_test():
    """Runs the test to find an Airtable record by relative path."""
    logger.info("--- Starting Airtable Record Finder Test ---")
    
    # Check if the test path is configured
    if not TEST_FRAME_RELATIVE_PATH:
        logger.error("TEST_FRAME_RELATIVE_PATH is not set in your .env file.")
        logger.error("Please set it to a valid relative path corresponding to an entry in your Airtable.")
        return False
        
    logger.info(f"Attempting to find record for relative path: {TEST_FRAME_RELATIVE_PATH}")
    logger.info(f"Using configured fields: FRAME_FILENAME_FIELD='{FRAME_FILENAME_FIELD}', TITLE_FIELD='{TITLE_FIELD}', FRAME_NUMBER_FIELD='{FRAME_NUMBER_FIELD}'")
    
    try:
        # Initialize the Airtable client
        airtable_client = AirtableClient()
        logger.info("AirtableClient initialized.")
        
        # Call the function to test
        found_record = airtable_client.find_record_by_relative_path(TEST_FRAME_RELATIVE_PATH)
        
        if found_record:
            logger.info("✅ Successfully found a unique record!")
            record_id = found_record.get('id')
            fields = found_record.get('fields', {})
            logger.info(f"  Record ID: {record_id}")
            # Print some key fields for verification
            logger.info(f"  Fields found: {list(fields.keys())}")
            logger.info(f"  Field '{TITLE_FIELD}' (FolderName): {fields.get(TITLE_FIELD)}")
            logger.info(f"  Field '{FRAME_NUMBER_FIELD}': {fields.get(FRAME_NUMBER_FIELD)}")
            if FRAME_FILENAME_FIELD:
                 logger.info(f"  Field '{FRAME_FILENAME_FIELD}': {fields.get(FRAME_FILENAME_FIELD)}")
            return True
        else:
            logger.warning("❌ Failed to find a unique record for the specified path.")
            logger.warning("Check logs above for details on which matching strategies were attempted.")
            logger.warning("Verify that the TEST_FRAME_RELATIVE_PATH in your .env file exists in Airtable and matches naming conventions.")
            return False
            
    except ValueError as ve:
         logger.error(f"Configuration Error: {ve}")
         logger.error("Please ensure AIRTABLE_PERSONAL_ACCESS_TOKEN and AIRTABLE_BASE_ID are correctly set in your .env file.")
         return False
    except ImportError as ie:
         # Catch potential issues with pyairtable if not installed correctly
         logger.error(f"Import Error: {ie}. Is pyairtable installed correctly?")
         return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during the test: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = run_test()
    logger.info("--- Test Finished ---")
    sys.exit(0 if success else 1) 