#!/usr/bin/env python3
"""
Script to verify that technical_details is correctly stored in JSONB format
in both frames and chunks tables.
"""

import os
import sys
import logging
import asyncio
import json
from dotenv import load_dotenv
import asyncpg
from tabulate import tabulate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("jsonb_verifier")

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

async def verify_jsonb_in_frames(pool):
    """Verify that technical_details in frames table is JSONB format."""
    async with pool.acquire() as conn:
        logger.info("Verifying JSONB format in metadata.frame_details_full table...")
        
        # Check technical_details column type
        column_type = await conn.fetchval("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'metadata' 
            AND table_name = 'frame_details_full' 
            AND column_name = 'technical_details'
        """)
        
        logger.info(f"Column type for technical_details in frames: {column_type}")
        
        # Get some sample data
        frames = await conn.fetch("""
            SELECT frame_id, technical_details
            FROM metadata.frame_details_full
            LIMIT 3
        """)
        
        # Display sample data
        for frame in frames:
            logger.info(f"Frame {frame['frame_id']} technical_details:")
            
            # Check if it's a proper JSON object
            td = frame['technical_details']
            logger.info(f"  Type in Python: {type(td)}")
            
            # Display some keys
            if isinstance(td, dict):
                logger.info(f"  Keys: {', '.join(td.keys())}")
                # Test JSONB query capability
                logger.info(f"  processing_version: {td.get('processing_version', 'N/A')}")
            else:
                logger.info(f"  Value: {str(td)[:100]}...")
        
        # Test JSONB query capability
        count = await conn.fetchval("""
            SELECT COUNT(*)
            FROM metadata.frame_details_full
            WHERE technical_details ? 'processing_version'
        """)
        
        logger.info(f"Frames with processing_version key: {count}")
        
        # Return success if column type is jsonb and we can query JSONB properties
        return column_type == 'jsonb' and count > 0

async def verify_jsonb_in_chunks(pool):
    """Verify that technical_details in chunks table is JSONB format."""
    async with pool.acquire() as conn:
        logger.info("\nVerifying JSONB format in metadata.frame_details_chunks table...")
        
        # Check technical_details column type
        column_type = await conn.fetchval("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'metadata' 
            AND table_name = 'frame_details_chunks' 
            AND column_name = 'technical_details'
        """)
        
        logger.info(f"Column type for technical_details in chunks: {column_type}")
        
        # Get some sample data
        chunks = await conn.fetch("""
            SELECT chunk_id, technical_details
            FROM metadata.frame_details_chunks
            LIMIT 3
        """)
        
        # Display sample data
        for chunk in chunks:
            logger.info(f"Chunk {chunk['chunk_id']} technical_details:")
            
            # Check if it's a proper JSON object
            td = chunk['technical_details']
            logger.info(f"  Type in Python: {type(td)}")
            
            # Display some keys
            if isinstance(td, dict):
                logger.info(f"  Keys: {', '.join(td.keys())}")
                # Test JSONB query capability
                logger.info(f"  processing_version: {td.get('processing_version', 'N/A')}")
            else:
                logger.info(f"  Value: {str(td)[:100]}...")
        
        # Test JSONB query capability
        count = await conn.fetchval("""
            SELECT COUNT(*)
            FROM metadata.frame_details_chunks
            WHERE technical_details ? 'parent_frame_id'
        """)
        
        logger.info(f"Chunks with parent_frame_id key: {count}")
        
        # Return success if column type is jsonb and we can query JSONB properties
        return column_type == 'jsonb' and count > 0

async def main():
    """Main function."""
    logger.info("Starting JSONB format verification...")
    
    try:
        # Create connection pool
        pool = await create_connection_pool()
        
        # Verify JSONB in frames table
        frames_result = await verify_jsonb_in_frames(pool)
        
        # Verify JSONB in chunks table
        chunks_result = await verify_jsonb_in_chunks(pool)
        
        # Summary
        logger.info("\nVerification Summary:")
        logger.info(f"  - Frames technical_details is JSONB: {frames_result}")
        logger.info(f"  - Chunks technical_details is JSONB: {chunks_result}")
        
        overall_result = frames_result and chunks_result
        logger.info(f"  - Overall result: {'SUCCESS' if overall_result else 'FAILURE'}")
        
        # Close the connection pool
        await pool.close()
        logger.info("\nJSONB verification complete")
        logger.info("PostgreSQL connection pool closed")
        
        return overall_result
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1) 