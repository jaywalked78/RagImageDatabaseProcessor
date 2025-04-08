#!/usr/bin/env python3
"""
Production data verification script to ensure all tables have proper data.
Checks content, metadata, and embeddings schemas and verifies relationships.
"""

import os
import sys
import logging
import asyncio
import json
from datetime import datetime
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
logger = logging.getLogger('prod_verify')

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

async def verify_content_frames(pool):
    """Verify data in content.frames table."""
    async with pool.acquire() as conn:
        logger.info("Checking content.frames table...")
        
        # Get count of frames
        count = await conn.fetchval("SELECT COUNT(*) FROM content.frames")
        logger.info(f"Total frames in content.frames: {count}")
        
        # Check if required fields are populated
        missing_fields = await conn.fetch("""
            SELECT frame_id, 
                CASE WHEN image_url IS NULL THEN 'missing_image_url' ELSE '' END ||
                CASE WHEN folder_name IS NULL THEN ' missing_folder_name' ELSE '' END ||
                CASE WHEN file_name IS NULL THEN ' missing_file_name' ELSE '' END as missing_fields
            FROM content.frames
            WHERE image_url IS NULL OR folder_name IS NULL OR file_name IS NULL
        """)
        
        if missing_fields:
            logger.warning(f"Found {len(missing_fields)} frames with missing required fields:")
            for row in missing_fields[:5]:
                logger.warning(f"  Frame {row['frame_id']}: {row['missing_fields']}")
            if len(missing_fields) > 5:
                logger.warning(f"  ... and {len(missing_fields) - 5} more")
        else:
            logger.info("✅ All frames have required fields populated")
        
        # Sample data
        sample = await conn.fetch("SELECT * FROM content.frames LIMIT 2")
        logger.info("Sample frames data:")
        for row in sample:
            logger.info(f"  {dict(row)}")

async def verify_metadata_tables(pool):
    """Verify data in metadata tables."""
    async with pool.acquire() as conn:
        logger.info("\nChecking metadata tables...")
        
        # Check frame_details_full table
        frame_details_count = await conn.fetchval("SELECT COUNT(*) FROM metadata.frame_details_full")
        logger.info(f"Total rows in metadata.frame_details_full: {frame_details_count}")
        
        # Check frame_details_chunks table
        chunks_count = await conn.fetchval("SELECT COUNT(*) FROM metadata.frame_details_chunks")
        logger.info(f"Total rows in metadata.frame_details_chunks: {chunks_count}")
        
        # Check process_frames_chunks table
        process_count = await conn.fetchval("SELECT COUNT(*) FROM metadata.process_frames_chunks")
        logger.info(f"Total rows in metadata.process_frames_chunks: {process_count}")
        
        # Check if metadata is linked properly to frames
        orphaned_metadata = await conn.fetch("""
            SELECT m.frame_id 
            FROM metadata.frame_details_full m
            LEFT JOIN content.frames f ON m.frame_id = f.frame_id
            WHERE f.frame_id IS NULL
        """)
        
        if orphaned_metadata:
            logger.error(f"Found {len(orphaned_metadata)} metadata entries without matching frames:")
            for row in orphaned_metadata[:5]:
                logger.error(f"  {row['frame_id']}")
            if len(orphaned_metadata) > 5:
                logger.error(f"  ... and {len(orphaned_metadata) - 5} more")
        else:
            logger.info("✅ All metadata entries have matching frames")
        
        # Check if chunks have reference IDs
        missing_refs = await conn.fetch("""
            SELECT frame_id, chunk_id
            FROM metadata.frame_details_chunks
            WHERE reference_id IS NULL
        """)
        
        if missing_refs:
            logger.warning(f"Found {len(missing_refs)} chunks without reference_id:")
            for row in missing_refs[:5]:
                logger.warning(f"  Chunk {row['chunk_id']} for frame {row['frame_id']}")
            if len(missing_refs) > 5:
                logger.warning(f"  ... and {len(missing_refs) - 5} more")
        else:
            logger.info("✅ All chunks have reference_id populated")
        
        # Check for chunks with OCR data
        with_ocr = await conn.fetchval("""
            SELECT COUNT(*)
            FROM metadata.frame_details_chunks
            WHERE ocr_data IS NOT NULL AND LENGTH(ocr_data) > 0
        """)
        
        logger.info(f"Chunks with OCR data: {with_ocr} out of {chunks_count}")
        
        # Sample frame_details_full data
        sample = await conn.fetch("SELECT * FROM metadata.frame_details_full LIMIT 1")
        if sample:
            logger.info("Sample frame_details_full data:")
            for row in sample:
                data = dict(row)
                # Truncate large text fields for readability
                if data.get('ocr_data') and len(data['ocr_data']) > 100:
                    data['ocr_data'] = data['ocr_data'][:100] + '...'
                logger.info(f"  {data}")
        
        # Sample frame_details_chunks data
        sample = await conn.fetch("SELECT * FROM metadata.frame_details_chunks LIMIT 1")
        if sample:
            logger.info("Sample frame_details_chunks data:")
            for row in sample:
                data = dict(row)
                if data.get('ocr_data') and len(data['ocr_data']) > 100:
                    data['ocr_data'] = data['ocr_data'][:100] + '...'
                logger.info(f"  {data}")
        
        # Sample process_frames_chunks data
        sample = await conn.fetch("SELECT * FROM metadata.process_frames_chunks LIMIT 1")
        if sample:
            logger.info("Sample process_frames_chunks data:")
            for row in sample:
                data = dict(row)
                logger.info(f"  {data}")

async def verify_embeddings_tables(pool):
    """Verify data in embeddings tables."""
    async with pool.acquire() as conn:
        logger.info("\nChecking embeddings tables...")
        
        # Check multimodal_embeddings table
        mm_count = await conn.fetchval("SELECT COUNT(*) FROM embeddings.multimodal_embeddings")
        logger.info(f"Total rows in embeddings.multimodal_embeddings: {mm_count}")
        
        # Check multimodal_embeddings_chunks table
        mm_chunks_count = await conn.fetchval("SELECT COUNT(*) FROM embeddings.multimodal_embeddings_chunks")
        logger.info(f"Total rows in embeddings.multimodal_embeddings_chunks: {mm_chunks_count}")
        
        # Check for embeddings with NULL vectors
        null_embeddings = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM embeddings.multimodal_embeddings_chunks
            WHERE embedding IS NULL
        """)
        
        if null_embeddings > 0:
            logger.error(f"Found {null_embeddings} chunk embeddings with NULL vectors")
        else:
            logger.info("✅ All chunk embeddings have non-NULL vectors")
        
        # Check for chunks without embeddings
        orphaned_chunks = await conn.fetch("""
            SELECT c.chunk_id
            FROM metadata.frame_details_chunks c
            LEFT JOIN embeddings.multimodal_embeddings_chunks e ON c.chunk_id = e.chunk_id
            WHERE e.embedding_id IS NULL
        """)
        
        if orphaned_chunks:
            logger.warning(f"Found {len(orphaned_chunks)} chunks without embeddings:")
            for row in orphaned_chunks[:5]:
                logger.warning(f"  Chunk {row['chunk_id']}")
            if len(orphaned_chunks) > 5:
                logger.warning(f"  ... and {len(orphaned_chunks) - 5} more")
        else:
            logger.info("✅ All chunks have embeddings")
        
        # Check for embeddings distribution by reference_type
        ref_types = await conn.fetch("""
            SELECT reference_type, COUNT(*) as count
            FROM embeddings.multimodal_embeddings_chunks
            GROUP BY reference_type
        """)
        
        logger.info("Embeddings distribution by reference_type:")
        for row in ref_types:
            logger.info(f"  {row['reference_type']}: {row['count']}")

async def check_ocr_data_quality(pool):
    """Check the quality of OCR data in the database."""
    async with pool.acquire() as conn:
        logger.info("\nChecking OCR data quality...")
        
        # Count frames with non-empty OCR data
        with_ocr = await conn.fetchval("""
            SELECT COUNT(*)
            FROM metadata.frame_details_full
            WHERE ocr_data IS NOT NULL AND LENGTH(ocr_data) > 10
        """)
        
        total = await conn.fetchval("SELECT COUNT(*) FROM metadata.frame_details_full")
        logger.info(f"Frames with substantial OCR data: {with_ocr} out of {total} ({with_ocr/total*100:.1f}%)")
        
        # Check average OCR text length
        avg_length = await conn.fetchval("""
            SELECT AVG(LENGTH(ocr_data))
            FROM metadata.frame_details_full
            WHERE ocr_data IS NOT NULL
        """)
        
        if avg_length:
            logger.info(f"Average OCR text length: {avg_length:.1f} characters")
        
        # Sample OCR data (first 300 chars) from a few frames
        sample_ocr = await conn.fetch("""
            SELECT frame_id, SUBSTRING(ocr_data, 1, 300) as sample_ocr
            FROM metadata.frame_details_full
            WHERE ocr_data IS NOT NULL AND LENGTH(ocr_data) > 0
            LIMIT 2
        """)
        
        if sample_ocr:
            logger.info("Sample OCR data:")
            for row in sample_ocr:
                logger.info(f"  Frame {row['frame_id']}:")
                logger.info(f"    {row['sample_ocr']}...")

async def detect_sensitive_info(pool):
    """Check for potentially sensitive information in OCR data."""
    async with pool.acquire() as conn:
        logger.info("\nChecking for sensitive information patterns in OCR data...")
        
        # Look for potential API keys (like format of 20+ alphanumeric characters)
        api_key_pattern = await conn.fetch("""
            SELECT frame_id, ocr_data
            FROM metadata.frame_details_full
            WHERE ocr_data ~ '[A-Za-z0-9_-]{20,}'
            LIMIT 5
        """)
        
        if api_key_pattern:
            logger.warning(f"Found {len(api_key_pattern)} frames with potential API key patterns")
            
        # Look for password field patterns (like "password=", "pwd=", etc.)
        password_pattern = await conn.fetch("""
            SELECT frame_id, ocr_data
            FROM metadata.frame_details_full
            WHERE ocr_data ~* '(password|passwd|pwd)[=:][^ ]*'
            LIMIT 5
        """)
        
        if password_pattern:
            logger.warning(f"Found {len(password_pattern)} frames with potential password fields")
            
        # Look for credit card number patterns (16 digits, possibly with spaces or dashes)
        card_pattern = await conn.fetch("""
            SELECT frame_id, ocr_data
            FROM metadata.frame_details_full
            WHERE ocr_data ~ '[0-9]{4}[ -]?[0-9]{4}[ -]?[0-9]{4}[ -]?[0-9]{4}'
            LIMIT 5
        """)
        
        if card_pattern:
            logger.warning(f"Found {len(card_pattern)} frames with potential credit/debit card numbers")
        
        # Potential .env file contents
        env_file_pattern = await conn.fetch("""
            SELECT frame_id, ocr_data
            FROM metadata.frame_details_full
            WHERE ocr_data ~* '(API_KEY|SECRET_KEY|TOKEN|DATABASE_URL|PASSWORD)'
            LIMIT 5
        """)
        
        if env_file_pattern:
            logger.warning(f"Found {len(env_file_pattern)} frames with potential .env file contents")
            
        # Total frames with any sensitive information
        total_sensitive = await conn.fetchval("""
            SELECT COUNT(DISTINCT frame_id)
            FROM metadata.frame_details_full
            WHERE ocr_data ~* '(password|passwd|pwd)[=:][^ ]*'
               OR ocr_data ~ '[0-9]{4}[ -]?[0-9]{4}[ -]?[0-9]{4}[ -]?[0-9]{4}'
               OR ocr_data ~* '(API_KEY|SECRET_KEY|TOKEN|DATABASE_URL|PASSWORD)'
               OR ocr_data ~ '[A-Za-z0-9_-]{20,}'
        """)
        
        logger.info(f"Total frames with potential sensitive information: {total_sensitive}")

async def main():
    """Execute the verification process."""
    logger.info("Starting production data verification...")
    
    # Create connection pool
    pool = await create_connection_pool()
    
    try:
        # Verify tables in each schema
        await verify_content_frames(pool)
        await verify_metadata_tables(pool)
        await verify_embeddings_tables(pool)
        
        # Check OCR data quality
        await check_ocr_data_quality(pool)
        
        # Check for sensitive information
        await detect_sensitive_info(pool)
        
        logger.info("\nVerification completed")
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        raise
    finally:
        # Close connection pool
        await pool.close()
        logger.info("PostgreSQL connection pool closed")

if __name__ == "__main__":
    asyncio.run(main()) 