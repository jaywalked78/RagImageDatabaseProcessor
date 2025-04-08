#!/usr/bin/env python3
"""
List Airtable records to help debug the matching issue.

This script fetches all records from Airtable and displays their folder paths
to help determine why frame matching is failing.
"""

import os
import sys
import json
import logging
import asyncio
import aiohttp
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('airtable_list')

# Load environment variables
load_dotenv()

# Airtable credentials
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_PERSONAL_ACCESS_TOKEN = os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "tblFrameAnalysis")

# Field names
FOLDER_PATH_FIELD = os.getenv("AIRTABLE_FOLDER_PATH_FIELD", "FolderPath")

async def list_airtable_records():
    """Fetch and list all records from Airtable."""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_PERSONAL_ACCESS_TOKEN or AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    all_records = []
    offset = None
    
    logger.info(f"Connecting to Airtable - Base: {AIRTABLE_BASE_ID}, Table: {AIRTABLE_TABLE_NAME}")
    
    async with aiohttp.ClientSession() as session:
        while True:
            # Construct URL with optional offset
            url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
            if offset:
                url += f"?offset={offset}"
            
            logger.debug(f"Making request to: {url}")
            
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Error fetching records: {error_text}")
                        break
                    
                    data = await response.json()
                    
                    # Process records
                    records = data.get('records', [])
                    for record in records:
                        record_id = record.get('id')
                        fields = record.get('fields', {})
                        
                        # Get folder path if available
                        folder_path = fields.get(FOLDER_PATH_FIELD, "No path available")
                        
                        all_records.append({
                            'id': record_id,
                            'folder_path': folder_path,
                        })
                    
                    logger.info(f"Fetched {len(records)} records in this batch")
                    
                    # Check for pagination
                    offset = data.get('offset')
                    if not offset:
                        break
            
            except Exception as e:
                logger.error(f"Error making request: {str(e)}")
                break
    
    # Display summary
    logger.info(f"Total records found: {len(all_records)}")
    
    if all_records:
        logger.info("\nSample folder paths (first 10):")
        for i, record in enumerate(all_records[:10]):
            logger.info(f"{i+1}. {record['folder_path']}")
        
        # Check for our target folder
        target_folder = "screen_recording_2025_02_20_at_10_59_16_am"
        matching_records = [r for r in all_records if target_folder in r['folder_path']]
        
        if matching_records:
            logger.info(f"\nFound {len(matching_records)} records containing '{target_folder}':")
            for i, record in enumerate(matching_records):
                logger.info(f"{i+1}. {record['folder_path']}")
        else:
            logger.info(f"\nNo records found containing the target folder: {target_folder}")
    
    return all_records

async def main():
    """Main entry point."""
    try:
        records = await list_airtable_records()
        
        # Save to file for reference
        with open('airtable_records.json', 'w') as f:
            json.dump(records, f, indent=2)
        
        logger.info(f"Saved {len(records)} records to airtable_records.json")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main()) 