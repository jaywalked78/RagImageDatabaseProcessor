"""
Airtable integration for TheLogicLoom application.
Handles fetching and manipulating data from Airtable.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
import time

import backoff
from pyairtable import Api, Base, Table
from pyairtable.formulas import match
from tenacity import retry, stop_after_attempt, wait_exponential

# Get a logger for this module
logger = logging.getLogger("logicLoom")

# Airtable configuration from environment variables
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'Frames')  # Default to 'Frames'


class AirtableClient:
    """Client for Airtable operations."""
    
    def __init__(self, api_key: Optional[str] = None, base_id: Optional[str] = None, 
                 table_name: Optional[str] = None):
        """
        Initialize the Airtable client.
        
        Args:
            api_key: Airtable API key (defaults to AIRTABLE_API_KEY env var)
            base_id: Airtable base ID (defaults to AIRTABLE_BASE_ID env var)
            table_name: Airtable table name (defaults to AIRTABLE_TABLE_NAME env var)
        """
        try:
            self.api_key = api_key or AIRTABLE_API_KEY
            self.base_id = base_id or AIRTABLE_BASE_ID
            self.table_name = table_name or AIRTABLE_TABLE_NAME
            
            if not self.api_key:
                logger.error("Airtable API key not provided")
                raise ValueError("Airtable API key is required. Set AIRTABLE_API_KEY env var or pass to constructor.")
            
            if not self.base_id:
                logger.error("Airtable base ID not provided")
                raise ValueError("Airtable base ID is required. Set AIRTABLE_BASE_ID env var or pass to constructor.")
            
            self.api = Api(self.api_key)
            self.base = Base(self.api, self.base_id)
            self.table = Table(self.api, self.base_id, self.table_name)
            
            logger.info(f"Airtable client initialized for base {self.base_id}, table {self.table_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Airtable client: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def get_records(self, formula: Optional[str] = None, 
                    fields: Optional[List[str]] = None, 
                    max_records: Optional[int] = None, 
                    page_size: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve records from Airtable with optional filtering.
        
        Args:
            formula: Optional Airtable formula for filtering
            fields: Optional list of field names to include
            max_records: Optional maximum number of records to return
            page_size: Page size for pagination (default: 100)
            
        Returns:
            List of record dictionaries with 'id' and 'fields' keys
        """
        try:
            # Use pyairtable's pagination
            records = self.table.all(
                formula=formula,
                fields=fields,
                max_records=max_records,
                page_size=page_size
            )
            
            logger.info(f"Retrieved {len(records)} records from Airtable")
            return records
        except Exception as e:
            logger.error(f"Error retrieving records from Airtable: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def get_record_by_id(self, record_id: str) -> Dict[str, Any]:
        """
        Retrieve a single record by its ID.
        
        Args:
            record_id: The Airtable record ID
            
        Returns:
            Record dictionary with 'id' and 'fields' keys
        """
        try:
            record = self.table.get(record_id)
            logger.debug(f"Retrieved record with ID: {record_id}")
            return record
        except Exception as e:
            logger.error(f"Error retrieving record with ID {record_id}: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def query_records(self, field_name: str, field_value: Union[str, int, bool, float]) -> List[Dict[str, Any]]:
        """
        Query records where a field equals a specific value.
        
        Args:
            field_name: The name of the field to query
            field_value: The value to match
            
        Returns:
            List of matching record dictionaries
        """
        try:
            formula = match({field_name: field_value})
            records = self.table.all(formula=formula)
            
            logger.info(f"Found {len(records)} records where {field_name} = {field_value}")
            return records
        except Exception as e:
            logger.error(f"Error querying records where {field_name} = {field_value}: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def update_record(self, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a record by its ID.
        
        Args:
            record_id: The Airtable record ID
            fields: Dictionary of field names to values to update
            
        Returns:
            Updated record dictionary
        """
        try:
            updated_record = self.table.update(record_id, fields)
            logger.info(f"Updated record with ID: {record_id}")
            return updated_record
        except Exception as e:
            logger.error(f"Error updating record with ID {record_id}: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    def get_frame_metadata_batch(self, batch_size: int = 100, 
                                 processed_field: str = 'Processed',
                                 processed_value: bool = False,
                                 max_batches: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get a batch of unprocessed frame metadata.
        
        Args:
            batch_size: Number of records to retrieve per batch
            processed_field: Field name that indicates if the frame has been processed
            processed_value: Value to filter the processed_field by (typically False for unprocessed)
            max_batches: Maximum number of batches to process (None for all)
            
        Returns:
            List of frame metadata records
        """
        try:
            formula = match({processed_field: processed_value})
            
            all_records = []
            batch_count = 0
            offset = None
            
            while True:
                # Get batch of records
                batch = self.table.all(
                    formula=formula,
                    page_size=batch_size,
                    offset=offset
                )
                
                if not batch:
                    break
                    
                all_records.extend(batch)
                batch_count += 1
                
                logger.info(f"Retrieved batch {batch_count} with {len(batch)} records")
                
                # Check if we've reached the max_batches limit
                if max_batches and batch_count >= max_batches:
                    logger.info(f"Reached maximum batch limit of {max_batches}")
                    break
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.2)
                
                # Check if there are more records
                if len(batch) < batch_size:
                    break
            
            logger.info(f"Retrieved a total of {len(all_records)} unprocessed frame records")
            return all_records
            
        except Exception as e:
            logger.error(f"Error retrieving frame metadata batch: {str(e)}")
            raise 