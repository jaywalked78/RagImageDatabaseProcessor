#!/usr/bin/env python3
"""
Diagnostic script to check database connection and content across all relevant tables.
"""

import os
import sys
import logging
import asyncio
import json
from dotenv import load_dotenv
import asyncpg
from tabulate import tabulate
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("db_diagnostics")

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
        logger.info(f"Attempting to connect to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}")
        logger.info(f"Using credentials: user={DB_USER}, password={'*' * (len(DB_PASSWORD) if DB_PASSWORD else 0)}")
        
        pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            timeout=10.0  # Set explicit timeout
        )
        logger.info(f"Successfully connected to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}")
        return pool
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
        logger.error(traceback.format_exc())
        return None

async def check_table_exists(conn, schema, table):
    """Check if a table exists in the database."""
    try:
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = $1 
                AND table_name = $2
            )
        """, schema, table)
        
        return exists
    except Exception as e:
        logger.error(f"Error checking if table {schema}.{table} exists: {str(e)}")
        return False

async def check_table_content(conn, schema, table, id_column=None, limit=10):
    """Check the content of a table."""
    try:
        # First, check if table exists
        table_exists = await check_table_exists(conn, schema, table)
        if not table_exists:
            logger.error(f"Table {schema}.{table} does not exist!")
            return False, 0, []
        
        # Count records
        count = await conn.fetchval(f"SELECT COUNT(*) FROM {schema}.{table}")
        
        # Get sample records
        if id_column:
            sample_query = f"SELECT * FROM {schema}.{table} ORDER BY {id_column} ASC LIMIT {limit}"
        else:
            sample_query = f"SELECT * FROM {schema}.{table} LIMIT {limit}"
            
        records = await conn.fetch(sample_query)
        
        return True, count, records
    except Exception as e:
        logger.error(f"Error checking content of table {schema}.{table}: {str(e)}")
        logger.error(traceback.format_exc())
        return False, 0, []

async def check_schema_exists(conn, schema):
    """Check if a schema exists in the database."""
    try:
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.schemata 
                WHERE schema_name = $1
            )
        """, schema)
        
        return exists
    except Exception as e:
        logger.error(f"Error checking if schema {schema} exists: {str(e)}")
        return False

async def get_table_columns(conn, schema, table):
    """Get the columns of a table."""
    try:
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = $1 
            AND table_name = $2
            ORDER BY ordinal_position
        """, schema, table)
        
        return columns
    except Exception as e:
        logger.error(f"Error getting columns for table {schema}.{table}: {str(e)}")
        return []

async def test_write_permission(conn, schema, table):
    """Test if we have write permission to a table by trying to start a transaction and rollback."""
    try:
        tr = conn.transaction()
        await tr.start()
        # Just check if we can execute a simple query to prepare for insertion
        await conn.execute(f"SELECT 1 FROM {schema}.{table} LIMIT 1")
        # Don't actually insert anything, just roll back
        await tr.rollback()
        return True
    except Exception as e:
        logger.error(f"Error testing write permission for {schema}.{table}: {str(e)}")
        return False

async def check_database():
    """Check the database connection and content."""
    pool = await create_connection_pool()
    
    if not pool:
        logger.error("Failed to create connection pool. Exiting.")
        return False
    
    try:
        async with pool.acquire() as conn:
            logger.info("=== DATABASE SCHEMA INFORMATION ===")
            # Check if the required schemas exist
            schemas = ['content', 'metadata', 'embeddings']
            for schema in schemas:
                schema_exists = await check_schema_exists(conn, schema)
                logger.info(f"Schema '{schema}' exists: {schema_exists}")
            
            logger.info("\n=== CONTENT SCHEMA TABLES ===")
            # Check frames table
            if await check_schema_exists(conn, 'content'):
                frames_exists, frames_count, frames_records = await check_table_content(
                    conn, 'content', 'frames', 'frame_id'
                )
                
                if frames_exists:
                    logger.info(f"Table content.frames exists with {frames_count} records")
                    
                    # Get columns
                    columns = await get_table_columns(conn, 'content', 'frames')
                    logger.info("Columns: " + ", ".join([f"{col['column_name']} ({col['data_type']})" for col in columns]))
                    
                    # Check write permission
                    write_permission = await test_write_permission(conn, 'content', 'frames')
                    logger.info(f"Have write permission to content.frames: {write_permission}")
                    
                    if frames_count > 0:
                        headers = [col['column_name'] for col in columns]
                        data = [[record[col['column_name']] for col in columns] for record in frames_records]
                        logger.info("Sample records:")
                        logger.info("\n" + tabulate(data, headers=headers))
                    else:
                        logger.warning("content.frames table exists but contains no records!")
            
            logger.info("\n=== METADATA SCHEMA TABLES ===")
            # Check frame_details_full table
            if await check_schema_exists(conn, 'metadata'):
                frame_details_exists, frame_details_count, frame_details_records = await check_table_content(
                    conn, 'metadata', 'frame_details_full', 'frame_id'
                )
                
                if frame_details_exists:
                    logger.info(f"Table metadata.frame_details_full exists with {frame_details_count} records")
                    
                    # Get columns
                    columns = await get_table_columns(conn, 'metadata', 'frame_details_full')
                    logger.info("Columns: " + ", ".join([f"{col['column_name']} ({col['data_type']})" for col in columns]))
                    
                    # Check write permission
                    write_permission = await test_write_permission(conn, 'metadata', 'frame_details_full')
                    logger.info(f"Have write permission to metadata.frame_details_full: {write_permission}")
                    
                    if frame_details_count > 0:
                        # Only show selected columns for readability
                        selected_columns = ['frame_id', 'description', 'workflow_stage', 'reference_id']
                        data = [[record[col] for col in selected_columns] for record in frame_details_records]
                        logger.info("Sample records:")
                        logger.info("\n" + tabulate(data, headers=selected_columns))
                    else:
                        logger.warning("metadata.frame_details_full table exists but contains no records!")
                
                # Check frame_details_chunks table
                chunks_exists, chunks_count, chunks_records = await check_table_content(
                    conn, 'metadata', 'frame_details_chunks', 'chunk_id'
                )
                
                if chunks_exists:
                    logger.info(f"Table metadata.frame_details_chunks exists with {chunks_count} records")
                    
                    # Get columns
                    columns = await get_table_columns(conn, 'metadata', 'frame_details_chunks')
                    logger.info("Columns: " + ", ".join([f"{col['column_name']} ({col['data_type']})" for col in columns]))
                    
                    # Check write permission
                    write_permission = await test_write_permission(conn, 'metadata', 'frame_details_chunks')
                    logger.info(f"Have write permission to metadata.frame_details_chunks: {write_permission}")
                    
                    if chunks_count > 0:
                        # Only show selected columns for readability
                        selected_columns = ['chunk_id', 'frame_id', 'workflow_stage', 'reference_id']
                        data = [[record[col] for col in selected_columns] for record in chunks_records]
                        logger.info("Sample records:")
                        logger.info("\n" + tabulate(data, headers=selected_columns))
                    else:
                        logger.warning("metadata.frame_details_chunks table exists but contains no records!")
            
            logger.info("\n=== EMBEDDINGS SCHEMA TABLES ===")
            # Check multimodal_embeddings_chunks table
            if await check_schema_exists(conn, 'embeddings'):
                embeddings_exists, embeddings_count, embeddings_records = await check_table_content(
                    conn, 'embeddings', 'multimodal_embeddings_chunks', 'embedding_id'
                )
                
                if embeddings_exists:
                    logger.info(f"Table embeddings.multimodal_embeddings_chunks exists with {embeddings_count} records")
                    
                    # Get columns
                    columns = await get_table_columns(conn, 'embeddings', 'multimodal_embeddings_chunks')
                    logger.info("Columns: " + ", ".join([f"{col['column_name']} ({col['data_type']})" for col in columns]))
                    
                    # Check write permission
                    write_permission = await test_write_permission(conn, 'embeddings', 'multimodal_embeddings_chunks')
                    logger.info(f"Have write permission to embeddings.multimodal_embeddings_chunks: {write_permission}")
                    
                    if embeddings_count > 0:
                        # Only show selected columns for readability
                        selected_columns = ['embedding_id', 'chunk_id', 'reference_id', 'model_name']
                        data = [[record[col] for col in selected_columns] for record in embeddings_records]
                        logger.info("Sample records:")
                        logger.info("\n" + tabulate(data, headers=selected_columns))
                    else:
                        logger.warning("embeddings.multimodal_embeddings_chunks table exists but contains no records!")
            
            # Diagnostics summary
            logger.info("\n=== DIAGNOSTICS SUMMARY ===")
            all_tables_exist = all([
                await check_table_exists(conn, 'content', 'frames'),
                await check_table_exists(conn, 'metadata', 'frame_details_full'),
                await check_table_exists(conn, 'metadata', 'frame_details_chunks'),
                await check_table_exists(conn, 'embeddings', 'multimodal_embeddings_chunks')
            ])
            
            has_frames = frames_count > 0 if 'frames_count' in locals() else False
            has_metadata = frame_details_count > 0 if 'frame_details_count' in locals() else False
            has_chunks = chunks_count > 0 if 'chunks_count' in locals() else False
            has_embeddings = embeddings_count > 0 if 'embeddings_count' in locals() else False
            
            logger.info(f"All required tables exist: {all_tables_exist}")
            logger.info(f"Frames data exists: {has_frames}")
            logger.info(f"Frame metadata exists: {has_metadata}")
            logger.info(f"Chunks data exists: {has_chunks}")
            logger.info(f"Embeddings data exists: {has_embeddings}")
            
            # Check for potential issues
            if all_tables_exist and not has_frames:
                logger.error("All tables exist but no frames data was found! Check content.frames table.")
                
            if has_frames and not has_metadata:
                logger.error("Frames exist but no metadata! Check process_frame function in your script.")
                
            if has_metadata and not has_chunks:
                logger.error("Metadata exists but no chunks! Check ensure_chunk_exists function in your script.")
                
            if has_chunks and not has_embeddings:
                logger.error("Chunks exist but no embeddings! Check ensure_embedding_exists function in your script.")
                
            return all_tables_exist and has_frames and has_metadata and has_chunks and has_embeddings
            
    except Exception as e:
        logger.error(f"Error during database diagnostics: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    finally:
        if pool:
            await pool.close()
            logger.info("Connection pool closed")

async def main():
    """Main function."""
    logger.info("Starting database diagnostics...")
    success = await check_database()
    logger.info(f"Diagnostics completed. Success: {success}")
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 