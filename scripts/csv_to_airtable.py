#!/usr/bin/env python
"""
CSV to Airtable Sync Script

This script reads data from processed_frames.csv and updates Airtable with information
about frames that have been flagged as containing API keys or other sensitive information.

Usage:
  python csv_to_airtable.py [options]

Options:
  --csv-file FILE       CSV file with processed frames data (default: processed_frames.csv)
  --base-id ID          Airtable base ID (required)
  --table-name NAME     Airtable table name (required)
  --api-key KEY         Airtable API key (required)
  --dry-run             Don't update Airtable, just show what would be updated
  --frame-id-field      Name of the field in Airtable that contains the frame ID (default: "FrameID")
  --flagged-field       Name of the field in Airtable to store flagged status (default: "Flagged")
  --ocr-data-field      Name of the field in Airtable to store OCR data (default: "OCRData")
"""

import os
import csv
import argparse
import time
import json
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("output/logs/csv_to_airtable.log")
    ]
)
logger = logging.getLogger(__name__)

# Try importing Airtable API library
try:
    from pyairtable import Api, Base, Table
    AIRTABLE_AVAILABLE = True
except ImportError:
    AIRTABLE_AVAILABLE = False
    print("Error: pyairtable package not found. This script requires the pyairtable package.")
    print("Install with: pip install pyairtable")
    sys.exit(1)

# Airtable rate limiting constants
AIRTABLE_RATE_LIMIT_SLEEP = 0.25  # Sleep 250ms between requests (allows ~4 req/sec)

class CSVToAirtableSync:
    """Class to sync CSV data to Airtable"""
    
    def __init__(self, options):
        self.options = options
        self.csv_file = Path(options.csv_file)
        self.last_airtable_request_time = 0
        self.updated_count = 0
        self.flagged_count = 0
        self.error_count = 0
        
        # Initialize Airtable connection
        try:
            self.airtable = Table(options.api_key, options.base_id, options.table_name)
            logger.info(f"Connected to Airtable: {options.base_id}/{options.table_name}")
            logger.info(f"Airtable rate limiting enabled: {AIRTABLE_RATE_LIMIT_SLEEP}s between requests")
        except Exception as e:
            logger.error(f"Failed to connect to Airtable: {e}")
            sys.exit(1)
    
    def find_airtable_record_by_frame_id(self, frame_id):
        """Find Airtable record ID by frame ID"""
        try:
            # Apply rate limiting
            current_time = time.time()
            time_since_last_request = current_time - self.last_airtable_request_time
            
            if time_since_last_request < AIRTABLE_RATE_LIMIT_SLEEP:
                sleep_time = AIRTABLE_RATE_LIMIT_SLEEP - time_since_last_request
                logger.debug(f"Rate limiting: Sleeping for {sleep_time:.3f}s")
                time.sleep(sleep_time)
            
            # Query Airtable for the record
            formula = f"{{{self.options.frame_id_field}}}='{frame_id}'"
            records = self.airtable.all(formula=formula)
            self.last_airtable_request_time = time.time()
            
            if records:
                return records[0]["id"]
            return None
        except Exception as e:
            logger.error(f"Error searching for record with frame_id {frame_id}: {e}")
            return None
    
    def update_airtable_record(self, record_id, data):
        """Update a single Airtable record"""
        if self.options.dry_run:
            logger.info(f"DRY RUN: Would update Airtable record {record_id} with data:")
            for key, value in data.items():
                logger.info(f"  {key}: {value}")
            return True
        
        # Apply rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_airtable_request_time
        
        if time_since_last_request < AIRTABLE_RATE_LIMIT_SLEEP:
            sleep_time = AIRTABLE_RATE_LIMIT_SLEEP - time_since_last_request
            logger.debug(f"Rate limiting: Sleeping for {sleep_time:.3f}s")
            time.sleep(sleep_time)
        
        try:
            self.airtable.update(record_id, data)
            self.last_airtable_request_time = time.time()
            logger.info(f"Updated Airtable record {record_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update Airtable record {record_id}: {e}")
            self.error_count += 1
            return False
    
    def load_ocr_data(self, frame_id):
        """Load OCR data from the structured JSON file"""
        try:
            # Check if structured JSON exists
            json_file = Path(self.options.ocr_dir) / f"{frame_id}_structured.json"
            if not json_file.exists():
                logger.warning(f"No structured OCR data found for frame {frame_id}: {json_file}")
                return None
                
            # Load the JSON data
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            return data
        except Exception as e:
            logger.error(f"Error loading OCR data for frame {frame_id}: {e}")
            return None
    
    def format_ocr_for_airtable(self, ocr_data):
        """Format OCR data for Airtable"""
        if not ocr_data:
            return "No OCR data available"
            
        formatted_parts = []
        
        # Add summary if available
        if "summary" in ocr_data and ocr_data["summary"]:
            formatted_parts.append("Summary:\n" + ocr_data["summary"])
            
        # Add topics if available
        if "topics" in ocr_data and ocr_data["topics"]:
            formatted_parts.append("Topics:\n" + ", ".join(ocr_data["topics"]))
        
        # Add URLs if found
        if ocr_data.get("urls"):
            formatted_parts.append("URLs:\n" + "\n".join(ocr_data["urls"]))
        
        # Add detected API keys if any
        if ocr_data.get("detected_api_keys"):
            formatted_parts.append("⚠️ DETECTED API KEYS ⚠️\n" + "\n".join(ocr_data["detected_api_keys"]))
        
        # Add sensitivity explanation if flagged
        if ocr_data.get("is_flagged") and ocr_data.get("sensitive_explanation"):
            formatted_parts.append("⚠️ SENSITIVE CONTENT ALERT ⚠️\n" + ocr_data["sensitive_explanation"])
        
        # Join all parts with separators
        return "\n\n---\n\n".join(formatted_parts)
    
    def process_csv(self):
        """Process the CSV file and update Airtable with flagged frames"""
        if not self.csv_file.exists():
            logger.error(f"CSV file not found: {self.csv_file}")
            return False
            
        logger.info(f"Processing CSV file: {self.csv_file}")
        
        # Read CSV file
        try:
            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                
                # Check required columns
                required_columns = ['frame_id', 'flagged']
                for col in required_columns:
                    if col not in reader.fieldnames:
                        logger.error(f"Required column '{col}' not found in CSV. Available columns: {reader.fieldnames}")
                        return False
                
                # Process each row
                for row in reader:
                    frame_id = row.get('frame_id')
                    flagged = row.get('flagged') == '1'
                    
                    if not frame_id:
                        continue
                        
                    # Skip non-flagged frames if specified
                    if self.options.flagged_only and not flagged:
                        continue
                    
                    logger.info(f"Processing frame {frame_id} (flagged: {flagged})")
                    
                    # Find record in Airtable
                    record_id = self.find_airtable_record_by_frame_id(frame_id)
                    if not record_id:
                        logger.warning(f"No Airtable record found for frame {frame_id}")
                        continue
                    
                    # Load OCR data if available
                    ocr_data = None
                    if self.options.include_ocr_data:
                        ocr_data = self.load_ocr_data(frame_id)
                    
                    # Prepare data for Airtable
                    airtable_data = {
                        self.options.flagged_field: flagged
                    }
                    
                    # Add OCR data if available
                    if ocr_data and self.options.include_ocr_data:
                        airtable_data[self.options.ocr_data_field] = self.format_ocr_for_airtable(ocr_data)
                    
                    # Add timestamp fields
                    if self.options.sync_timestamp_field:
                        airtable_data[self.options.sync_timestamp_field] = datetime.now().isoformat()
                    
                    # Update Airtable
                    if self.update_airtable_record(record_id, airtable_data):
                        self.updated_count += 1
                        if flagged:
                            self.flagged_count += 1
                    
                    # Sleep briefly to prevent hitting API limits
                    time.sleep(0.1)
        
        except Exception as e:
            logger.error(f"Error processing CSV: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Report results
        logger.info("\nSync Results:")
        logger.info(f"Total records updated: {self.updated_count}")
        logger.info(f"Flagged frames: {self.flagged_count}")
        logger.info(f"Errors: {self.error_count}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Sync CSV data to Airtable')
    
    parser.add_argument('--csv-file', default='processed_frames.csv',
                       help='CSV file with processed frames data')
    parser.add_argument('--ocr-dir', default='ocr_results',
                       help='Directory containing OCR structured JSON files')
    parser.add_argument('--base-id', required=True,
                       help='Airtable base ID')
    parser.add_argument('--table-name', required=True,
                       help='Airtable table name')
    parser.add_argument('--api-key', required=True,
                       help='Airtable API key')
    parser.add_argument('--dry-run', action='store_true',
                       help="Don't update Airtable, just show what would be updated")
    parser.add_argument('--flagged-only', action='store_true',
                       help='Only update records for flagged frames')
    parser.add_argument('--include-ocr-data', action='store_true',
                       help='Include OCR data in Airtable updates')
    
    # Field name options
    parser.add_argument('--frame-id-field', default='FrameID',
                       help='Name of the field in Airtable that contains the frame ID')
    parser.add_argument('--flagged-field', default='Flagged',
                       help='Name of the field in Airtable to store flagged status')
    parser.add_argument('--ocr-data-field', default='OCRData',
                       help='Name of the field in Airtable to store OCR data')
    parser.add_argument('--sync-timestamp-field', default='LastSynced',
                       help='Name of the field in Airtable to store sync timestamp')
    
    args = parser.parse_args()
    
    if not AIRTABLE_AVAILABLE:
        logger.error("pyairtable package is required")
        return 1
        
    syncer = CSVToAirtableSync(args)
    if syncer.process_csv():
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main()) 