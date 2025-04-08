#!/usr/bin/env python3
"""
Utility script to inspect the Supabase database schema.
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
logger = logging.getLogger('inspect')

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('POSTGRES_HOST', 'aws-0-us-east-1.pooler.supabase.com')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'postgres')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASS')

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
    """Inspect the schema of a table."""
    logger.info(f"Inspecting table {schema}.{table}")
    
    async with pool.acquire() as conn:
        # Check if table exists
        exists = await conn.fetchval(f'''
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = '{schema}' 
                AND table_name = '{table}'
            )
        ''')
        
        if not exists:
            logger.warning(f"Table {schema}.{table} does not exist")
            return
        
        # Get column information
        columns = await conn.fetch(f'''
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = '{schema}'
            AND table_name = '{table}'
            ORDER BY ordinal_position
        ''')
        
        logger.info(f"Columns in {schema}.{table}:")
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            logger.info(f"  {col['column_name']}: {col['data_type']} {nullable}")
        
        # Get primary key information
        pk_columns = await conn.fetch(f'''
            SELECT kc.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kc
                ON kc.constraint_name = tc.constraint_name
                AND kc.table_schema = tc.table_schema
                AND kc.table_name = tc.table_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = '{schema}'
            AND tc.table_name = '{table}'
            ORDER BY kc.ordinal_position
        ''')
        
        if pk_columns:
            pk_names = [col['column_name'] for col in pk_columns]
            logger.info(f"  Primary Key: {', '.join(pk_names)}")
        
        # Get foreign key information
        fk_info = await conn.fetch(f'''
            SELECT
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = '{schema}'
            AND tc.table_name = '{table}'
        ''')
        
        if fk_info:
            logger.info("  Foreign Keys:")
            for fk in fk_info:
                logger.info(f"    {fk['column_name']} -> {fk['foreign_table_schema']}.{fk['foreign_table_name']}.{fk['foreign_column_name']}")
        
        # Get sample data
        try:
            sample_data = await conn.fetch(f'''
                SELECT * FROM {schema}.{table} LIMIT 3
            ''')
            
            if sample_data:
                logger.info("  Sample Data:")
                for i, row in enumerate(sample_data):
                    logger.info(f"    Row {i+1}: {dict(row)}")
        except Exception as e:
            logger.error(f"Error fetching sample data: {str(e)}")

async def inspect_table_foreign_keys(pool, schema, table):
    """Inspect foreign key constraints on a table."""
    logger.info(f"Inspecting foreign key constraints on {schema}.{table}")
    
    async with pool.acquire() as conn:
        # Get foreign key information
        foreign_keys = await conn.fetch('''
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_schema AS foreign_table_schema,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.constraint_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = $1
            AND tc.table_name = $2
        ''', schema, table)
        
        if foreign_keys:
            logger.info(f"  Foreign Key Constraints on {schema}.{table}:")
            for fk in foreign_keys:
                logger.info(f"    {fk['constraint_name']}: {fk['column_name']} -> {fk['foreign_table_schema']}.{fk['foreign_table_name']}.{fk['foreign_column_name']}")
        else:
            logger.info(f"  No foreign key constraints found on {schema}.{table}")
            
        # Also look for constraints where this table is referenced
        references = await conn.fetch('''
            SELECT
                tc.table_schema AS referencing_schema,
                tc.table_name AS referencing_table,
                kcu.column_name AS referencing_column,
                tc.constraint_name,
                ccu.column_name AS referenced_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.constraint_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND ccu.table_schema = $1
            AND ccu.table_name = $2
        ''', schema, table)
        
        if references:
            logger.info(f"  Tables referencing {schema}.{table}:")
            for ref in references:
                logger.info(f"    {ref['referencing_schema']}.{ref['referencing_table']}.{ref['referencing_column']} -> {ref['referenced_column']} (constraint: {ref['constraint_name']})")
        else:
            logger.info(f"  No tables found referencing {schema}.{table}")

async def inspect_schema(pool, schema):
    """List all tables in a schema."""
    logger.info(f"Inspecting schema {schema}")
    
    async with pool.acquire() as conn:
        # Check if schema exists
        exists = await conn.fetchval(f'''
            SELECT EXISTS (
                SELECT FROM information_schema.schemata
                WHERE schema_name = '{schema}'
            )
        ''')
        
        if not exists:
            logger.warning(f"Schema {schema} does not exist")
            return
        
        # Get all tables in the schema
        tables = await conn.fetch(f'''
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{schema}'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        ''')
        
        logger.info(f"Tables in schema {schema}:")
        for table in tables:
            logger.info(f"  {table['table_name']}")
            
        # Inspect each table
        for table in tables:
            await inspect_table_schema(pool, schema, table['table_name'])

async def main():
    """Execute the inspection process."""
    logger.info("Starting database schema inspection...")
    
    # Create connection pool
    pool = await create_connection_pool()
    
    try:
        # Look for the 'frames' table in all schemas
        async with pool.acquire() as conn:
            schemas = await conn.fetch('''
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
                ORDER BY schema_name
            ''')
            
            logger.info("Searching for 'frames' table in all schemas:")
            found_frames = False
            
            for schema_row in schemas:
                schema = schema_row['schema_name']
                tables = await conn.fetch('''
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = $1
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                ''', schema)
                
                for table_row in tables:
                    table = table_row['table_name']
                    if table == 'frames':
                        found_frames = True
                        logger.info(f"Found frames table in schema: {schema}")
                        await inspect_table_schema(pool, schema, 'frames')
                        await inspect_table_foreign_keys(pool, schema, 'frames')
            
            if not found_frames:
                logger.info("No 'frames' table found in any schema")
        
        # Specifically inspect metadata schema tables
        logger.info("\n--- Metadata Schema Tables ---")
        metadata_tables = ['frame_details_full', 'frame_details_chunks', 'process_frames_chunks']
        for table in metadata_tables:
            await inspect_table_schema(pool, 'metadata', table)
            await inspect_table_foreign_keys(pool, 'metadata', table)
        
        # Specifically inspect embeddings schema tables
        logger.info("\n--- Embeddings Schema Tables ---")
        embeddings_tables = ['multimodal_embeddings', 'multimodal_embeddings_chunks', 'text_embeddings']
        for table in embeddings_tables:
            await inspect_table_schema(pool, 'embeddings', table)
            await inspect_table_foreign_keys(pool, 'embeddings', table)
                
    except Exception as e:
        logger.error(f"Inspection failed: {str(e)}")
        raise
    finally:
        # Close connection pool
        await pool.close()
        logger.info("PostgreSQL connection pool closed")

if __name__ == "__main__":
    asyncio.run(main()) 