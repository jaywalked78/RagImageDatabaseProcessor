#!/usr/bin/env python3
"""
Fix remaining reference IDs in embeddings.multimodal_embeddings_chunks that still use the old format.
This script ensures all embedding references use the standardized 'foldername/filename_ChunkN' format.
"""

import os
import sys
import logging
import asyncio
from dotenv import load_dotenv
import asyncpg
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("fix_embeddings")

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

async def get_all_embeddings(conn):
    """
    Get all embeddings to identify those with invalid reference IDs.
    
    Args:
        conn: Database connection
    """
    # Get all embeddings
    all_embeddings = await conn.fetch("""
        SELECT e.embedding_id, e.chunk_id, e.reference_id 
        FROM embeddings.multimodal_embeddings_chunks e
    """)
    
    # Identify simple frame pattern (e.g., 'frame_000006.jpg')
    simple_frame_pattern = re.compile(r'^frame_\d+\.jpg$')
    frame_ids = []
    
    invalid_embeddings = []
    for row in all_embeddings:
        ref_id = row['reference_id']
        if ref_id and simple_frame_pattern.match(ref_id):
            invalid_embeddings.append(row)
            logger.info(f"Found invalid embedding: {row['embedding_id']} with reference_id '{ref_id}'")
    
    logger.info(f"Manually identified {len(invalid_embeddings)} embeddings with old format reference IDs")
    return invalid_embeddings

async def update_embedding_references(conn, invalid_embeddings):
    """
    Update reference IDs for invalid embeddings.
    
    Args:
        conn: Database connection
        invalid_embeddings: List of embeddings with invalid reference IDs
        
    Returns:
        Number of updated records
    """
    if not invalid_embeddings:
        return 0
    
    # Get the folder name from content.frames
    folder_name = await conn.fetchval("""
        SELECT folder_name FROM content.frames LIMIT 1
    """)
    
    if not folder_name:
        logger.error("Could not determine folder name from content.frames")
        return 0
    
    logger.info(f"Using folder name: {folder_name}")
    
    # Update each embedding
    updated_count = 0
    for row in invalid_embeddings:
        embedding_id = row['embedding_id']
        chunk_id = row['chunk_id']
        old_ref = row['reference_id']
        
        # Try to get the correct reference ID from metadata.frame_details_chunks
        new_ref = await conn.fetchval("""
            SELECT reference_id 
            FROM metadata.frame_details_chunks 
            WHERE chunk_id = $1
        """, chunk_id)
        
        if not new_ref:
            # Fall back to constructing a new reference ID
            frame_id = old_ref  # frame_000XXX.jpg
            new_ref = f"{folder_name}/{frame_id}_Chunk1"
        
        # Execute the update
        await conn.execute("""
            UPDATE embeddings.multimodal_embeddings_chunks
            SET reference_id = $1
            WHERE embedding_id = $2
        """, new_ref, embedding_id)
        
        logger.info(f"Updated embedding {embedding_id}: '{old_ref}' -> '{new_ref}'")
        updated_count += 1
    
    return updated_count

async def verify_references(conn):
    """
    Verify all embeddings now have the correct reference ID format.
    
    Args:
        conn: Database connection
    """
    # Count embeddings with incorrect format
    remaining_incorrect = await conn.fetchval("""
        SELECT COUNT(*)
        FROM embeddings.multimodal_embeddings_chunks
        WHERE reference_id !~ '^[^/]+/[^/]+_Chunk\d+$' OR reference_id IS NULL
    """)
    
    if remaining_incorrect > 0:
        logger.warning(f"There are still {remaining_incorrect} embeddings with incorrect reference ID format")
    else:
        logger.info("✅ All embeddings now have the correct reference ID format")
    
    # Verify consistency with chunk references
    inconsistent_refs = await conn.fetch("""
        SELECT e.embedding_id, e.chunk_id, e.reference_id as emb_ref, c.reference_id as chunk_ref
        FROM embeddings.multimodal_embeddings_chunks e
        JOIN metadata.frame_details_chunks c ON e.chunk_id = c.chunk_id
        WHERE e.reference_id != c.reference_id
        LIMIT 5
    """)
    
    if inconsistent_refs:
        logger.warning(f"Found {len(inconsistent_refs)} embeddings with reference IDs inconsistent with their chunks")
        for row in inconsistent_refs:
            logger.warning(f"  Embedding {row['embedding_id']} (Chunk {row['chunk_id']}):")
            logger.warning(f"    Embedding reference: {row['emb_ref']}")
            logger.warning(f"    Chunk reference: {row['chunk_ref']}")
    else:
        logger.info("✅ All embedding reference IDs match their corresponding chunk reference IDs")

async def main():
    """Execute the reference ID fix process."""
    logger.info("Starting to fix embedding reference IDs...")
    
    # Create connection pool
    pool = await create_connection_pool()
    
    try:
        async with pool.acquire() as conn:
            # Get all embeddings and identify those with invalid reference IDs
            invalid_embeddings = await get_all_embeddings(conn)
            
            if invalid_embeddings:
                # Update embedding references
                updated_count = await update_embedding_references(conn, invalid_embeddings)
                logger.info(f"Updated {updated_count} embedding reference IDs")
                
                # Verify all references are now correct
                await verify_references(conn)
            else:
                logger.info("No embedding reference IDs to update")
                
            logger.info("Reference ID fix process complete")
    except Exception as e:
        logger.error(f"Error in fix process: {str(e)}")
    finally:
        # Close connection pool
        await pool.close()
        logger.info("PostgreSQL connection pool closed")

if __name__ == "__main__":
    asyncio.run(main()) 