#!/usr/bin/env python3
"""
Fix the schema of metadata.frame_details_chunks table by adding missing columns.

This script adds created_at and updated_at columns if they don't exist.
"""

import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
import asyncpg

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('schema_fix')

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-us-east-1.pooler.supabase.com')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')

async def create_pool():
    """Create a connection pool to PostgreSQL database."""
    try:
        pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            min_size=1,
            max_size=5
        )
        logger.info(f"Successfully connected to PostgreSQL at {DB_HOST}:{DB_PORT}")
        return pool
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        sys.exit(1)

async def check_column_exists(pool, table_name, schema_name, column_name):
    """Check if a column exists in a table."""
    query = """
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_schema = $1 
    AND table_name = $2 
    AND column_name = $3
    """
    
    async with pool.acquire() as conn:
        result = await conn.fetchval(query, schema_name, table_name, column_name)
        return result is not None

async def add_column(pool, table_name, schema_name, column_name, column_type):
    """Add a column to a table if it doesn't exist."""
    column_exists = await check_column_exists(pool, table_name, schema_name, column_name)
    
    if not column_exists:
        query = f"""
        ALTER TABLE {schema_name}.{table_name}
        ADD COLUMN {column_name} {column_type}
        """
        
        async with pool.acquire() as conn:
            try:
                await conn.execute(query)
                logger.info(f"Successfully added column {column_name} to {schema_name}.{table_name}")
                return True
            except Exception as e:
                logger.error(f"Error adding column {column_name} to {schema_name}.{table_name}: {e}")
                return False
    else:
        logger.info(f"Column {column_name} already exists in {schema_name}.{table_name}")
        return True

async def update_existing_rows(pool, table_name, schema_name):
    """Update existing rows to set created_at and updated_at values if they're NULL."""
    query = f"""
    UPDATE {schema_name}.{table_name}
    SET created_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
    WHERE created_at IS NULL OR updated_at IS NULL
    """
    
    async with pool.acquire() as conn:
        try:
            result = await conn.execute(query)
            logger.info(f"Updated timestamps for existing rows in {schema_name}.{table_name}: {result}")
            return True
        except Exception as e:
            logger.error(f"Error updating timestamps in {schema_name}.{table_name}: {e}")
            return False

async def fix_schema():
    """Fix the schema by adding missing columns."""
    pool = await create_pool()
    
    try:
        # Check and add created_at column
        await add_column(pool, 'frame_details_chunks', 'metadata', 'created_at', 'TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP')
        
        # Check and add updated_at column
        await add_column(pool, 'frame_details_chunks', 'metadata', 'updated_at', 'TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP')
        
        # Update existing rows
        await update_existing_rows(pool, 'frame_details_chunks', 'metadata')
        
        logger.info("Schema fix completed successfully")
        
    except Exception as e:
        logger.error(f"An error occurred while fixing schema: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        await pool.close()
        logger.info("PostgreSQL connection pool closed")

if __name__ == "__main__":
    asyncio.run(fix_schema()) 