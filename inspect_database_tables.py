#!/usr/bin/env python3
"""
Inspect all columns in the database tables for migration purposes.
This script retrieves the complete schema information for all tables
that need to be migrated.
"""

import os
import sys
import logging
import asyncio
import json
from dotenv import load_dotenv
import asyncpg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('db_inspector')

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-us-east-1.pooler.supabase.com')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')

# Verify environment variables
if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    logger.error("Missing database connection parameters. Please check your .env file.")
    sys.exit(1)

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

async def inspect_table_schema(pool, schema, table):
    """Inspect the schema of a specific table."""
    async with pool.acquire() as conn:
        # Get column information
        columns = await conn.fetch('''
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = $1 AND table_name = $2
            ORDER BY ordinal_position
        ''', schema, table)

        # Get primary key information
        primary_keys = await conn.fetch('''
            SELECT c.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
            JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
                AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
            WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = $1 AND tc.table_name = $2
        ''', schema, table)

        pk_columns = [pk['column_name'] for pk in primary_keys]
        
        logger.info(f"\n=== {schema}.{table} Schema ===")
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f"DEFAULT {col['column_default']}" if col['column_default'] else ""
            pk = "PRIMARY KEY" if col['column_name'] in pk_columns else ""
            logger.info(f"  {col['column_name']}: {col['data_type']} {nullable} {default} {pk}".strip())
        
        return columns

async def sample_table_data(pool, schema, table, limit=3):
    """Get sample data from a table."""
    async with pool.acquire() as conn:
        try:
            # First check if table exists and has data
            count = await conn.fetchval(f'SELECT COUNT(*) FROM {schema}.{table}')
            
            if count == 0:
                logger.info(f"\n=== {schema}.{table} Sample Data ===")
                logger.info("  Table is empty")
                return
            
            # Get column names
            columns = await conn.fetch('''
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = $1 AND table_name = $2
                ORDER BY ordinal_position
            ''', schema, table)
            
            column_names = [col['column_name'] for col in columns]
            
            # Select sample data
            sample_data = await conn.fetch(f'SELECT * FROM {schema}.{table} LIMIT {limit}')
            
            logger.info(f"\n=== {schema}.{table} Sample Data ({min(count, limit)} of {count} rows) ===")
            
            # Display sample data in a readable format
            for i, row in enumerate(sample_data):
                logger.info(f"  Row {i+1}:")
                for col in column_names:
                    # Truncate long values for better display
                    value = row[col]
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:97] + '...'
                    elif isinstance(value, (list, dict)):
                        value = json.dumps(value)[:97] + '...' if len(json.dumps(value)) > 100 else json.dumps(value)
                    logger.info(f"    {col}: {value}")
        
        except Exception as e:
            logger.error(f"Error sampling data from {schema}.{table}: {str(e)}")

async def check_table_exists(pool, schema, table):
    """Check if a table exists."""
    async with pool.acquire() as conn:
        exists = await conn.fetchval('''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = $1 AND table_name = $2
            )
        ''', schema, table)
        return exists

async def inspect_database():
    """Inspect the database for migration purposes."""
    pool = await create_connection_pool()
    
    try:
        # Tables to inspect
        tables = [
            ('embeddings', 'multimodal_embeddings'),
            ('embeddings', 'multimodal_embeddings_chunks'),
            ('metadata', 'frame_details_full'),
            ('metadata', 'frame_details_chunks'),
            ('metadata', 'process_frames_chunks')
        ]
        
        for schema, table in tables:
            exists = await check_table_exists(pool, schema, table)
            
            if exists:
                await inspect_table_schema(pool, schema, table)
                await sample_table_data(pool, schema, table)
            else:
                logger.warning(f"Table {schema}.{table} does not exist")
        
        # Get unique reference_id formats
        logger.info("\n=== Reference ID Formats ===")
        async with pool.acquire() as conn:
            # Check if multimodal_embeddings table exists first
            mm_exists = await check_table_exists(pool, 'embeddings', 'multimodal_embeddings')
            
            if mm_exists:
                # Sample frame reference_ids
                frame_refs = await conn.fetch('''
                    SELECT reference_id FROM embeddings.multimodal_embeddings
                    WHERE reference_type = 'frame'
                    ORDER BY reference_id
                    LIMIT 5
                ''')
                
                logger.info("Frame reference_id samples:")
                for ref in frame_refs:
                    logger.info(f"  {ref['reference_id']}")
                
                # Sample chunk reference_ids
                chunk_refs = await conn.fetch('''
                    SELECT reference_id FROM embeddings.multimodal_embeddings
                    WHERE reference_type = 'chunk'
                    ORDER BY reference_id
                    LIMIT 5
                ''')
                
                logger.info("\nChunk reference_id samples:")
                for ref in chunk_refs:
                    logger.info(f"  {ref['reference_id']}")
            else:
                logger.warning("Table embeddings.multimodal_embeddings does not exist. Cannot sample reference_ids.")
        
    finally:
        await pool.close()
        logger.info("PostgreSQL connection pool closed")

if __name__ == "__main__":
    logger.info("Starting database inspection")
    asyncio.run(inspect_database()) 