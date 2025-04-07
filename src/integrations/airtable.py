"""
Airtable client for accessing and manipulating frame data.
Handles API communication, record retrieval, and updates.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
import time
from pathlib import Path
import re

from pyairtable import Api, Table, Base
from pyairtable.formulas import match
from dotenv import load_dotenv

# Import application settings
from src.config.settings import (
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID,
    AIRTABLE_TABLE_NAME,
    DRIVE_FILE_ID_FIELD,
    FRAME_NUMBER_FIELD,
    VIDEO_ID_FIELD,
    TIMESTAMP_FIELD,
    TITLE_FIELD,
    PROCESSED_FIELD,
    ConfigError
)

# Get a logger for this module
logger = logging.getLogger("logicLoom.integrations.airtable")

# Load environment variables
load_dotenv()

class AirtableClient:
    """Client for interacting with Airtable API."""
    
    def __init__(self, api_key: Optional[str] = None, base_id: Optional[str] = None, table_name: Optional[str] = None):
        """
        Initialize the Airtable client.
        
        Args:
            api_key: Airtable API key. If None, will use AIRTABLE_API_KEY environment variable.
            base_id: Airtable base ID. If None, will use AIRTABLE_BASE_ID environment variable.
            table_name: Airtable table name. If None, will use AIRTABLE_TABLE_NAME environment variable.
        """
        try:
            # Get API key
            self.api_key = api_key or os.environ.get('AIRTABLE_API_KEY')
            if not self.api_key:
                raise ValueError("Airtable API key not provided and AIRTABLE_API_KEY environment variable not set")
                
            # Get base ID
            self.base_id = base_id or os.environ.get('AIRTABLE_BASE_ID')
            if not self.base_id:
                raise ValueError("Airtable base ID not provided and AIRTABLE_BASE_ID environment variable not set")
                
            # Get table name
            self.table_name = table_name or os.environ.get('AIRTABLE_TABLE_NAME', 'Frames')
            
            # Initialize Airtable API
            self.api = Api(self.api_key)
            self.base = Base(self.api, self.base_id)
            self.table = Table(self.api, self.base_id, self.table_name)
            
            logger.info(f"Airtable client initialized for table '{self.table_name}'")
            
        except Exception as e:
            logger.error(f"Error initializing Airtable client: {str(e)}")
            raise
    
    def get_frame_metadata_batch(self, batch_size: Optional[int] = None, 
                                processed_field: str = 'Processed',
                                processed_value: bool = False,
                                max_batches: Optional[int] = 1) -> List[Dict[str, Any]]:
        """
        Get a batch of frame metadata records from Airtable.
        
        Args:
            batch_size: Number of records to retrieve per batch. If None, will use max available.
            processed_field: Field name that tracks whether a frame has been processed.
            processed_value: Value to filter by (True = processed, False = unprocessed).
            max_batches: Maximum number of batches to retrieve. If None, will get all available records.
            
        Returns:
            List of records (each a dictionary with 'id', 'fields', and other metadata)
        """
        try:
            formula = f"{{{processed_field}}} = {str(processed_value).lower()}"
            logger.info(f"Fetching frames with filter: {formula}")
            
            # Set up query parameters
            params = {
                'formula': formula,
                'sort': [{'field': 'FolderName', 'direction': 'asc'}]
            }
            
            if batch_size:
                params['max_records'] = batch_size if max_batches == 1 else batch_size * max_batches
            
            # Fetch records
            records = self.table.all(**params)
            
            # If max_batches is specified, limit the number of records
            if batch_size and max_batches is not None and max_batches > 0:
                records = records[:batch_size * max_batches]
            
            logger.info(f"Retrieved {len(records)} frame records from Airtable")
            return records
        except Exception as e:
            logger.error(f"Error fetching frame metadata batch: {str(e)}")
            raise
    
    def mark_record_as_processed(self, record_id: str, processed_field: str = 'Processed') -> bool:
        """
        Mark a record as processed in Airtable.
        
        Args:
            record_id: ID of the record to update
            processed_field: Field name to mark as processed
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update the record
            self.table.update(record_id, {processed_field: True})
            logger.info(f"Marked record {record_id} as processed")
            return True
        except Exception as e:
            logger.error(f"Error marking record {record_id} as processed: {str(e)}")
            return False
    
    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single record by ID.
        
        Args:
            record_id: ID of the record to retrieve
            
        Returns:
            Record dictionary if found, None otherwise
        """
        try:
            record = self.table.get(record_id)
            return record
        except Exception as e:
            logger.error(f"Error retrieving record {record_id}: {str(e)}")
            return None
    
    def create_record(self, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new record in Airtable.
        
        Args:
            fields: Dictionary of field values to set
            
        Returns:
            The created record dictionary if successful, None otherwise
        """
        try:
            new_record = self.table.create(fields)
            logger.info(f"Created new record with ID {new_record['id']}")
            return new_record
        except Exception as e:
            logger.error(f"Error creating Airtable record: {str(e)}")
            return None
    
    def update_record(self, record_id: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing record in Airtable.
        
        Args:
            record_id: ID of the record to update
            fields: Dictionary of field values to update
            
        Returns:
            The updated record dictionary if successful, None otherwise
        """
        try:
            updated_record = self.table.update(record_id, fields)
            logger.info(f"Updated record {record_id}")
            return updated_record
        except Exception as e:
            logger.error(f"Error updating record {record_id}: {str(e)}")
            return None
    
    def batch_update_records(self, updates: List[Dict[str, Any]]) -> bool:
        """
        Update multiple records in a single batch operation.
        
        Args:
            updates: List of dictionaries with 'id' and 'fields' keys
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to the expected format for batch updates
            formatted_updates = []
            for update in updates:
                formatted_updates.append({
                    'id': update['id'],
                    'fields': update['fields']
                })
            
            # Execute batch update
            result = self.table.batch_update(formatted_updates)
            logger.info(f"Batch updated {len(result)} records")
            return True
        except Exception as e:
            logger.error(f"Error in batch update: {str(e)}")
            return False
    
    def search_records(self, formula: str) -> List[Dict[str, Any]]:
        """
        Search for records using an Airtable formula.
        
        Args:
            formula: Airtable formula for filtering records
            
        Returns:
            List of matching records
        """
        try:
            records = self.table.all(formula=formula)
            logger.info(f"Found {len(records)} records matching formula: {formula}")
            return records
        except Exception as e:
            logger.error(f"Error searching records with formula {formula}: {str(e)}")
            raise

    def extract_frame_metadata(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract standardized frame metadata from an Airtable record.
        Maps Airtable field names to standard internal field names.
        
        Args:
            record: Airtable record dictionary
            
        Returns:
            Standardized metadata dictionary
        """
        fields = record.get('fields', {})
        
        # Map Airtable field names to standard internal field names
        metadata = {
            'record_id': record.get('id'),
            'drive_file_id': fields.get(DRIVE_FILE_ID_FIELD),
            'frame_number': fields.get(FRAME_NUMBER_FIELD),
            'video_id': fields.get(VIDEO_ID_FIELD),
            'timestamp': fields.get(TIMESTAMP_FIELD),
            'title': fields.get(TITLE_FIELD),
        }
        
        # Add all other fields as extras
        for field_name, field_value in fields.items():
            if field_name not in {DRIVE_FILE_ID_FIELD, FRAME_NUMBER_FIELD, VIDEO_ID_FIELD, 
                                  TIMESTAMP_FIELD, TITLE_FIELD, PROCESSED_FIELD}:
                metadata[field_name] = field_value
        
        return metadata 

    def find_record_by_relative_path(self, relative_frame_path: str) -> Optional[Dict[str, Any]]:
        """
        Finds an Airtable record matching a given relative file path.

        Args:
            relative_frame_path: The relative path of the frame file 
                                (e.g., 'FolderName/frame_001.png'), expected
                                to potentially match a value in Airtable.

        Returns:
            The matching Airtable record dictionary, or None if not found or ambiguous.
        """
        if not relative_frame_path:
            logger.warning("Relative frame path provided to find_record_by_relative_path cannot be empty.")
            return None

        # --- Strategy 1: Direct match on FRAME_FILENAME_FIELD --- 
        # Assumes a field exists in Airtable storing this exact relative path.
        if FRAME_FILENAME_FIELD:
            formula_direct = match({FRAME_FILENAME_FIELD: relative_frame_path})
            logger.debug(f"Attempting to find Airtable record using direct formula: {formula_direct}")
            try:
                records_direct = self.search_records(formula=formula_direct)
                if len(records_direct) == 1:
                    logger.info(f"Found unique Airtable record {records_direct[0]['id']} matching path '{relative_frame_path}' directly via field '{FRAME_FILENAME_FIELD}'.")
                    return records_direct[0]
                elif len(records_direct) > 1:
                    logger.warning(f"Found multiple ({len(records_direct)}) Airtable records matching path '{relative_frame_path}' directly via field '{FRAME_FILENAME_FIELD}'. Returning None due to ambiguity.")
                    return None
                # If 0 records found with direct match, log and proceed to strategy 2
                logger.debug(f"Direct path match failed for '{relative_frame_path}' using field '{FRAME_FILENAME_FIELD}'.")
            except Exception as e:
                 logger.error(f"Error searching Airtable with direct formula '{formula_direct}': {e}", exc_info=True)
                 # Don't return yet, try strategy 2
        else:
             logger.debug(f"FRAME_FILENAME_FIELD not configured, skipping direct path match.")

        # --- Strategy 2: Match FolderName (TITLE_FIELD) and FrameNumber (FRAME_NUMBER_FIELD) --- 
        logger.debug(f"Attempting FolderName/FrameNumber match for '{relative_frame_path}'.")
        try:
            # Extract folder name and frame number from the path
            p = Path(relative_frame_path)
            # Handle potential empty parent if path is just a filename
            folder_name = p.parent.name if p.parent.name else None 
            base_filename = p.stem # e.g., 'frame_001'

            # Attempt to extract frame number (adjust regex for flexibility)
            frame_num_match = re.search(r'[_-](\d+)$', base_filename) # Look for _digits or -digits at the end
            frame_num = int(frame_num_match.group(1)) if frame_num_match else None

            if folder_name and frame_num is not None:
                 # Build formula using configured field names
                 # Note: Ensure FrameNumber is stored as a number in Airtable for this to work directly
                 formula_parts = f"AND({{'{TITLE_FIELD}'}}='{folder_name}', {{'{FRAME_NUMBER_FIELD}'}}={frame_num})"
                 logger.debug(f"Attempting to find Airtable record using formula: {formula_parts}")
                 
                 records_indirect = self.search_records(formula=formula_parts)

                 if len(records_indirect) == 1:
                     logger.info(f"Found unique Airtable record {records_indirect[0]['id']} matching {TITLE_FIELD}='{folder_name}', {FRAME_NUMBER_FIELD}={frame_num}.")
                     return records_indirect[0]
                 elif len(records_indirect) > 1:
                     logger.warning(f"Found multiple ({len(records_indirect)}) Airtable records matching {TITLE_FIELD}='{folder_name}', {FRAME_NUMBER_FIELD}={frame_num}. Returning None due to ambiguity.")
                     return None
                 else:
                     # Log only if the first strategy also failed
                     if not FRAME_FILENAME_FIELD: # Or if direct search yielded 0 results
                         logger.warning(f"Could not find any Airtable record matching {TITLE_FIELD}='{folder_name}', {FRAME_NUMBER_FIELD}={frame_num}.")
                     else:
                          logger.debug(f"Secondary match also failed for FolderName/FrameNumber for path '{relative_frame_path}'.")
                     return None # Strategy 2 failed
            else:
                 logger.warning(f"Could not reliably extract FolderName ('{folder_name}') or FrameNumber ('{frame_num}') from path '{relative_frame_path}' for secondary search.")
                 return None # Cannot perform secondary search

        except Exception as e:
            logger.error(f"Error searching Airtable with {TITLE_FIELD}/{FRAME_NUMBER_FIELD} formula for path '{relative_frame_path}': {e}", exc_info=True)
            return None

        # If both strategies failed or weren't applicable
        logger.warning(f"Could not find a unique Airtable record for relative path: {relative_frame_path} using available strategies.")
        return None 