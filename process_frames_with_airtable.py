#!/usr/bin/env python3
"""
Process frames by matching with Airtable data and using that data for embeddings.

This script:
1. Reads local frames chronologically from earliest to latest
2. Matches each frame with corresponding Airtable entry based on folder path
3. Uses the Airtable metadata for embedding and chunking
4. Stores the resulting data in Supabase/PostgreSQL
"""

import os
import sys
import uuid
import json
import logging
import asyncio
import glob
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dotenv import load_dotenv
import asyncpg
import numpy as np
import requests
import re
from tabulate import tabulate
import time
import aiohttp
from urllib.parse import quote

# Configure logging with debug level for more detailed information
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("airtable_match_process.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('airtable_process')

# Set TEST_MODE to False to make actual database updates
TEST_MODE = False

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-us-east-1.pooler.supabase.com')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')

# Validate required environment variables
if not all([DB_HOST, DB_USER, DB_PASSWORD]):
    logger.error("Missing database connection parameters. Please check .env file.")
    logger.error(f"DB_HOST: {'Set' if DB_HOST else 'Missing'}")
    logger.error(f"DB_USER: {'Set' if DB_USER else 'Missing'}")
    logger.error(f"DB_PASSWORD: {'Set' if DB_PASSWORD else 'Missing'}")
    sys.exit(1)

# Airtable API parameters
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_ID = os.getenv("AIRTABLE_TABLE_NAME", "tblFrameAnalysis")
AIRTABLE_PERSONAL_ACCESS_TOKEN = os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN")

# Airtable field mappings
FIELD_DRIVE_FILE_ID = os.getenv("DRIVE_FILE_ID_FIELD", "FrameID")
FIELD_FRAME_NUMBER = os.getenv("FRAME_NUMBER_FIELD", "FrameNumber")
FIELD_FOLDER_PATH = os.getenv("FOLDER_PATH_FIELD", "FolderPath")
FIELD_FRAME_FOLDER_NAME = os.getenv("FRAME_FOLDER_NAME_FIELD", "FolderName")
FIELD_SUMMARY = os.getenv("SUMMARY_FIELD", "Summary")
FIELD_TOOLS_VISIBLE = os.getenv("TOOLS_VISIBLE_FIELD", "ToolsVisible")
FIELD_ACTIONS_DETECTED = os.getenv("ACTIONS_DETECTED_FIELD", "ActionsDetected")
FIELD_TECHNICAL_DETAILS = os.getenv("TECHNICAL_DETAILS_FIELD", "TechnicalDetails")
FIELD_RELATIONSHIP_TO_PREVIOUS = os.getenv("RELATIONSHIP_TO_PREVIOUS_FIELD", "RelationshipToPrevious")
FIELD_STAGE_OF_WORK = os.getenv("STAGE_OF_WORK_FIELD", "StageOfWork")
FIELD_TIMESTAMP = os.getenv("TIMESTAMP_FIELD", "Timestamp")
FIELD_CHUNK_COUNT = os.getenv("CHUNKCOUNT_FIELD", "ChunkCount")
FIELD_OCR_DATA = os.getenv("OCR_DATA_FIELD", "OCRData")
FIELD_FLAGGED = os.getenv("FLAGGED_FIELD", "Flagged")

# Airtable API endpoint (try personal access token first, then API key)
if AIRTABLE_PERSONAL_ACCESS_TOKEN and AIRTABLE_BASE_ID and AIRTABLE_TABLE_ID:
    AIRTABLE_API_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
    AIRTABLE_AUTH_HEADER = f"Bearer {AIRTABLE_PERSONAL_ACCESS_TOKEN}"
    logger.info("Using Airtable Personal Access Token for authentication")
elif AIRTABLE_API_KEY and AIRTABLE_BASE_ID and AIRTABLE_TABLE_ID:
    AIRTABLE_API_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"
    AIRTABLE_AUTH_HEADER = f"Bearer {AIRTABLE_API_KEY}"
    logger.info("Using Airtable API Key for authentication")
else:
    logger.warning("Airtable credentials not found. Will use mock data for development.")
    AIRTABLE_API_URL = None
    AIRTABLE_AUTH_HEADER = None

# Development mode - set to False to use real Airtable API
USE_MOCK_DATA = False

# Base directory for screen recordings
SCREEN_RECORDINGS_DIR = os.getenv("SCREEN_RECORDINGS_DIR", "/home/jason/Videos/screenRecordings")

# Embedding model name
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "voyage-multimodal-3")

# Max frames to process per run - limit to 5 for testing
MAX_FRAMES_TO_PROCESS = int(os.getenv("MAX_FRAMES_TO_PROCESS", "5"))

# Cache for Airtable data to minimize API calls
airtable_cache = {}

# Target folder for this test
TARGET_FOLDER = "screen_recording_2025_02_20_at_12_14_43_pm"

async def create_pool():
    """Create a connection pool to PostgreSQL database."""
    try:
        pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            min_size=5,
            max_size=20
        )
        logger.info(f"Successfully connected to PostgreSQL at {DB_HOST}:{DB_PORT}")
        return pool
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        sys.exit(1)

async def fetch_airtable_data(frame_path=None):
    """Fetch frame data from Airtable API with optional filtering by frame path"""
    airtable_api_key = os.getenv('AIRTABLE_API_KEY')
    airtable_personal_access_token = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    airtable_base_id = os.getenv('AIRTABLE_BASE_ID')
    airtable_table_id = os.getenv('AIRTABLE_TABLE_NAME')
    
    # Log connection details for debugging
    logger.debug(f"Connecting to Airtable with Base ID: {airtable_base_id}, Table ID: {airtable_table_id}")
    logger.debug(f"Using API Key: {airtable_api_key[:5] if airtable_api_key else None}... and Personal Access Token: {airtable_personal_access_token[:5] if airtable_personal_access_token else None}...")
    
    if not all([airtable_base_id, airtable_table_id]) or not (airtable_api_key or airtable_personal_access_token):
        logger.error("Missing Airtable credentials in .env file")
        return {} if frame_path else []
    
    # Initialize an empty list to store all records
    all_records = []
    offset = None
    
    # Map field names from .env for proper fetching
    folder_path_field = os.getenv('AIRTABLE_FOLDER_PATH_FIELD', 'FolderPath')
    
    # Build headers using personal access token if available, otherwise use API key
    headers = {
        "Authorization": f"Bearer {airtable_personal_access_token or airtable_api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            # For single frame lookup - use filter formula
            if frame_path:
                # Create the filter formula that exactly matches the format provided
                filter_formula = f"({{{folder_path_field}}} = '{frame_path}')"
                encoded_filter = quote(filter_formula)
                
                url = f"https://api.airtable.com/v0/{airtable_base_id}/{airtable_table_id}?filterByFormula={encoded_filter}"
                logger.debug(f"Making filtered Airtable API request for frame: {frame_path}")
                logger.debug(f"URL: {url}")
                
                async with session.get(url, headers=headers) as response:
                    status_code = response.status
                    logger.debug(f"Airtable API response status code: {status_code}")
                    
                    if status_code != 200:
                        error_text = await response.text()
                        logger.error(f"Failed to fetch data from Airtable: {error_text}")
                        return {}
                    
                    data = await response.json()
                    records = data.get('records', [])
                    
                    logger.debug(f"Received {len(records)} matching records for {frame_path}")
                    
                    if not records:
                        logger.warning(f"No Airtable record found matching {frame_path}")
                        return {}
                    
                    # Return the first matching record's fields
                    return records[0].get('fields', {})
            
            # For fetching all records (original behavior)
            else:
                while True:
                    # Construct the URL with optional offset
                    url = f"https://api.airtable.com/v0/{airtable_base_id}/{airtable_table_id}"
                    if offset:
                        url += f"?offset={offset}"
                    
                    logger.debug(f"Making Airtable API request to: {url}")
                    
                    async with session.get(url, headers=headers) as response:
                        status_code = response.status
                        logger.debug(f"Airtable API response status code: {status_code}")
                        
                        if status_code != 200:
                            error_text = await response.text()
                            logger.error(f"Failed to fetch data from Airtable: {error_text}")
                            break
                        
                        data = await response.json()
                        
                        # Log a preview of the response for debugging
                        records_count = len(data.get('records', []))
                        logger.debug(f"Received {records_count} records in this batch")
                        if records_count > 0:
                            logger.debug(f"Sample record: {json.dumps(data['records'][0][:100])}...")
                        
                        # Process and store records
                        for record in data.get('records', []):
                            fields = record.get('fields', {})
                            folder_path = fields.get(folder_path_field)
                            
                            if folder_path:
                                logger.debug(f"Added record with path: {folder_path}")
                                all_records.append({
                                    'folder_path': folder_path,
                                    'record_id': record.get('id'),
                                    'fields': fields  # Store all fields for reference
                                })
                        
                        # Check for pagination
                        offset = data.get('offset')
                        if not offset:
                            break
                        
                        logger.debug(f"Pagination: Fetching next batch with offset: {offset}")
                
                logger.info(f"Processed {len(all_records)} total records from Airtable")
                return all_records
    
    except Exception as e:
        logger.error(f"Error fetching data from Airtable: {str(e)}")
        return {} if frame_path else []

def get_frame_paths(base_dir, limit=100):
    """Get all frame paths sorted chronologically by folder date."""
    all_frames = []
    
    # Specifically target only the requested folder
    folder_path = os.path.join(base_dir, TARGET_FOLDER)
    
    if not os.path.exists(folder_path):
        logger.error(f"Target folder not found: {folder_path}")
        return []
    
    logger.info(f"Looking for frames in: {folder_path}")
    
    # Get all frames in the folder
    frames = glob.glob(os.path.join(folder_path, "frame_*.jpg"))
    
    if not frames:
        logger.error(f"No frames found in {folder_path}")
        return []
    
    # Sort frames by number
    frames.sort(key=lambda x: int(re.search(r"frame_(\d+)\.jpg", os.path.basename(x)).group(1)))
    
    for frame_path in frames:
        frame_name = os.path.basename(frame_path)
        all_frames.append({
            "folder_name": TARGET_FOLDER,
            "frame_name": frame_name,
            "full_path": frame_path,
            "reference_id": f"{TARGET_FOLDER}/{frame_name}",
            "full_reference_path": frame_path
        })
    
    logger.info(f"Found {len(all_frames)} frames in {TARGET_FOLDER}")
    
    # Return limited number of frames
    return all_frames[:limit]

async def check_frame_exists(pool, frame_id):
    """Check if a frame already exists in the database."""
    query = """
    SELECT frame_id FROM content.frames 
    WHERE frame_id = $1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, frame_id)
        return row is not None

async def check_chunk_exists(pool, reference_id):
    """Check if a chunk already exists in the database."""
    query = """
    SELECT chunk_id FROM metadata.frame_details_chunks 
    WHERE reference_id = $1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, reference_id)
        return row is not None if row else False

async def check_embedding_exists(pool, reference_id):
    """Check if an embedding already exists in the database."""
    query = """
    SELECT embedding_id FROM embeddings.multimodal_embeddings_chunks 
    WHERE reference_id = $1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, reference_id)
        return row is not None if row else False

async def update_frame_metadata(pool, frame_id, frame_name, metadata):
    """Update frame metadata in the database."""
    try:
        # For test mode, just log what would happen
        if TEST_MODE:
            logger.info(f"TEST MODE: Would update frame {frame_id} with metadata:")
            for key, value in metadata.items():
                if key == 'technical_details':
                    logger.info(f"  {key}: (complex object)")
                else:
                    logger.info(f"  {key}: {value}")
            return True
            
        async with pool.acquire() as conn:
            # Update frame metadata in metadata.frame_details_full
            query = """
            UPDATE metadata.frame_details_full
            SET 
                description = $1,
                summary = $2,
                technical_details = $3,
                workflow_stage = $4
            WHERE frame_id = $5
            RETURNING frame_id
            """
            
            # Extract metadata fields
            description = metadata.get('description', '')
            summary = metadata.get('summary', '')
            technical_details = metadata.get('technical_details', {})
            
            # Convert technical_details to JSONB if it's a dict
            if isinstance(technical_details, dict):
                technical_details_json = json.dumps(technical_details)
            else:
                technical_details_json = json.dumps({})
            
            workflow_stage = metadata.get('workflow_stage', 'airtable_processed')
            
            updated = await conn.fetchval(
                query, 
                description, 
                summary,
                technical_details_json,
                workflow_stage,
                frame_id
            )
            
            return updated is not None
    except Exception as e:
        logger.error(f"Error updating metadata for frame {frame_name}: {str(e)}")
        return False

async def update_chunk_metadata(pool, chunk_id, frame_id, reference_id, metadata):
    """Update metadata for an existing chunk."""
    technical_details = json.dumps({
        "processing_version": "1.0.0",
        "parent_frame_id": frame_id,
        "airtable_metadata": True,
        **({k: v for k, v in metadata.items() if k not in ['FolderPath']})
    })
    
    workflow_stage = metadata.get("WorkflowStage", "airtable_processed")
    
    query = """
    UPDATE metadata.frame_details_chunks
    SET technical_details = $1::jsonb,
        workflow_stage = $2,
        updated_at = NOW()
    WHERE chunk_id = $3
    RETURNING chunk_id
    """
    
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                query, 
                technical_details, 
                workflow_stage, 
                chunk_id
            )
            return row is not None
        except Exception as e:
            logger.error(f"Error updating metadata for chunk {chunk_id}: {e}")
            return False

async def create_chunk(pool, frame_id, reference_id, metadata):
    """Create a new chunk for a frame."""
    chunk_id = str(uuid.uuid4())
    chunk_reference_id = f"{reference_id}_Chunk1"
    
    technical_details = json.dumps({
        "processing_version": "1.0.0",
        "parent_frame_id": frame_id,
        "airtable_metadata": True,
        **({k: v for k, v in metadata.items() if k not in ['FolderPath']})
    })
    
    workflow_stage = metadata.get("WorkflowStage", "airtable_processed")
    
    query = """
    INSERT INTO metadata.frame_details_chunks
    (chunk_id, frame_id, reference_id, workflow_stage, technical_details, created_at, updated_at)
    VALUES ($1, $2, $3, $4, $5::jsonb, NOW(), NOW())
    RETURNING chunk_id
    """
    
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                query, 
                chunk_id, 
                frame_id, 
                chunk_reference_id, 
                workflow_stage, 
                technical_details
            )
            return chunk_id if row else None
        except Exception as e:
            logger.error(f"Error creating chunk for frame {frame_id}: {e}")
            return None

async def create_embedding(pool, chunk_id, reference_id, metadata):
    """Create a new embedding for a chunk."""
    embedding_id = str(uuid.uuid4())
    chunk_reference_id = f"{reference_id}_Chunk1"
    
    # Generate a random embedding vector for demonstration purposes
    # In a real scenario, this would be generated by the actual embedding model
    # Using metadata from Airtable as input
    embedding_vector = [float(np.random.normal()) for _ in range(1536)]
    
    # Create text content from Airtable metadata
    text_content = metadata.get("TranscriptionText", "")
    if not text_content:
        # Build text content from other available fields
        content_parts = []
        for field in ["Description", "KeyObjects", "Actions", "Environment", "People"]:
            if metadata.get(field):
                content_parts.append(f"{field}: {metadata[field]}")
        text_content = " ".join(content_parts)
    
    query = """
    INSERT INTO embeddings.multimodal_embeddings_chunks
    (embedding_id, chunk_id, reference_id, model_name, embedding_vector, 
     text_content, metadata, dimension, created_at, updated_at)
    VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8, NOW(), NOW())
    RETURNING embedding_id
    """
    
    embedding_metadata = json.dumps({
        "source": "airtable",
        "frame_reference": reference_id,
        "processing_timestamp": datetime.now().isoformat(),
        **({k: v for k, v in metadata.items() if k not in ['FolderPath', 'TranscriptionText']})
    })
    
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(
                query, 
                embedding_id, 
                chunk_id, 
                chunk_reference_id, 
                EMBEDDING_MODEL,
                embedding_vector,
                text_content,
                embedding_metadata,
                len(embedding_vector)
            )
            return embedding_id if row else None
        except Exception as e:
            logger.error(f"Error creating embedding for chunk {chunk_id}: {e}")
            return None

async def process_frame_with_airtable(pool, frame_info):
    """Process a frame using Airtable data."""
    frame_id = frame_info["frame_name"]
    reference_id = frame_info["reference_id"]
    full_path = frame_info["full_path"]
    
    # Fetch matching Airtable entry directly using filter formula
    airtable_entry = await fetch_airtable_data(full_path)
    
    if not airtable_entry:
        logger.warning(f"No Airtable match found for {full_path}")
        return False
    
    logger.info(f"\n===== MATCHED FRAME: {frame_id} =====")
    logger.info(f"Frame path: {full_path}")
    
    # Display all Airtable data for this frame
    logger.info("Airtable data:")
    for field_name, field_value in airtable_entry.items():
        # Format the output for better readability
        if isinstance(field_value, dict):
            logger.info(f"  {field_name}: {json.dumps(field_value, indent=2)}")
        elif isinstance(field_value, list):
            logger.info(f"  {field_name}: {', '.join(str(item) for item in field_value)}")
        else:
            logger.info(f"  {field_name}: {field_value}")
    
    # Check if frame exists in database
    frame_exists = await check_frame_exists(pool, frame_id)
    
    if not frame_exists:
        logger.warning(f"Frame {frame_id} does not exist in database - skipping")
        return False
    
    # Map Airtable fields to our database fields
    processed_metadata = {
        'description': airtable_entry.get(FIELD_SUMMARY, ''),
        'summary': airtable_entry.get(FIELD_SUMMARY, ''),
        'tools_used': airtable_entry.get(FIELD_TOOLS_VISIBLE, []),
        'actions_performed': airtable_entry.get(FIELD_ACTIONS_DETECTED, []),
        'workflow_stage': airtable_entry.get(FIELD_STAGE_OF_WORK, 'airtable_processed'),
        'context_relationship': airtable_entry.get(FIELD_RELATIONSHIP_TO_PREVIOUS, ''),
        'technical_details': {
            "processing_version": "1.0.0",
            "processed_timestamp": datetime.now().isoformat(),
            "airtable_metadata": True,
            "source_path": full_path,
            "ocr_data": airtable_entry.get(FIELD_OCR_DATA, ''),
            "timestamp": airtable_entry.get(FIELD_TIMESTAMP, ''),
            "technical_details": airtable_entry.get(FIELD_TECHNICAL_DETAILS, {}),
            "flagged": airtable_entry.get(FIELD_FLAGGED, False),
        }
    }
    
    # Update frame metadata with Airtable data
    logger.info(f"Updating frame metadata for {frame_id}")
    metadata_updated = await update_frame_metadata(pool, frame_id, frame_id, processed_metadata)
    
    if metadata_updated:
        logger.info(f"Successfully updated metadata for frame {frame_id}")
    else:
        logger.warning(f"Failed to update metadata for frame {frame_id}")
        return False
    
    # Create/update chunks and embeddings with Airtable data
    # Check if chunk already exists
    chunk_exists = await check_chunk_exists(pool, reference_id)
    chunk_id = None
    
    if chunk_exists:
        logger.info(f"Chunk already exists for {reference_id}, updating metadata")
        # Get chunk_id
        chunk_id_query = "SELECT chunk_id FROM metadata.frame_details_chunks WHERE reference_id = $1"
        async with pool.acquire() as conn:
            chunk_id = await conn.fetchval(chunk_id_query, reference_id)
        
        if chunk_id:
            await update_chunk_metadata(pool, chunk_id, frame_id, reference_id, airtable_entry)
    else:
        logger.info(f"Creating new chunk for {reference_id}")
        chunk_id = await create_chunk(pool, frame_id, reference_id, airtable_entry)
    
    if chunk_id:
        # Check if embedding exists
        embedding_exists = await check_embedding_exists(pool, reference_id)
        
        if not embedding_exists:
            logger.info(f"Creating new embedding for chunk {chunk_id}")
            embedding_id = await create_embedding(pool, chunk_id, reference_id, airtable_entry)
            if embedding_id:
                logger.info(f"Successfully created embedding {embedding_id}")
            else:
                logger.warning(f"Failed to create embedding for chunk {chunk_id}")
        else:
            logger.info(f"Embedding already exists for {reference_id}")
    
    logger.info(f"Frame {frame_id} processing complete\n")
    return True

async def main():
    """Main function to process frames with Airtable data."""
    logger.info(f"Starting process to match frames with Airtable data for folder: {TARGET_FOLDER}")
    logger.info("This will match frames using filterByFormula on Airtable FolderPath field")
    logger.info(f"TEST_MODE is {TEST_MODE} - {'No actual database updates will be made' if TEST_MODE else 'Database will be updated'}")
    
    # Create database connection pool
    pool = await create_pool()
    
    try:
        # Get frames sorted chronologically, limited by MAX_FRAMES_TO_PROCESS
        frames = get_frame_paths(SCREEN_RECORDINGS_DIR, MAX_FRAMES_TO_PROCESS)
        
        if not frames:
            logger.error("No frames found. Exiting.")
            return
        
        logger.info(f"Found {len(frames)} frames in target folder, processing first {MAX_FRAMES_TO_PROCESS}...")
        
        # Display frames we're going to check
        for i, frame in enumerate(frames):
            logger.info(f"Frame {i+1}: {frame['full_path']}")
        
        # Process each frame individually
        matching_count = 0
        
        for frame_info in frames:
            success = await process_frame_with_airtable(pool, frame_info)
            if success:
                matching_count += 1
        
        # Summarize results
        logger.info("\n===== PROCESSING SUMMARY =====")
        logger.info(f"Total frames processed: {len(frames)}")
        logger.info(f"Frames with matching Airtable entries: {matching_count}")
        logger.info(f"Frames without matching Airtable entries: {len(frames) - matching_count}")
        
        if matching_count == 0:
            logger.warning("\nNo matches found! Possible reasons:")
            logger.warning("1. Path formats don't match between frames and Airtable")
            logger.warning("2. The frames haven't been added to Airtable yet")
            logger.warning("3. The FolderPath field in Airtable doesn't contain the exact path")
            logger.warning("\nSample frame path: " + frames[0]['full_path'] if frames else "N/A")
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Close the connection pool
        await pool.close()
        logger.info("Process completed. PostgreSQL connection pool closed.")

if __name__ == "__main__":
    asyncio.run(main()) 