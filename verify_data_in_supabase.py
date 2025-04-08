#!/usr/bin/env python3
"""
Script to verify data in Supabase database tables.
Queries the database to check if the processed data was correctly stored.
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
logger = logging.getLogger("supabase_verifier")

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

async def check_content_frames(pool):
    """Check data in content.frames table."""
    async with pool.acquire() as conn:
        logger.info("Checking content.frames table...")
        
        # Check if table exists
        table_exists = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'content' AND table_name = 'frames')"
        )
        
        if not table_exists:
            logger.error("content.frames table does not exist!")
            return
        
        # Count records
        count = await conn.fetchval("SELECT COUNT(*) FROM content.frames")
        logger.info(f"Found {count} records in content.frames table")
        
        # Get first 10 records
        records = await conn.fetch("SELECT * FROM content.frames LIMIT 10")
        
        if not records:
            logger.warning("No records found in content.frames table!")
            return
            
        # Display data with fixed column handling
        if records:
            headers = list(records[0].keys())
            data = [[record[col] for col in headers] for record in records]
            
            logger.info("Sample records from content.frames table:")
            logger.info("\n" + tabulate(data, headers=headers))

async def check_metadata_frames(pool):
    """Check data in metadata.frame_details_full table."""
    async with pool.acquire() as conn:
        logger.info("\nChecking metadata.frame_details_full table...")
        
        # Count records
        count = await conn.fetchval("SELECT COUNT(*) FROM metadata.frame_details_full")
        logger.info(f"Found {count} records in metadata.frame_details_full table")
        
        # Get records for our processed frames
        records = await conn.fetch("""
            SELECT frame_id, reference_id, description, workflow_stage, tags
            FROM metadata.frame_details_full
            WHERE description IS NOT NULL
            AND description NOT LIKE 'Description for%'
            LIMIT 10
        """)
        
        if not records:
            logger.warning("No processed records found in metadata.frame_details_full table!")
        else:
            # Display data
            headers = ["frame_id", "reference_id", "description", "workflow_stage", "tags"]
            data = [[record['frame_id'], record['reference_id'], 
                    record['description'][:50] + "..." if record['description'] and len(record['description']) > 50 else record['description'],
                    record['workflow_stage'], record['tags']] 
                    for record in records]
            
            logger.info("Sample processed records from metadata.frame_details_full table:")
            logger.info("\n" + tabulate(data, headers=headers))
        
        # Check technical details (JSON/JSONB fields)
        records = await conn.fetch("""
            SELECT frame_id, technical_details
            FROM metadata.frame_details_full
            WHERE technical_details IS NOT NULL
            LIMIT 5
        """)
        
        if records:
            logger.info("\nSample technical_details from metadata.frame_details_full:")
            for record in records:
                logger.info(f"Frame {record['frame_id']}:")
                logger.info(json.dumps(record['technical_details'], indent=2))

async def check_metadata_chunks(pool):
    """Check data in metadata.frame_details_chunks table."""
    async with pool.acquire() as conn:
        logger.info("\nChecking metadata.frame_details_chunks table...")
        
        # Count records
        count = await conn.fetchval("SELECT COUNT(*) FROM metadata.frame_details_chunks")
        logger.info(f"Found {count} records in metadata.frame_details_chunks table")
        
        # First, check which columns exist in the table
        columns = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'metadata' AND table_name = 'frame_details_chunks'
        """)
        
        # Log available columns
        available_columns = [col['column_name'] for col in columns]
        logger.info(f"Available columns in metadata.frame_details_chunks: {', '.join(available_columns)}")
        
        # Get records for our processed chunks with verified columns
        records = await conn.fetch("""
            SELECT chunk_id, frame_id, reference_id, description
            FROM metadata.frame_details_chunks
            WHERE description IS NOT NULL
            AND description NOT LIKE 'Chunk for%'
            LIMIT 10
        """)
        
        if not records:
            logger.warning("No processed records found in metadata.frame_details_chunks table!")
        else:
            # Display data
            headers = ["chunk_id", "frame_id", "reference_id", "description"]
            data = [[record['chunk_id'], record['frame_id'], record['reference_id'], 
                    record['description'][:50] + "..." if record['description'] and len(record['description']) > 50 else record['description']] 
                    for record in records]
            
            logger.info("Sample processed records from metadata.frame_details_chunks table:")
            logger.info("\n" + tabulate(data, headers=headers))
            
        # Check technical details if they exist
        if 'technical_details' in available_columns:
            records = await conn.fetch("""
                SELECT chunk_id, technical_details
                FROM metadata.frame_details_chunks
                WHERE technical_details IS NOT NULL
                LIMIT 5
            """)
            
            if records:
                logger.info("\nSample technical_details from metadata.frame_details_chunks:")
                for record in records:
                    logger.info(f"Chunk {record['chunk_id']}:")
                    logger.info(json.dumps(record['technical_details'], indent=2))

async def check_embeddings(pool):
    """Check data in embeddings tables."""
    async with pool.acquire() as conn:
        logger.info("\nChecking embeddings.multimodal_embeddings_chunks table...")
        
        # Count records
        count = await conn.fetchval("SELECT COUNT(*) FROM embeddings.multimodal_embeddings_chunks")
        logger.info(f"Found {count} records in embeddings.multimodal_embeddings_chunks table")
        
        # Check embedding reference_ids
        records = await conn.fetch("""
            SELECT embedding_id, chunk_id, reference_id
            FROM embeddings.multimodal_embeddings_chunks
            LIMIT 10
        """)
        
        if not records:
            logger.warning("No records found in embeddings.multimodal_embeddings_chunks table!")
        else:
            # Display data
            headers = ["embedding_id", "chunk_id", "reference_id"]
            data = [[record['embedding_id'], record['chunk_id'], record['reference_id']] 
                    for record in records]
            
            logger.info("Sample records from embeddings.multimodal_embeddings_chunks table:")
            logger.info("\n" + tabulate(data, headers=headers))
        
        # First, check what columns are available in the table
        columns = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'embeddings' AND table_name = 'multimodal_embeddings_chunks'
        """)
        
        # Log available columns
        available_columns = [col['column_name'] for col in columns]
        logger.info(f"Available columns in embeddings.multimodal_embeddings_chunks: {', '.join(available_columns)}")
        
        # Try different possible column names for embedding vectors
        possible_vector_columns = ['embedding_vector', 'embedding', 'vector', 'content_vector']
        vector_column = None
        
        for col in possible_vector_columns:
            if col in available_columns:
                vector_column = col
                break
        
        if vector_column:
            # Check if there are any vectors
            try:
                vector_count = await conn.fetchval(f"""
                    SELECT COUNT(*) 
                    FROM embeddings.multimodal_embeddings_chunks 
                    WHERE {vector_column} IS NOT NULL
                """)
                logger.info(f"Found {vector_count} records with embedding vectors in column '{vector_column}'")
                
                # Get information about vector dimensions if possible
                try:
                    vector_dimensions = await conn.fetchval(f"""
                        SELECT array_length({vector_column}, 1)
                        FROM embeddings.multimodal_embeddings_chunks 
                        WHERE {vector_column} IS NOT NULL
                        LIMIT 1
                    """)
                    if vector_dimensions:
                        logger.info(f"Embedding vectors have {vector_dimensions} dimensions")
                except Exception as e:
                    logger.info(f"Could not determine vector dimensions: {str(e)}")
                    
            except Exception as e:
                logger.error(f"Error checking vector column '{vector_column}': {str(e)}")
        else:
            logger.warning("No embedding vector column found in table. Checked for: " + ", ".join(possible_vector_columns))

async def main():
    """Main function."""
    logger.info("Starting data verification in Supabase database...")
    
    try:
        # Create connection pool
        pool = await create_connection_pool()
        
        # Check the various tables with better error handling
        try:
            await check_content_frames(pool)
        except Exception as e:
            logger.error(f"Error checking content.frames: {str(e)}")
        
        try:
            await check_metadata_frames(pool)
        except Exception as e:
            logger.error(f"Error checking metadata.frame_details_full: {str(e)}")
        
        try:
            await check_metadata_chunks(pool)
        except Exception as e:
            logger.error(f"Error checking metadata.frame_details_chunks: {str(e)}")
        
        try:
            await check_embeddings(pool)
        except Exception as e:
            logger.error(f"Error checking embeddings tables: {str(e)}")
        
        logger.info("\nData verification complete")
        
        # Close pool
        await pool.close()
        logger.info("PostgreSQL connection pool closed")
        
    except Exception as e:
        logger.error(f"Error during verification: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 