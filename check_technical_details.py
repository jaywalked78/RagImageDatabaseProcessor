#!/usr/bin/env python3
"""
Script to check the technical_details field format in both frames and chunks tables.
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
logger = logging.getLogger("tech_details_check")

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

async def check_column_type(pool, schema, table, column):
    """Check the data type of a column in PostgreSQL."""
    async with pool.acquire() as conn:
        data_type = await conn.fetchval("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_schema = $1 
              AND table_name = $2 
              AND column_name = $3
        """, schema, table, column)
        
        logger.info(f"Column {schema}.{table}.{column} has data type: {data_type}")
        return data_type

async def check_technical_details_frames(pool):
    """Check technical_details in frames table."""
    async with pool.acquire() as conn:
        logger.info("\n=== Technical Details in Frames ===")
        
        # Get a few sample records
        frames = await conn.fetch("""
            SELECT frame_id, technical_details
            FROM metadata.frame_details_full
            ORDER BY frame_id
            LIMIT 5
        """)
        
        logger.info(f"Found {len(frames)} frames with technical_details")
        
        for i, frame in enumerate(frames, 1):
            frame_id = frame["frame_id"]
            tech_details = frame["technical_details"]
            
            logger.info(f"\nFrame {i}: {frame_id}")
            logger.info(f"Python type: {type(tech_details)}")
            
            # Try to extract some key fields to verify it's proper JSON data
            if tech_details:
                if isinstance(tech_details, dict):
                    # It's already a dict object (proper JSONB)
                    logger.info("✅ Database returned a Python dict - correctly working with JSONB!")
                    logger.info(f"Processing version: {tech_details.get('processing_version', 'N/A')}")
                    logger.info(f"Processed timestamp: {tech_details.get('processed_timestamp', 'N/A')}")
                    logger.info(f"Sensitive info detected: {tech_details.get('sensitive_info_detected', 'N/A')}")
                elif isinstance(tech_details, str):
                    # It's a string, try to parse it
                    logger.info("⚠️ Database returned a string, might need to parse JSON")
                    try:
                        parsed = json.loads(tech_details)
                        logger.info("  - String can be parsed as JSON")
                        logger.info(f"  - Processing version: {parsed.get('processing_version', 'N/A')}")
                        logger.info(f"  - Processed timestamp: {parsed.get('processed_timestamp', 'N/A')}")
                    except json.JSONDecodeError:
                        logger.error("❌ String cannot be parsed as valid JSON")
                        logger.info(f"  - Raw value: {tech_details[:100]}...")
                else:
                    # It's some other type
                    logger.info(f"⚠️ Unexpected type: {type(tech_details)}")
                    logger.info(f"  - Raw value: {str(tech_details)[:100]}...")
            else:
                logger.info("❌ technical_details is empty/null")

async def check_technical_details_chunks(pool):
    """Check technical_details in chunks table."""
    async with pool.acquire() as conn:
        logger.info("\n=== Technical Details in Chunks ===")
        
        # Get a few sample records
        chunks = await conn.fetch("""
            SELECT chunk_id, frame_id, technical_details
            FROM metadata.frame_details_chunks
            ORDER BY frame_id
            LIMIT 5
        """)
        
        logger.info(f"Found {len(chunks)} chunks with technical_details")
        
        for i, chunk in enumerate(chunks, 1):
            chunk_id = chunk["chunk_id"]
            frame_id = chunk["frame_id"]
            tech_details = chunk["technical_details"]
            
            logger.info(f"\nChunk {i}: {chunk_id} (Frame: {frame_id})")
            logger.info(f"Python type: {type(tech_details)}")
            
            # Try to extract some key fields to verify it's proper JSON data
            if tech_details:
                if isinstance(tech_details, dict):
                    # It's already a dict object (proper JSONB)
                    logger.info("✅ Database returned a Python dict - correctly working with JSONB!")
                    logger.info(f"Processing version: {tech_details.get('processing_version', 'N/A')}")
                    logger.info(f"Processed timestamp: {tech_details.get('processed_timestamp', 'N/A')}")
                    logger.info(f"Parent frame ID: {tech_details.get('parent_frame_id', 'N/A')}")
                elif isinstance(tech_details, str):
                    # It's a string, try to parse it
                    logger.info("⚠️ Database returned a string, might need to parse JSON")
                    try:
                        parsed = json.loads(tech_details)
                        logger.info("  - String can be parsed as JSON")
                        logger.info(f"  - Processing version: {parsed.get('processing_version', 'N/A')}")
                        logger.info(f"  - Parent frame ID: {parsed.get('parent_frame_id', 'N/A')}")
                    except json.JSONDecodeError:
                        logger.error("❌ String cannot be parsed as valid JSON")
                        logger.info(f"  - Raw value: {tech_details[:100]}...")
                else:
                    # It's some other type
                    logger.info(f"⚠️ Unexpected type: {type(tech_details)}")
                    logger.info(f"  - Raw value: {str(tech_details)[:100]}...")
            else:
                logger.info("❌ technical_details is empty/null")

async def test_jsonb_query(pool):
    """Test querying JSONB fields."""
    async with pool.acquire() as conn:
        logger.info("\n=== Testing JSONB Queries ===")
        
        # Test query with ? operator (exists)
        frames_with_processing_version = await conn.fetchval("""
            SELECT COUNT(*)
            FROM metadata.frame_details_full
            WHERE technical_details ? 'processing_version'
        """)
        
        logger.info(f"Frames with processing_version key: {frames_with_processing_version}")
        
        # Test query with direct value comparison
        frames_with_sensitive_info = await conn.fetchval("""
            SELECT COUNT(*)
            FROM metadata.frame_details_full
            WHERE technical_details->>'sensitive_info_detected' = 'true'
        """)
        
        logger.info(f"Frames with sensitive info detected: {frames_with_sensitive_info}")
        
        # Test querying nested values
        chunks_with_parent_frame = await conn.fetchval("""
            SELECT COUNT(*)
            FROM metadata.frame_details_chunks
            WHERE technical_details ? 'parent_frame_id'
        """)
        
        logger.info(f"Chunks with parent_frame_id key: {chunks_with_parent_frame}")
        
        # Return success if JSONB queries work
        return frames_with_processing_version > 0

async def main():
    """Main function."""
    logger.info("Starting technical_details field format check...")
    
    try:
        # Create connection pool
        pool = await create_connection_pool()
        
        # Check column types
        frames_type = await check_column_type(pool, 'metadata', 'frame_details_full', 'technical_details')
        chunks_type = await check_column_type(pool, 'metadata', 'frame_details_chunks', 'technical_details')
        
        is_jsonb = frames_type == 'jsonb' and chunks_type == 'jsonb'
        logger.info(f"Both technical_details columns have JSONB type: {is_jsonb}")
        
        # Check actual values
        await check_technical_details_frames(pool)
        await check_technical_details_chunks(pool)
        
        # Test JSONB queries
        queries_work = await test_jsonb_query(pool)
        
        # Final assessment
        success = is_jsonb and queries_work
        logger.info("\nSummary:")
        logger.info(f"  - Columns have JSONB type: {is_jsonb}")
        logger.info(f"  - JSONB queries work: {queries_work}")
        logger.info(f"  - Overall assessment: {'✅ Successfully using JSONB' if success else '❌ Problems with JSONB'}")
        
        # Close the connection pool
        await pool.close()
        logger.info("Check completed. PostgreSQL connection pool closed.")
        
        return success
        
    except Exception as e:
        logger.error(f"Error during check: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 