#!/usr/bin/env python3
"""
Script to update reference_id format in renamed tables to use foldername/filename format.
"""

import os
import sys
import asyncio
import logging
import asyncpg
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path setup
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Import environment variables
try:
    if Path(project_root / '.env').exists():
        # Load .env file if python-dotenv is available
        try:
            from dotenv import load_dotenv
            load_dotenv(project_root / '.env')
            logger.info("Loaded environment from .env file")
        except ImportError:
            logger.warning("python-dotenv not found, using environment variables as is")
except Exception as e:
    logger.error(f"Error loading environment: {e}")

async def get_connection():
    """Get a database connection."""
    # Get connection parameters from environment
    host = os.getenv('POSTGRES_HOST')
    port = os.getenv('POSTGRES_PORT')
    database = os.getenv('POSTGRES_DB')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASS')
    
    # Check if all parameters are available
    if not all([host, port, database, user, password]):
        logger.error("Incomplete PostgreSQL connection information")
        return None
    
    try:
        # Create connection
        dsn = f"postgres://{user}:{password}@{host}:{port}/{database}"
        conn = await asyncpg.connect(dsn=dsn)
        logger.info(f"Connected to PostgreSQL database at {host}:{port}/{database}")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

async def update_frame_reference_ids(conn):
    """Update reference_ids in frame_details_full to include folder name."""
    try:
        # First, check if the table exists
        exists = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'metadata' 
            AND table_name = 'frame_details_full'
        )
        """)
        
        if not exists:
            logger.error("Table metadata.frame_details_full does not exist")
            return False
        
        # Get all frames with their folder names
        frames = await conn.fetch("""
        SELECT f.id, f.frame_name, f.folder_name, fdf.reference_id
        FROM content.frames f
        JOIN metadata.frame_details_full fdf ON f.id = fdf.frame_id
        """)
        
        logger.info(f"Found {len(frames)} frames to update reference_ids")
        
        # Update each frame's reference_id
        updated_count = 0
        for frame in frames:
            frame_id = frame['id']
            frame_name = frame['frame_name']
            folder_name = frame['folder_name'] or "unknown_folder"
            current_ref_id = frame['reference_id']
            
            # Create new reference_id in the format "folder_name/frame_name"
            new_ref_id = f"{folder_name}/{frame_name}"
            
            # Only update if different
            if current_ref_id != new_ref_id:
                await conn.execute("""
                UPDATE metadata.frame_details_full
                SET reference_id = $1, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE frame_id = $2
                """, new_ref_id, frame_id)
                updated_count += 1
        
        logger.info(f"Updated {updated_count} frame reference_ids in frame_details_full")
        
        # Also update in embeddings.multimodal_embeddings for frames
        embed_updates = await conn.execute("""
        UPDATE embeddings.multimodal_embeddings e
        SET reference_id = f.folder_name || '/' || f.frame_name,
            updated_at = CURRENT_TIMESTAMP
        FROM content.frames f
        JOIN metadata.frame_details_full fdf ON f.id = fdf.frame_id
        WHERE e.reference_id = fdf.reference_id
        AND e.reference_type = 'frame'
        AND e.reference_id != f.folder_name || '/' || f.frame_name
        """)
        
        logger.info(f"Updated frame reference_ids in multimodal_embeddings")
        return True
    
    except Exception as e:
        logger.error(f"Error updating frame reference_ids: {e}")
        return False

async def update_chunk_reference_ids(conn):
    """Update reference_ids in frame_details_chunk to include folder name and frame name."""
    try:
        # First, check if the table exists
        exists = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'metadata' 
            AND table_name = 'frame_details_chunk'
        )
        """)
        
        if not exists:
            logger.error("Table metadata.frame_details_chunk does not exist")
            return False
        
        # Get all chunks with their frame and folder information
        chunks = await conn.fetch("""
        SELECT c.id, c.frame_id, c.chunk_sequence_id, 
               f.frame_name, f.folder_name, fdc.reference_id,
               fdc.chunk_id
        FROM content.chunks c
        JOIN content.frames f ON c.frame_id = f.id
        JOIN metadata.frame_details_chunk fdc ON c.id = fdc.chunk_id
        """)
        
        logger.info(f"Found {len(chunks)} chunks to update reference_ids")
        
        # Update each chunk's reference_id
        updated_count = 0
        for chunk in chunks:
            chunk_id = chunk['chunk_id']
            frame_name = chunk['frame_name']
            folder_name = chunk['folder_name'] or "unknown_folder"
            chunk_sequence_id = chunk['chunk_sequence_id']
            current_ref_id = chunk['reference_id']
            
            # Create new reference_id in the format "folder_name/frame_name/chunk_sequence_id"
            new_ref_id = f"{folder_name}/{frame_name}/chunk_{chunk_sequence_id}"
            
            # Only update if different
            if current_ref_id != new_ref_id:
                await conn.execute("""
                UPDATE metadata.frame_details_chunk
                SET reference_id = $1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE chunk_id = $2
                """, new_ref_id, chunk_id)
                updated_count += 1
        
        logger.info(f"Updated {updated_count} chunk reference_ids in frame_details_chunk")
        
        # Also update in embeddings.multimodal_embeddings for chunks
        embed_updates = await conn.execute("""
        UPDATE embeddings.multimodal_embeddings e
        SET reference_id = f.folder_name || '/' || f.frame_name || '/chunk_' || c.chunk_sequence_id,
            updated_at = CURRENT_TIMESTAMP
        FROM content.chunks c
        JOIN content.frames f ON c.frame_id = f.id
        JOIN metadata.frame_details_chunk fdc ON c.id = fdc.chunk_id
        WHERE e.reference_id = fdc.reference_id
        AND e.reference_type = 'chunk'
        AND e.reference_id != f.folder_name || '/' || f.frame_name || '/chunk_' || c.chunk_sequence_id
        """)
        
        logger.info(f"Updated chunk reference_ids in multimodal_embeddings")
        return True
    
    except Exception as e:
        logger.error(f"Error updating chunk reference_ids: {e}")
        return False

async def main():
    """Main function to update reference_ids."""
    logger.info("Starting reference_id update process")
    
    # Get database connection
    conn = await get_connection()
    if not conn:
        logger.error("Could not connect to database. Update aborted.")
        return
    
    try:
        # Start a transaction
        async with conn.transaction():
            # Update frame reference_ids
            frame_success = await update_frame_reference_ids(conn)
            if not frame_success:
                logger.error("Failed to update frame reference_ids")
                return
            
            # Update chunk reference_ids
            chunk_success = await update_chunk_reference_ids(conn)
            if not chunk_success:
                logger.error("Failed to update chunk reference_ids")
                return
            
            logger.info("Successfully updated all reference_ids")
    
    except Exception as e:
        logger.error(f"Error during update process: {e}")
    
    finally:
        # Close connection
        await conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    asyncio.run(main()) 