#!/usr/bin/env python3
"""
Update reference IDs across all tables to use the standardized format:
- Frames: foldername/filename
- Chunks: foldername/filename_ChunkN

This ensures consistent reference IDs across the database.
"""

import os
import sys
import logging
import asyncio
import json
import re
from dotenv import load_dotenv
import asyncpg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("update_refids")

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-us-east-1.pooler.supabase.com')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')

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

async def get_frames_data(conn):
    """
    Get data for all frames including folder name and filename.
    
    Args:
        conn: Database connection
        
    Returns:
        Dictionary mapping frame_id to (folder_name, file_name)
    """
    try:
        frames = await conn.fetch("""
            SELECT frame_id, folder_name, file_name
            FROM content.frames
        """)
        
        frames_data = {}
        for frame in frames:
            frames_data[frame['frame_id']] = (
                frame['folder_name'],
                frame['file_name']
            )
        
        logger.info(f"Retrieved data for {len(frames_data)} frames")
        return frames_data
    except Exception as e:
        logger.error(f"Error getting frames data: {str(e)}")
        raise

async def get_chunks_data(conn):
    """
    Get data for all chunks and their relationship to frames.
    
    Args:
        conn: Database connection
        
    Returns:
        Dictionary mapping chunk_id to frame_id
    """
    try:
        chunks = await conn.fetch("""
            SELECT chunk_id, frame_id
            FROM metadata.frame_details_chunks
        """)
        
        chunks_data = {}
        for chunk in chunks:
            chunks_data[chunk['chunk_id']] = chunk['frame_id']
        
        logger.info(f"Retrieved data for {len(chunks_data)} chunks")
        return chunks_data
    except Exception as e:
        logger.error(f"Error getting chunks data: {str(e)}")
        raise

async def update_frame_reference_ids(conn, frames_data):
    """
    Update reference IDs for frames to format 'foldername/filename'.
    
    Args:
        conn: Database connection
        frames_data: Dictionary mapping frame_id to (folder_name, file_name)
        
    Returns:
        Number of updated records
    """
    total_updated = 0
    
    try:
        # Update metadata.frame_details_full
        updates = []
        for frame_id, (folder_name, file_name) in frames_data.items():
            new_reference_id = f"{folder_name}/{file_name}"
            updates.append((new_reference_id, frame_id))
        
        async with conn.transaction():
            result = await conn.executemany("""
                UPDATE metadata.frame_details_full
                SET reference_id = $1
                WHERE frame_id = $2
            """, updates)
            
            frame_count = len(updates)
            logger.info(f"Updated {frame_count} reference IDs in metadata.frame_details_full")
            total_updated += frame_count
            
        # Also update content.frames if it has a reference_id column
        try:
            await conn.execute("SELECT reference_id FROM content.frames LIMIT 1")
            # If we get here, the column exists
            async with conn.transaction():
                result = await conn.executemany("""
                    UPDATE content.frames
                    SET reference_id = $1
                    WHERE frame_id = $2
                """, updates)
                
                logger.info(f"Updated {frame_count} reference IDs in content.frames")
        except Exception as e:
            # Column might not exist
            logger.info("No reference_id column in content.frames, skipping")
        
        return total_updated
    except Exception as e:
        logger.error(f"Error updating frame reference IDs: {str(e)}")
        raise

async def update_chunk_reference_ids(conn, chunks_data, frames_data):
    """
    Update reference IDs for chunks to format 'foldername/filename_ChunkN'.
    Also updates embedding references.
    
    Args:
        conn: Database connection
        chunks_data: Dictionary mapping chunk_id to frame_id
        frames_data: Dictionary mapping frame_id to (folder_name, file_name)
        
    Returns:
        Number of updated records
    """
    total_updated = 0
    
    try:
        # Get existing chunks to determine their chunk numbers
        chunks_by_frame = {}
        for chunk_id, frame_id in chunks_data.items():
            if frame_id not in chunks_by_frame:
                chunks_by_frame[frame_id] = []
            chunks_by_frame[frame_id].append(chunk_id)
        
        # Generate new reference IDs for chunks
        chunk_updates = []
        for frame_id, chunk_ids in chunks_by_frame.items():
            if frame_id not in frames_data:
                logger.warning(f"Frame {frame_id} not found in frames data, skipping")
                continue
                
            folder_name, file_name = frames_data[frame_id]
            frame_path = f"{folder_name}/{file_name}"
            
            # Sort chunks to ensure consistent numbering
            chunk_ids.sort()
            
            for i, chunk_id in enumerate(chunk_ids, 1):
                new_reference_id = f"{frame_path}_Chunk{i}"
                chunk_updates.append((new_reference_id, chunk_id))
        
        # Update metadata.frame_details_chunks
        async with conn.transaction():
            await conn.executemany("""
                UPDATE metadata.frame_details_chunks
                SET reference_id = $1
                WHERE chunk_id = $2
            """, chunk_updates)
            
            logger.info(f"Updated {len(chunk_updates)} reference IDs in metadata.frame_details_chunks")
            total_updated += len(chunk_updates)
        
        # Update embeddings.multimodal_embeddings_chunks
        try:
            async with conn.transaction():
                await conn.executemany("""
                    UPDATE embeddings.multimodal_embeddings_chunks
                    SET reference_id = $1
                    WHERE chunk_id = $2
                """, chunk_updates)
                
                logger.info(f"Updated {len(chunk_updates)} reference IDs in embeddings.multimodal_embeddings_chunks")
                total_updated += len(chunk_updates)
        except Exception as e:
            logger.error(f"Error updating embeddings: {str(e)}")
            # Continue with other updates
        
        return total_updated
    except Exception as e:
        logger.error(f"Error updating chunk reference IDs: {str(e)}")
        raise

async def verify_reference_ids(conn):
    """
    Verify the updated reference IDs follow the correct format.
    
    Args:
        conn: Database connection
    """
    try:
        # Check frame reference IDs
        frame_results = await conn.fetch("""
            SELECT reference_id
            FROM metadata.frame_details_full
            LIMIT 5
        """)
        
        logger.info("Sample frame reference IDs:")
        for row in frame_results:
            logger.info(f"  {row['reference_id']}")
        
        # Check chunk reference IDs
        chunk_results = await conn.fetch("""
            SELECT reference_id
            FROM metadata.frame_details_chunks
            LIMIT 5
        """)
        
        logger.info("Sample chunk reference IDs:")
        for row in chunk_results:
            logger.info(f"  {row['reference_id']}")
        
        # Verify format consistency
        frame_pattern = r'^[^/]+/[^/]+$'
        chunk_pattern = r'^[^/]+/[^/]+_Chunk\d+$'
        
        invalid_frames = await conn.fetchval(f"""
            SELECT COUNT(*)
            FROM metadata.frame_details_full
            WHERE reference_id !~ '{frame_pattern}'
        """)
        
        invalid_chunks = await conn.fetchval(f"""
            SELECT COUNT(*)
            FROM metadata.frame_details_chunks
            WHERE reference_id !~ '{chunk_pattern}'
        """)
        
        if invalid_frames > 0:
            logger.warning(f"Found {invalid_frames} frames with invalid reference ID format")
        else:
            logger.info("✅ All frame reference IDs follow the correct format")
        
        if invalid_chunks > 0:
            logger.warning(f"Found {invalid_chunks} chunks with invalid reference ID format")
        else:
            logger.info("✅ All chunk reference IDs follow the correct format")
            
    except Exception as e:
        logger.error(f"Error verifying reference IDs: {str(e)}")

async def main():
    """Execute the reference ID update process."""
    logger.info("Starting reference ID update process...")
    
    # Create connection pool
    pool = await create_connection_pool()
    
    try:
        async with pool.acquire() as conn:
            # Get frames and chunks data
            frames_data = await get_frames_data(conn)
            chunks_data = await get_chunks_data(conn)
            
            # Update reference IDs
            frames_updated = await update_frame_reference_ids(conn, frames_data)
            chunks_updated = await update_chunk_reference_ids(conn, chunks_data, frames_data)
            
            # Verify updates
            await verify_reference_ids(conn)
            
            logger.info(f"Successfully updated {frames_updated + chunks_updated} reference IDs")
    except Exception as e:
        logger.error(f"Error in update process: {str(e)}")
    finally:
        # Close connection pool
        await pool.close()
        logger.info("PostgreSQL connection pool closed")

if __name__ == "__main__":
    asyncio.run(main()) 