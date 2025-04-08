#!/usr/bin/env python3
"""
Check the database schema for tables in Supabase.
"""

import os
import sys
import logging
import asyncio
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
logger = logging.getLogger("check_schema")

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

async def check_table_schema(conn, schema, table):
    """
    Check the schema for a specific table.
    
    Args:
        conn: Database connection
        schema: Schema name
        table: Table name
    """
    logger.info(f"Checking schema for {schema}.{table}")
    
    # Get column information
    columns = await conn.fetch("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = $1 AND table_name = $2
        ORDER BY ordinal_position
    """, schema, table)
    
    if not columns:
        logger.warning(f"No columns found for {schema}.{table}")
        return
    
    logger.info(f"Found {len(columns)} columns in {schema}.{table}:")
    for col in columns:
        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
        logger.info(f"  {col['column_name']} ({col['data_type']}, {nullable})")

async def main():
    """Check the schema for relevant tables."""
    logger.info("Starting schema check...")
    
    # Create connection pool
    pool = await create_connection_pool()
    
    try:
        async with pool.acquire() as conn:
            # Check content.frames
            await check_table_schema(conn, 'content', 'frames')
            
            # Check metadata tables
            await check_table_schema(conn, 'metadata', 'frame_details_full')
            await check_table_schema(conn, 'metadata', 'frame_details_chunks')
            await check_table_schema(conn, 'metadata', 'process_frames_chunks')
            
            # Check embeddings tables
            await check_table_schema(conn, 'embeddings', 'multimodal_embeddings')
            await check_table_schema(conn, 'embeddings', 'multimodal_embeddings_chunks')
            
            logger.info("Schema check complete")
    except Exception as e:
        logger.error(f"Error in schema check: {str(e)}")
    finally:
        # Close connection pool
        await pool.close()
        logger.info("PostgreSQL connection pool closed")

if __name__ == "__main__":
    asyncio.run(main()) 