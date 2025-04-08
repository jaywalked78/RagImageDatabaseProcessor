#!/usr/bin/env python3
"""
Module for handling interactions with Airtable API.
Provides functionality to find frame metadata and records.
"""

import os
import logging
import re
import sys
import json
import time
import requests
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from pyairtable import Api
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', 'tblFrameAnalysis')
FRAME_BASE_DIR = os.environ.get('FRAME_BASE_DIR', '/home/jason/Videos/screenRecordings')

class AirtableConnector:
    """Base class for interacting with Airtable API."""
    
    def __init__(self, api_key: Optional[str] = None, base_id: Optional[str] = None, table_name: Optional[str] = None):
        """
        Initialize the Airtable connector.
        
        Args:
            api_key: Airtable API key (defaults to env var AIRTABLE_PERSONAL_ACCESS_TOKEN)
            base_id: Airtable base ID (defaults to env var AIRTABLE_BASE_ID)
            table_name: Airtable table name (defaults to env var AIRTABLE_TABLE_NAME)
        """
        self.api_key = api_key or AIRTABLE_TOKEN
        self.base_id = base_id or AIRTABLE_BASE_ID
        self.table_name = table_name or AIRTABLE_TABLE_NAME
        
        if not self.api_key:
            raise ValueError("No Airtable API key provided. Set AIRTABLE_PERSONAL_ACCESS_TOKEN environment variable.")
        if not self.base_id:
            raise ValueError("No Airtable Base ID provided. Set AIRTABLE_BASE_ID environment variable.")
        if not self.table_name:
            raise ValueError("No Airtable Table Name provided. Set AIRTABLE_TABLE_NAME environment variable.")
        
        # Initialize Airtable API client
        self.api = Api(self.api_key)
        self.table = self.api.table(self.base_id, self.table_name)
        
        logger.info(f"Initialized Airtable connector for table {self.table_name} in base {self.base_id}")

    def get_all_records(self, filter_by_formula: Optional[str] = None, sort: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, Any]]:
        """
        Get all records from the Airtable table with optional filtering and sorting.
        
        Args:
            filter_by_formula: Airtable formula for filtering records
            sort: List of sort specifications
            
        Returns:
            List of Airtable records
        """
        try:
            kwargs = {}
            if filter_by_formula:
                kwargs['formula'] = filter_by_formula
            if sort:
                kwargs['sort'] = sort
                
            return self.table.all(**kwargs)
        except Exception as e:
            logger.error(f"Error fetching records from Airtable: {e}")
            return []
    
    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single record by its ID.
        
        Args:
            record_id: Airtable record ID
            
        Returns:
            The record if found, None otherwise
        """
        try:
            return self.table.get(record_id)
        except Exception as e:
            logger.error(f"Error fetching record {record_id} from Airtable: {e}")
            return None
    
    def update_record(self, record_id: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a record with new fields.
        
        Args:
            record_id: Airtable record ID
            fields: Dictionary of fields to update
            
        Returns:
            The updated record if successful, None otherwise
        """
        try:
            # Detailed logging of the update operation
            logger.info(f"AIRTABLE UPDATE: Record ID: {record_id}")
            logger.info(f"AIRTABLE UPDATE: Table: {self.table_name} in Base: {self.base_id}")
            logger.info(f"AIRTABLE UPDATE: Fields being updated: {', '.join(fields.keys())}")
            
            # Log sensitive fields with values
            for field_name, field_value in fields.items():
                if field_name in ['Flagged', 'OCRData', 'Summary', 'ActionsDetected', 'TechnicalDetails']:
                    if isinstance(field_value, str):
                        truncated_value = field_value[:100] + "..." if len(field_value) > 100 else field_value
                    else:
                        truncated_value = str(field_value)
                    logger.info(f"AIRTABLE UPDATE: {field_name} = {truncated_value}")
            
            result = self.table.update(record_id, fields)
            logger.info(f"AIRTABLE UPDATE: Successfully updated record {record_id}")
            return result
        except Exception as e:
            logger.error(f"Error updating record {record_id} in Airtable: {e}")
            return None
    
    def create_record(self, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new record with the provided fields.
        
        Args:
            fields: Dictionary of fields for the new record
            
        Returns:
            The created record if successful, None otherwise
        """
        try:
            # Detailed logging of record creation
            logger.info(f"AIRTABLE CREATE: Creating new record in table: {self.table_name}")
            logger.info(f"AIRTABLE CREATE: Base ID: {self.base_id}")
            logger.info(f"AIRTABLE CREATE: Fields being set: {', '.join(fields.keys())}")
            
            # Log specific field values with truncation for large text fields
            for field_name, field_value in fields.items():
                if field_name in ['Flagged', 'OCRData', 'Summary', 'ActionsDetected', 'TechnicalDetails']:
                    if isinstance(field_value, str):
                        truncated_value = field_value[:100] + "..." if len(field_value) > 100 else field_value
                    else:
                        truncated_value = str(field_value)
                    logger.info(f"AIRTABLE CREATE: {field_name} = {truncated_value}")
            
            # Create the record and log success
            result = self.table.create(fields)
            record_id = result.get('id', 'unknown')
            logger.info(f"AIRTABLE CREATE: Successfully created record with ID: {record_id}")
            return result
        except Exception as e:
            logger.error(f"Error creating record in Airtable: {e}")
            return None


class AirtableMetadataFinder(AirtableConnector):
    """
    Class for finding and updating metadata in Airtable.
    """
    
    def __init__(self, token: str, base_id: str, table_name: str):
        """
        Initialize the AirtableMetadataFinder.
        
        Args:
            token: Airtable personal access token
            base_id: Airtable base ID
            table_name: Airtable table name
        """
        super().__init__(token, base_id, table_name)
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.base_url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        self.rate_limit_sleep = float(os.environ.get('AIRTABLE_RATE_LIMIT_SLEEP', '0.25'))
        
        # Verify we have the necessary credentials
        if not token:
            logger.error("AIRTABLE_PERSONAL_ACCESS_TOKEN not set")
            raise ValueError("AIRTABLE_PERSONAL_ACCESS_TOKEN not set")
        if not base_id:
            logger.error("AIRTABLE_BASE_ID not set")
            raise ValueError("AIRTABLE_BASE_ID not set")
    
    def extract_frame_number(self, frame_filename: str) -> Optional[int]:
        """
        Extract frame number from a filename.
        
        Args:
            frame_filename: Filename of the frame (e.g., "frame_000123.jpg")
            
        Returns:
            Frame number if found, None otherwise
        """
        # Try to match patterns like frame_000123.jpg or frame-000123.jpg
        pattern = r'frame[_-]0*(\d+)\.'
        match = re.search(pattern, frame_filename)
        if match:
            return int(match.group(1))
        return None
    
    def extract_folder_name(self, frame_path: str) -> str:
        """
        Extract the folder name from a frame path.
        
        Args:
            frame_path: Full path to the frame file
            
        Returns:
            Folder name
        """
        return os.path.basename(os.path.dirname(frame_path))
    
    def find_record_by_frame_number(self, frame_number: int, folder_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find a record by frame number and optionally folder name.
        
        Args:
            frame_number: Frame number to search for
            folder_name: Optional folder name to narrow down the search
            
        Returns:
            Matching record if found, None otherwise
        """
        try:
            # Search by frame number
            filter_formula = f"{{FrameNumber}} = {frame_number}"
            matching_records = self.get_all_records(filter_by_formula=filter_formula)
            
            if not matching_records:
                logger.warning(f"No records found with frame number {frame_number}")
                return None
            
            logger.info(f"Found {len(matching_records)} records with frame number {frame_number}")
            
            # If folder name is provided, try to narrow down by folder name
            if folder_name and len(matching_records) > 1:
                logger.info(f"Trying to narrow by folder name: {folder_name}")
                for record in matching_records:
                    record_folder = record.get('fields', {}).get('FolderName', '')
                    if record_folder == folder_name:
                        logger.info(f"Found exact match with folder name: {folder_name}")
                        return record
                
                # If no exact match, try partial match
                for record in matching_records:
                    record_folder = record.get('fields', {}).get('FolderName', '')
                    if folder_name in record_folder or record_folder in folder_name:
                        logger.info(f"Found partial match with folder name: {record_folder}")
                        return record
            
            # If no folder match or folder name not provided, return the first record
            return matching_records[0]
        
        except Exception as e:
            logger.error(f"Error finding record by frame number {frame_number}: {e}")
            return None
    
    async def find_record_by_frame_path(self, frame_path: str) -> Optional[Dict[str, Any]]:
        """
        Find an Airtable record based on the frame path.
        
        Args:
            frame_path: Path to the frame
            
        Returns:
            Airtable record dictionary or None if not found
        """
        try:
            # Extract folder name and frame name
            frame_name = os.path.basename(frame_path)
            folder_path = os.path.dirname(frame_path)
            folder_name = os.path.basename(folder_path)
            
            # Build the Airtable filter formula - use the correct field names
            frame_path_formula = f"AND({{FolderPath}}='{folder_path}', {{FrameID}}='{frame_name}')"
            
            # Apply rate limiting
            time.sleep(self.rate_limit_sleep)
            
            # Make the API request
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params={
                    "filterByFormula": frame_path_formula,
                    "maxRecords": 1
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Airtable API error: {response.status_code} - {response.text}")
                return None
                
            # Parse the response
            data = response.json()
            records = data.get('records', [])
            
            if not records:
                logger.warning(f"No Airtable record found for frame: {frame_path}")
                return None
                
            # Return the first matching record
            return records[0]
            
        except Exception as e:
            logger.error(f"Error finding Airtable record for {frame_path}: {e}")
            return None
    
    def update_frame_metadata(self, record_id: str, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a frame record.
        
        Args:
            record_id: Airtable record ID
            metadata: Dictionary of metadata to update
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            result = self.update_record(record_id, metadata)
            return result is not None
        except Exception as e:
            logger.error(f"Error updating metadata for record {record_id}: {e}")
            return False

    def update_record(self, record_id: str, fields: Dict[str, Any]) -> bool:
        """
        Update an Airtable record.
        
        Args:
            record_id: Airtable record ID
            fields: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Apply rate limiting
            time.sleep(self.rate_limit_sleep)
            
            # Prepare the request payload
            payload = {
                "records": [
                    {
                        "id": record_id,
                        "fields": fields
                    }
                ]
            }
            
            # Make the API request
            response = requests.patch(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Airtable API error: {response.status_code} - {response.text}")
                return False
                
            logger.info(f"Successfully updated Airtable record: {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating Airtable record {record_id}: {e}")
            return False 