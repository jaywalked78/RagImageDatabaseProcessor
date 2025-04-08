#!/usr/bin/env python3
"""
Script to verify the reference_id format in all tables.
"""

import os
import asyncio
import logging
import asyncpg
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path setup
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Import environment variables
try:
    if Path(project_root / '.env').exists():
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

async def verify_reference_ids(conn):
    """Verify reference_id format in all tables."""
    try:
        # Check for the tables
        tables = [
            "metadata.frame_details_full",
            "metadata.frame_details_chunk",
            "embeddings.multimodal_embeddings"
        ]
        
        for table in tables:
            logger.info(f"\n=== Checking {table} ===")
            
            # Check if table exists
            exists = await conn.fetchval(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = $1 AND table_name = $2
            )
            """, table.split('.')[0], table.split('.')[1])
            
            if not exists:
                logger.warning(f"Table {table} does not exist")
                continue
            
            # Count total rows
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            logger.info(f"Total rows in {table}: {count}")
            
            # Check reference_id format
            if count > 0:
                # Get 5 example reference_ids
                rows = await conn.fetch(f"SELECT reference_id FROM {table} LIMIT 5")
                logger.info(f"Reference_id examples from {table}:")
                for i, row in enumerate(rows):
                    logger.info(f"  {i+1}. {row['reference_id']}")
                
                # Count reference_ids with slashes (for folder/frame format)
                slash_count = await conn.fetchval(f"""
                SELECT COUNT(*) FROM {table} WHERE reference_id LIKE '%/%'
                """)
                logger.info(f"Reference_ids with folder/frame format: {slash_count} ({slash_count/count*100:.1f}%)")
                
                # For multimodal_embeddings, check by reference_type
                if table == "embeddings.multimodal_embeddings":
                    # Count by reference_type
                    type_counts = await conn.fetch("""
                    SELECT reference_type, COUNT(*) 
                    FROM embeddings.multimodal_embeddings 
                    GROUP BY reference_type
                    """)
                    logger.info("Counts by reference_type:")
                    for row in type_counts:
                        logger.info(f"  {row['reference_type']}: {row['count']}")
                    
                    # Check frame references
                    frame_refs = await conn.fetch("""
                    SELECT reference_id FROM embeddings.multimodal_embeddings
                    WHERE reference_type = 'frame'
                    LIMIT 5
                    """)
                    logger.info("Frame reference_id examples:")
                    for i, row in enumerate(frame_refs):
                        logger.info(f"  {i+1}. {row['reference_id']}")
                    
                    # Check chunk references
                    chunk_refs = await conn.fetch("""
                    SELECT reference_id FROM embeddings.multimodal_embeddings
                    WHERE reference_type = 'chunk'
                    LIMIT 5
                    """)
                    logger.info("Chunk reference_id examples:")
                    for i, row in enumerate(chunk_refs):
                        logger.info(f"  {i+1}. {row['reference_id']}")
                
                # For frame_details_chunk, check if they contain "chunk_"
                if table == "metadata.frame_details_chunk":
                    chunk_format_count = await conn.fetchval(f"""
                    SELECT COUNT(*) FROM {table} WHERE reference_id LIKE '%/chunk_%'
                    """)
                    logger.info(f"Reference_ids with proper chunk format: {chunk_format_count} ({chunk_format_count/count*100:.1f}%)")
        
        return True
    except Exception as e:
        logger.error(f"Error verifying reference_ids: {e}")
        return False

async def verify_frame_chunk_references(conn):
    """Verify that frame and chunk references match between tables."""
    try:
        logger.info("\n=== Checking reference consistency across tables ===")
        
        # Check if frame reference_ids in frame_details_full match those in multimodal_embeddings
        frame_match_count = await conn.fetchval("""
        SELECT COUNT(*)
        FROM metadata.frame_details_full fdf
        JOIN embeddings.multimodal_embeddings emm
            ON fdf.reference_id = emm.reference_id
        WHERE emm.reference_type = 'frame'
        """)
        
        total_frames_in_multimodal = await conn.fetchval("""
        SELECT COUNT(*) FROM embeddings.multimodal_embeddings
        WHERE reference_type = 'frame'
        """)
        
        total_frames_in_details = await conn.fetchval("""
        SELECT COUNT(*) FROM metadata.frame_details_full
        """)
        
        logger.info(f"Frame references that match between tables: {frame_match_count}")
        logger.info(f"Total frames in multimodal_embeddings: {total_frames_in_multimodal}")
        logger.info(f"Total frames in frame_details_full: {total_frames_in_details}")
        
        if total_frames_in_multimodal > 0:
            match_percentage = (frame_match_count / total_frames_in_multimodal) * 100
            logger.info(f"Match percentage: {match_percentage:.1f}%")
        
        # Check if chunk reference_ids in frame_details_chunk match those in multimodal_embeddings
        chunk_match_count = await conn.fetchval("""
        SELECT COUNT(*)
        FROM metadata.frame_details_chunk fdc
        JOIN embeddings.multimodal_embeddings emm
            ON fdc.reference_id = emm.reference_id
        WHERE emm.reference_type = 'chunk'
        """)
        
        total_chunks_in_multimodal = await conn.fetchval("""
        SELECT COUNT(*) FROM embeddings.multimodal_embeddings
        WHERE reference_type = 'chunk'
        """)
        
        total_chunks_in_details = await conn.fetchval("""
        SELECT COUNT(*) FROM metadata.frame_details_chunk
        """)
        
        logger.info(f"Chunk references that match between tables: {chunk_match_count}")
        logger.info(f"Total chunks in multimodal_embeddings: {total_chunks_in_multimodal}")
        logger.info(f"Total chunks in frame_details_chunk: {total_chunks_in_details}")
        
        if total_chunks_in_multimodal > 0:
            match_percentage = (chunk_match_count / total_chunks_in_multimodal) * 100
            logger.info(f"Match percentage: {match_percentage:.1f}%")
        
        return True
    except Exception as e:
        logger.error(f"Error verifying reference consistency: {e}")
        return False

async def main():
    """Main function to verify reference_ids."""
    logger.info("Starting reference_id verification")
    
    # Get database connection
    conn = await get_connection()
    if not conn:
        logger.error("Could not connect to database. Verification aborted.")
        return
    
    try:
        # Verify reference_ids in all tables
        await verify_reference_ids(conn)
        
        # Verify cross-table reference consistency
        await verify_frame_chunk_references(conn)
        
        logger.info("Reference_id verification completed")
    
    except Exception as e:
        logger.error(f"Error during verification process: {e}")
    
    finally:
        # Close connection
        await conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    asyncio.run(main()) 