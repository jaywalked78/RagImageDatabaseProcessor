#!/usr/bin/env python3
"""
Check reference IDs across all database tables to verify they follow the correct format:
- Frames: foldername/filename
- Chunks: foldername/filename_ChunkN
"""

import os
import sys
import logging
import asyncio
from typing import List, Dict, Any
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
logger = logging.getLogger("check_refids")

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
        logger.info(f"Connected to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}")
        return pool
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
        sys.exit(1)

async def check_frame_reference_ids(conn):
    """
    Check reference IDs in metadata.frame_details_full.
    
    Args:
        conn: Database connection
    
    Returns:
        Tuple of (valid_count, invalid_count, sample_valid, sample_invalid)
    """
    # Expected format for frames: foldername/filename
    frame_pattern = r'^[^/]+/[^/]+$'
    
    # Get total count
    total_count = await conn.fetchval("""
        SELECT COUNT(*) FROM metadata.frame_details_full
    """)
    
    # Get count of valid reference IDs
    valid_count = await conn.fetchval(f"""
        SELECT COUNT(*) 
        FROM metadata.frame_details_full
        WHERE reference_id ~ '{frame_pattern}'
    """)
    
    # Get count of invalid reference IDs
    invalid_count = total_count - valid_count
    
    # Get sample of valid reference IDs
    valid_samples = await conn.fetch(f"""
        SELECT frame_id, reference_id
        FROM metadata.frame_details_full
        WHERE reference_id ~ '{frame_pattern}'
        LIMIT 5
    """)
    
    # Get sample of invalid reference IDs
    invalid_samples = await conn.fetch(f"""
        SELECT frame_id, reference_id
        FROM metadata.frame_details_full
        WHERE reference_id !~ '{frame_pattern}' OR reference_id IS NULL
        LIMIT 5
    """)
    
    return (valid_count, invalid_count, valid_samples, invalid_samples)

async def check_chunk_reference_ids(conn):
    """
    Check reference IDs in metadata.frame_details_chunks.
    
    Args:
        conn: Database connection
    
    Returns:
        Tuple of (valid_count, invalid_count, sample_valid, sample_invalid)
    """
    # Expected format for chunks: foldername/filename_ChunkN
    chunk_pattern = r'^[^/]+/[^/]+_Chunk\d+$'
    
    # Get total count
    total_count = await conn.fetchval("""
        SELECT COUNT(*) FROM metadata.frame_details_chunks
    """)
    
    # Get count of valid reference IDs
    valid_count = await conn.fetchval(f"""
        SELECT COUNT(*) 
        FROM metadata.frame_details_chunks
        WHERE reference_id ~ '{chunk_pattern}'
    """)
    
    # Get count of invalid reference IDs
    invalid_count = total_count - valid_count
    
    # Get sample of valid reference IDs
    valid_samples = await conn.fetch(f"""
        SELECT chunk_id, frame_id, reference_id
        FROM metadata.frame_details_chunks
        WHERE reference_id ~ '{chunk_pattern}'
        LIMIT 5
    """)
    
    # Get sample of invalid reference IDs
    invalid_samples = await conn.fetch(f"""
        SELECT chunk_id, frame_id, reference_id
        FROM metadata.frame_details_chunks
        WHERE reference_id !~ '{chunk_pattern}' OR reference_id IS NULL
        LIMIT 5
    """)
    
    return (valid_count, invalid_count, valid_samples, invalid_samples)

async def check_embeddings_reference_ids(conn):
    """
    Check reference IDs in embeddings.multimodal_embeddings_chunks.
    
    Args:
        conn: Database connection
    
    Returns:
        Tuple of (valid_count, invalid_count, sample_valid, sample_invalid)
    """
    # Expected format for chunks in embeddings: foldername/filename_ChunkN
    chunk_pattern = r'^[^/]+/[^/]+_Chunk\d+$'
    
    # Get total count
    total_count = await conn.fetchval("""
        SELECT COUNT(*) FROM embeddings.multimodal_embeddings_chunks
    """)
    
    # Get count of valid reference IDs
    valid_count = await conn.fetchval(f"""
        SELECT COUNT(*) 
        FROM embeddings.multimodal_embeddings_chunks
        WHERE reference_id ~ '{chunk_pattern}'
    """)
    
    # Get count of invalid reference IDs
    invalid_count = total_count - valid_count
    
    # Get sample of valid reference IDs
    valid_samples = await conn.fetch(f"""
        SELECT embedding_id, chunk_id, reference_id
        FROM embeddings.multimodal_embeddings_chunks
        WHERE reference_id ~ '{chunk_pattern}'
        LIMIT 5
    """)
    
    # Get sample of invalid reference IDs
    invalid_samples = await conn.fetch(f"""
        SELECT embedding_id, chunk_id, reference_id
        FROM embeddings.multimodal_embeddings_chunks
        WHERE reference_id !~ '{chunk_pattern}' OR reference_id IS NULL
        LIMIT 5
    """)
    
    return (valid_count, invalid_count, valid_samples, invalid_samples)

async def check_consistency_across_tables(conn):
    """
    Check that reference IDs are consistent across related tables.
    
    Args:
        conn: Database connection
    """
    # Check that chunk reference IDs in frame_details_chunks match those in embeddings table
    inconsistent_chunks = await conn.fetch("""
        SELECT c.chunk_id, c.reference_id as chunks_ref, e.reference_id as embeddings_ref
        FROM metadata.frame_details_chunks c
        JOIN embeddings.multimodal_embeddings_chunks e ON c.chunk_id = e.chunk_id
        WHERE c.reference_id != e.reference_id
        LIMIT 10
    """)
    
    if inconsistent_chunks:
        logger.warning(f"Found {len(inconsistent_chunks)} chunks with inconsistent reference IDs across tables:")
        for row in inconsistent_chunks:
            logger.warning(f"  Chunk {row['chunk_id']}:")
            logger.warning(f"    metadata.frame_details_chunks: {row['chunks_ref']}")
            logger.warning(f"    embeddings.multimodal_embeddings_chunks: {row['embeddings_ref']}")
    else:
        logger.info("✅ All chunk reference IDs are consistent across tables")
    
    # Check that frame reference IDs in frame_details_chunks match the pattern based on frame_id
    inconsistent_frames = await conn.fetch("""
        SELECT c.frame_id, c.reference_id, 
               SUBSTR(c.reference_id, 1, POSITION('_Chunk' IN c.reference_id) - 1) as expected_frame_ref,
               f.reference_id as actual_frame_ref
        FROM metadata.frame_details_chunks c
        JOIN metadata.frame_details_full f ON c.frame_id = f.frame_id
        WHERE POSITION('_Chunk' IN c.reference_id) > 0
          AND SUBSTR(c.reference_id, 1, POSITION('_Chunk' IN c.reference_id) - 1) != f.reference_id
        LIMIT 10
    """)
    
    if inconsistent_frames:
        logger.warning(f"Found {len(inconsistent_frames)} chunks with inconsistent reference ID prefixes:")
        for row in inconsistent_frames:
            logger.warning(f"  Frame {row['frame_id']}:")
            logger.warning(f"    Expected frame reference: {row['expected_frame_ref']}")
            logger.warning(f"    Actual frame reference: {row['actual_frame_ref']}")
    else:
        logger.info("✅ All chunk reference ID prefixes match their parent frame reference IDs")

async def main():
    """Main function to execute the reference ID checks."""
    logger.info("Starting reference ID verification...")
    
    # Create connection pool
    pool = await create_connection_pool()
    
    try:
        async with pool.acquire() as conn:
            # Check frame reference IDs
            logger.info("\n--- Checking Frame Reference IDs ---")
            frame_results = await check_frame_reference_ids(conn)
            valid_count, invalid_count, valid_samples, invalid_samples = frame_results
            
            logger.info(f"Frame reference IDs: {valid_count} valid, {invalid_count} invalid")
            
            if valid_samples:
                logger.info("Sample valid frame reference IDs:")
                for row in valid_samples:
                    logger.info(f"  Frame {row['frame_id']}: {row['reference_id']}")
                    
            if invalid_samples:
                logger.warning("Sample invalid frame reference IDs:")
                for row in invalid_samples:
                    logger.warning(f"  Frame {row['frame_id']}: {row['reference_id']}")
            
            # Check chunk reference IDs
            logger.info("\n--- Checking Chunk Reference IDs ---")
            chunk_results = await check_chunk_reference_ids(conn)
            valid_count, invalid_count, valid_samples, invalid_samples = chunk_results
            
            logger.info(f"Chunk reference IDs: {valid_count} valid, {invalid_count} invalid")
            
            if valid_samples:
                logger.info("Sample valid chunk reference IDs:")
                for row in valid_samples:
                    logger.info(f"  Chunk {row['chunk_id']} (Frame {row['frame_id']}): {row['reference_id']}")
                    
            if invalid_samples:
                logger.warning("Sample invalid chunk reference IDs:")
                for row in invalid_samples:
                    logger.warning(f"  Chunk {row['chunk_id']} (Frame {row['frame_id']}): {row['reference_id']}")
            
            # Check embeddings reference IDs
            logger.info("\n--- Checking Embeddings Reference IDs ---")
            emb_results = await check_embeddings_reference_ids(conn)
            valid_count, invalid_count, valid_samples, invalid_samples = emb_results
            
            logger.info(f"Embeddings reference IDs: {valid_count} valid, {invalid_count} invalid")
            
            if valid_samples:
                logger.info("Sample valid embeddings reference IDs:")
                for row in valid_samples:
                    logger.info(f"  Embedding {row['embedding_id']} (Chunk {row['chunk_id']}): {row['reference_id']}")
                    
            if invalid_samples:
                logger.warning("Sample invalid embeddings reference IDs:")
                for row in invalid_samples:
                    logger.warning(f"  Embedding {row['embedding_id']} (Chunk {row['chunk_id']}): {row['reference_id']}")
            
            # Check consistency across tables
            logger.info("\n--- Checking Reference ID Consistency Across Tables ---")
            await check_consistency_across_tables(conn)
            
            logger.info("\nReference ID verification complete")
    except Exception as e:
        logger.error(f"Error in verification process: {str(e)}")
    finally:
        # Close connection pool
        await pool.close()
        logger.info("PostgreSQL connection pool closed")

if __name__ == "__main__":
    asyncio.run(main()) 