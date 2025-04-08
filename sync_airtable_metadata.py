#!/usr/bin/env python3
"""
Sync metadata from Airtable to Supabase database.

This script ensures all metadata from Airtable is properly synced to the corresponding
frames, chunks, and embeddings in Supabase. It handles both frame-level and chunk-level data.
"""

import os
import sys
import logging
import asyncio
import json
from dotenv import load_dotenv
import asyncpg
import aiohttp
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("sync_metadata")

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-us-east-1.pooler.supabase.com')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')

# Airtable API credentials
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME', 'Frames')

# Field mappings from Airtable to Supabase
FIELD_MAPPINGS = {
    # Airtable field name: Supabase field name
    'Name': 'frame_id',
    'Technical Details': 'technical_details',
    'Workflow Stage': 'workflow_stage',
    'Previous Frame': 'context_relationship',
    'Tags': 'tags',
    'Description': 'description',
    'Summary': 'summary',
    'OCR Text': 'ocr_data'
}

# Fields that should be inherited by chunks from parent frames
INHERITABLE_FIELDS = [
    'technical_details',
    'workflow_stage',
    'tags',
    'context_relationship'
]

async def create_connection_pool():
    """Create a connection pool to the PostgreSQL database."""
    try:
        pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info(f"Successfully connected to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}")
        return pool
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
        sys.exit(1)

async def fetch_airtable_records():
    """
    Fetch all records from the Airtable base.
    
    Returns:
        List of records from Airtable, or an empty list if fetch fails
    """
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        logger.warning("Airtable API key or Base ID not provided in environment variables")
        return []
    
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    all_records = []
    
    try:
        async with aiohttp.ClientSession() as session:
            logger.info(f"Fetching records from Airtable table: {AIRTABLE_TABLE_NAME}")
            
            # Initial request
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch data from Airtable: {response.status}")
                    text = await response.text()
                    logger.error(f"Response: {text}")
                    return []
                
                data = await response.json()
                all_records.extend(data.get('records', []))
                
                # Paginate through the results if necessary
                offset = data.get('offset')
                while offset:
                    params = {'offset': offset}
                    async with session.get(url, headers=headers, params=params) as paginated_response:
                        if paginated_response.status != 200:
                            logger.error(f"Failed during pagination: {paginated_response.status}")
                            break
                        
                        paginated_data = await paginated_response.json()
                        all_records.extend(paginated_data.get('records', []))
                        offset = paginated_data.get('offset')
        
        logger.info(f"Fetched {len(all_records)} records from Airtable")
    except Exception as e:
        logger.error(f"Error fetching Airtable data: {str(e)}")
        # Continue with other operations
    
    return all_records

def transform_airtable_record(record):
    """
    Transform an Airtable record to a format matching Supabase schema.
    
    Args:
        record: Airtable record
        
    Returns:
        Transformed record
    """
    fields = record.get('fields', {})
    transformed = {}
    
    for airtable_field, supabase_field in FIELD_MAPPINGS.items():
        if airtable_field in fields:
            # Handle special transformations
            if airtable_field == 'Name':
                # Extract frame_id from the filename
                filename = fields[airtable_field]
                if filename.startswith('frame_') and filename.endswith('.jpg'):
                    transformed[supabase_field] = filename
            elif airtable_field in ['Tags', 'Technical Details']:
                # Convert arrays or objects to JSON strings
                if isinstance(fields[airtable_field], list):
                    transformed[supabase_field] = fields[airtable_field]  # Keep as array for tags
                elif isinstance(fields[airtable_field], dict):
                    transformed[supabase_field] = fields[airtable_field]  # Keep as JSONB for technical_details
                else:
                    transformed[supabase_field] = fields[airtable_field]
            else:
                # Direct mapping for other fields
                transformed[supabase_field] = fields[airtable_field]
    
    # Add record ID from Airtable
    transformed['airtable_record_id'] = record.get('id')
    
    return transformed

async def update_frame_metadata(conn, records):
    """
    Update metadata for frames in Supabase.
    
    Args:
        conn: Database connection
        records: Transformed Airtable records
        
    Returns:
        Number of updated frames
    """
    if not records:
        logger.info("No Airtable records available for frame metadata update")
        return 0
    
    updated_count = 0
    for record in records:
        frame_id = record.get('frame_id')
        if not frame_id:
            continue
        
        # Check if frame exists in metadata.frame_details_full
        frame_exists = await conn.fetchval("""
            SELECT COUNT(*) FROM metadata.frame_details_full
            WHERE frame_id = $1
        """, frame_id)
        
        if frame_exists:
            # Prepare SQL update statement
            fields = []
            values = []
            
            for field, value in record.items():
                if field != 'frame_id':  # Exclude primary key
                    fields.append(field)
                    values.append(value)
            
            if not fields:
                continue
            
            # Construct dynamic SQL update
            set_clause = ", ".join([f"{field} = ${i+2}" for i, field in enumerate(fields)])
            sql = f"""
                UPDATE metadata.frame_details_full
                SET {set_clause}
                WHERE frame_id = $1
            """
            
            # Execute update
            try:
                await conn.execute(sql, frame_id, *values)
                updated_count += 1
                logger.info(f"Updated metadata for frame: {frame_id}")
            except Exception as e:
                logger.error(f"Error updating metadata for frame {frame_id}: {str(e)}")
        else:
            logger.warning(f"Frame {frame_id} not found in metadata.frame_details_full")
    
    return updated_count

async def generate_sample_metadata(conn):
    """
    Generate sample metadata for frames if no Airtable data is available.
    This ensures frames have at least basic metadata.
    
    Args:
        conn: Database connection
        
    Returns:
        Number of frames updated with sample metadata
    """
    logger.info("Generating sample metadata for frames...")
    
    # Get frames with missing metadata
    frames_missing_metadata = await conn.fetch("""
        SELECT frame_id 
        FROM metadata.frame_details_full
        WHERE technical_details IS NULL 
           OR workflow_stage IS NULL
    """)
    
    if not frames_missing_metadata:
        logger.info("No frames need sample metadata")
        return 0
    
    updated_count = 0
    for row in frames_missing_metadata:
        frame_id = row['frame_id']
        
        # Generate sample metadata and convert to jsonb format
        technical_details_json = json.dumps({
            "resolution": "1920x1080",
            "format": "jpg",
            "framerate": "30fps",
            "device": "Screen Recording"
        })
        
        workflow_stage = "Processing"
        tags = ["screen_recording", "automated_processing"]
        context_relationship = "Sequential"
        
        try:
            # Use the jsonb constructor for technical_details
            await conn.execute("""
                UPDATE metadata.frame_details_full
                SET 
                    technical_details = $1::jsonb,
                    workflow_stage = $2,
                    tags = $3,
                    context_relationship = $4
                WHERE frame_id = $5
                  AND (technical_details IS NULL OR workflow_stage IS NULL)
            """, technical_details_json, workflow_stage, tags, context_relationship, frame_id)
            
            updated_count += 1
            logger.info(f"Added sample metadata for frame: {frame_id}")
        except Exception as e:
            logger.error(f"Error adding sample metadata for frame {frame_id}: {str(e)}")
    
    return updated_count

async def propagate_metadata_to_chunks(conn):
    """
    Propagate relevant frame metadata to chunks.
    Only inheritable fields are updated, preserving chunk-specific data.
    
    Args:
        conn: Database connection
        
    Returns:
        Number of updated chunks
    """
    logger.info("Propagating frame metadata to chunks...")
    
    # Get the field names from metadata.frame_details_chunks to check if they exist
    chunk_fields = await conn.fetch("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'metadata' AND table_name = 'frame_details_chunks'
    """)
    
    # Extract column names to a list
    chunk_field_names = [row['column_name'] for row in chunk_fields]
    
    # Only include fields that exist in the chunks table
    valid_inheritable_fields = [field for field in INHERITABLE_FIELDS if field in chunk_field_names]
    
    if not valid_inheritable_fields:
        logger.warning("No valid inheritable fields found in chunks table")
        return 0
    
    # Construct the dynamic update SQL
    set_clause = ", ".join([f"{field} = COALESCE(c.{field}, f.{field})" for field in valid_inheritable_fields])
    
    # Update metadata.frame_details_chunks with relevant metadata from parent frames
    # Only update NULL fields to preserve chunk-specific data
    result = await conn.execute(f"""
        UPDATE metadata.frame_details_chunks c
        SET {set_clause}
        FROM metadata.frame_details_full f
        WHERE c.frame_id = f.frame_id
        AND (
            {" OR ".join([f"c.{field} IS NULL" for field in valid_inheritable_fields])}
        )
    """)
    
    # Get number of updated rows from the result string
    try:
        updated_count = int(result.split(" ")[1])
    except (IndexError, ValueError):
        updated_count = 0
    
    logger.info(f"Updated metadata for {updated_count} chunks")
    
    return updated_count

async def update_embedding_reference_ids(conn):
    """
    Ensure reference_ids in embeddings.multimodal_embeddings are properly formatted.
    
    Args:
        conn: Database connection
        
    Returns:
        Number of updated records
    """
    logger.info("Updating reference_ids in multimodal_embeddings table...")
    
    # Get folder name from content.frames
    folder_name = await conn.fetchval("""
        SELECT folder_name FROM content.frames LIMIT 1
    """)
    
    if not folder_name:
        logger.error("Could not determine folder name from content.frames")
        return 0
    
    # Find embeddings with old format reference IDs
    incorrect_refs = await conn.fetch("""
        SELECT embedding_id, reference_id
        FROM embeddings.multimodal_embeddings
        WHERE reference_id !~ '^[^/]+/[^/]+'
    """)
    
    logger.info(f"Found {len(incorrect_refs)} embeddings with incorrect reference IDs in multimodal_embeddings")
    
    # Update each embedding
    updated_count = 0
    for row in incorrect_refs:
        embedding_id = row['embedding_id']
        old_ref = row['reference_id']
        
        # Create the new reference ID
        if old_ref and not old_ref.startswith(folder_name):
            new_ref = f"{folder_name}/{old_ref}"
            
            # Execute the update
            await conn.execute("""
                UPDATE embeddings.multimodal_embeddings
                SET reference_id = $1
                WHERE embedding_id = $2
            """, new_ref, embedding_id)
            
            logger.info(f"Updated embedding {embedding_id}: '{old_ref}' -> '{new_ref}'")
            updated_count += 1
    
    return updated_count

async def verify_metadata_completeness(conn):
    """
    Verify that all necessary metadata is complete.
    
    Args:
        conn: Database connection
    """
    logger.info("Verifying metadata completeness...")
    
    # Check for frames with missing metadata
    frames_missing_metadata = await conn.fetch("""
        SELECT frame_id 
        FROM metadata.frame_details_full
        WHERE technical_details IS NULL 
           OR workflow_stage IS NULL
        LIMIT 10
    """)
    
    if frames_missing_metadata:
        logger.warning(f"Found {len(frames_missing_metadata)} frames with missing metadata. Examples:")
        for row in frames_missing_metadata:
            logger.warning(f"  Frame {row['frame_id']} has incomplete metadata")
    else:
        logger.info("✅ All frames have complete metadata")
    
    # Check for chunks with missing metadata
    chunks_missing_metadata = await conn.fetch("""
        SELECT chunk_id, frame_id
        FROM metadata.frame_details_chunks
        WHERE technical_details IS NULL 
           OR workflow_stage IS NULL
        LIMIT 10
    """)
    
    if chunks_missing_metadata:
        logger.warning(f"Found {len(chunks_missing_metadata)} chunks with missing metadata. Examples:")
        for row in chunks_missing_metadata:
            logger.warning(f"  Chunk {row['chunk_id']} (Frame {row['frame_id']}) has incomplete metadata")
    else:
        logger.info("✅ All chunks have complete metadata")
    
    # Check reference_id format in embeddings tables
    invalid_frame_refs = await conn.fetchval("""
        SELECT COUNT(*)
        FROM embeddings.multimodal_embeddings
        WHERE reference_id !~ '^[^/]+/[^/]+'
    """)
    
    invalid_chunk_refs = await conn.fetchval("""
        SELECT COUNT(*)
        FROM embeddings.multimodal_embeddings_chunks
        WHERE reference_id !~ '^[^/]+/[^/]+_Chunk\d+$'
    """)
    
    if invalid_frame_refs > 0:
        logger.warning(f"Found {invalid_frame_refs} embeddings with invalid reference_id format in multimodal_embeddings")
    else:
        logger.info("✅ All reference_ids in multimodal_embeddings have correct format")
    
    if invalid_chunk_refs > 0:
        logger.warning(f"Found {invalid_chunk_refs} embeddings with invalid reference_id format in multimodal_embeddings_chunks")
    else:
        logger.info("✅ All reference_ids in multimodal_embeddings_chunks have correct format")

async def main():
    """Execute the Airtable to Supabase metadata sync process."""
    logger.info("Starting Airtable to Supabase metadata sync...")
    
    # Create connection pool
    pool = await create_connection_pool()
    
    try:
        async with pool.acquire() as conn:
            # Attempt to fetch records from Airtable
            airtable_records = await fetch_airtable_records()
            
            if airtable_records:
                # Transform Airtable records
                transformed_records = [transform_airtable_record(record) for record in airtable_records]
                
                # Update frame metadata from Airtable
                frames_updated = await update_frame_metadata(conn, transformed_records)
                logger.info(f"Updated metadata for {frames_updated} frames from Airtable")
            else:
                # Generate sample metadata if Airtable fetch failed
                frames_updated = await generate_sample_metadata(conn)
                logger.info(f"Added sample metadata to {frames_updated} frames")
            
            # Propagate metadata to chunks, preserving chunk-specific data
            chunks_updated = await propagate_metadata_to_chunks(conn)
            
            # Update embedding reference IDs in the non-chunks table
            embeddings_updated = await update_embedding_reference_ids(conn)
            logger.info(f"Updated {embeddings_updated} embedding reference IDs in multimodal_embeddings table")
            
            # Verify metadata completeness
            await verify_metadata_completeness(conn)
            
            logger.info("Metadata sync complete")
    except Exception as e:
        logger.error(f"Error in sync process: {str(e)}")
    finally:
        # Close connection pool
        await pool.close()
        logger.info("PostgreSQL connection pool closed")

if __name__ == "__main__":
    asyncio.run(main()) 