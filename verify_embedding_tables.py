#!/usr/bin/env python3
"""
Verification script for database tables and reference IDs.
Ensures that all tables have the correct reference ID formats and data consistency.
"""

import os
import sys
import logging
import asyncio
import re
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
logger = logging.getLogger('verification')

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-us-east-1.pooler.supabase.com')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')
EMBEDDING_DIM = int(os.getenv('EMBEDDING_DIM', '1024'))

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

async def verify_tables_exist(pool):
    """Verify all required tables exist and have data."""
    tables = [
        'embeddings.multimodal_embeddings',
        'embeddings.multimodal_embeddings_chunks',
        'metadata.frame_details_full',
        'metadata.frame_details_chunks',
        'metadata.process_frames_chunks'
    ]
    
    all_exist = True
    async with pool.acquire() as conn:
        logger.info("Verifying tables exist and have data:")
        for table in tables:
            # Check if table exists
            exists = await conn.fetchval('''
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = $1 AND table_name = $2
                )
            ''', table.split('.')[0], table.split('.')[1])
            
            if not exists:
                logger.error(f"❌ Table {table} does not exist")
                all_exist = False
                continue
            
            # Check if table has data
            count = await conn.fetchval(f'SELECT COUNT(*) FROM {table}')
            if count == 0:
                logger.warning(f"⚠️ Table {table} exists but is empty")
            else:
                logger.info(f"✅ Table {table} exists with {count} rows")
    
    return all_exist

async def verify_reference_id_format(pool):
    """Verify all reference IDs follow the correct format."""
    frame_pattern = re.compile(r'^[^/]+_[^/]+$')  # folder_name_frame_name
    chunk_pattern = re.compile(r'^.+_chunk_\d+$')  # Any_reference_chunk_NUMBER
    
    valid_formats = True
    async with pool.acquire() as conn:
        logger.info("\nVerifying reference ID formats:")
        
        # Check frame reference IDs in multimodal_embeddings
        frame_refs = await conn.fetch('''
            SELECT reference_id FROM embeddings.multimodal_embeddings
            WHERE reference_type = 'frame'
        ''')
        
        invalid_frame_refs = []
        for row in frame_refs:
            ref_id = row['reference_id']
            if not frame_pattern.match(ref_id) or '/' in ref_id:
                invalid_frame_refs.append(ref_id)
        
        # Check chunk reference IDs in multimodal_embeddings
        chunk_refs = await conn.fetch('''
            SELECT reference_id FROM embeddings.multimodal_embeddings
            WHERE reference_type = 'chunk'
        ''')
        
        invalid_chunk_refs = []
        for row in chunk_refs:
            ref_id = row['reference_id']
            if not chunk_pattern.match(ref_id) or '/' in ref_id:
                invalid_chunk_refs.append(ref_id)
        
        # Check frame reference IDs in frame_details_full
        metadata_frame_refs = await conn.fetch('''
            SELECT reference_id FROM metadata.frame_details_full
        ''')
        
        invalid_metadata_frames = []
        for row in metadata_frame_refs:
            ref_id = row['reference_id']
            if not frame_pattern.match(ref_id) or '/' in ref_id:
                invalid_metadata_frames.append(ref_id)
        
        # Check chunk reference IDs in frame_details_chunks
        metadata_chunk_refs = await conn.fetch('''
            SELECT reference_id FROM metadata.frame_details_chunks
        ''')
        
        invalid_metadata_chunks = []
        for row in metadata_chunk_refs:
            ref_id = row['reference_id']
            if not chunk_pattern.match(ref_id) or '/' in ref_id:
                invalid_metadata_chunks.append(ref_id)
        
        # Report results
        if invalid_frame_refs:
            logger.error(f"❌ Found {len(invalid_frame_refs)} invalid frame reference IDs in multimodal_embeddings")
            for ref in invalid_frame_refs[:5]:  # Show only first 5
                logger.error(f"   - {ref}")
            if len(invalid_frame_refs) > 5:
                logger.error(f"   - ... and {len(invalid_frame_refs) - 5} more")
            valid_formats = False
        else:
            logger.info(f"✅ All {len(frame_refs)} frame reference IDs in multimodal_embeddings are valid")
        
        if invalid_chunk_refs:
            logger.error(f"❌ Found {len(invalid_chunk_refs)} invalid chunk reference IDs in multimodal_embeddings")
            for ref in invalid_chunk_refs[:5]:
                logger.error(f"   - {ref}")
            if len(invalid_chunk_refs) > 5:
                logger.error(f"   - ... and {len(invalid_chunk_refs) - 5} more")
            valid_formats = False
        else:
            logger.info(f"✅ All {len(chunk_refs)} chunk reference IDs in multimodal_embeddings are valid")
        
        if invalid_metadata_frames:
            logger.error(f"❌ Found {len(invalid_metadata_frames)} invalid frame reference IDs in frame_details_full")
            for ref in invalid_metadata_frames[:5]:
                logger.error(f"   - {ref}")
            if len(invalid_metadata_frames) > 5:
                logger.error(f"   - ... and {len(invalid_metadata_frames) - 5} more")
            valid_formats = False
        else:
            logger.info(f"✅ All {len(metadata_frame_refs)} frame reference IDs in frame_details_full are valid")
        
        if invalid_metadata_chunks:
            logger.error(f"❌ Found {len(invalid_metadata_chunks)} invalid chunk reference IDs in frame_details_chunks")
            for ref in invalid_metadata_chunks[:5]:
                logger.error(f"   - {ref}")
            if len(invalid_metadata_chunks) > 5:
                logger.error(f"   - ... and {len(invalid_metadata_chunks) - 5} more")
            valid_formats = False
        else:
            logger.info(f"✅ All {len(metadata_chunk_refs)} chunk reference IDs in frame_details_chunks are valid")
    
    return valid_formats

async def verify_reference_id_consistency(pool):
    """Verify that reference IDs are consistent across schemas."""
    consistent = True
    async with pool.acquire() as conn:
        logger.info("\nVerifying reference ID consistency across schemas:")
        
        # Compare frame reference IDs between multimodal_embeddings and frame_details_full
        frames_in_embeddings = set([row['reference_id'] for row in await conn.fetch('''
            SELECT reference_id FROM embeddings.multimodal_embeddings
            WHERE reference_type = 'frame'
        ''')])
        
        frames_in_metadata = set([row['reference_id'] for row in await conn.fetch('''
            SELECT reference_id FROM metadata.frame_details_full
        ''')])
        
        missing_in_metadata = frames_in_embeddings - frames_in_metadata
        missing_in_embeddings = frames_in_metadata - frames_in_embeddings
        
        # Compare chunk reference IDs between multimodal_embeddings and frame_details_chunks
        chunks_in_embeddings = set([row['reference_id'] for row in await conn.fetch('''
            SELECT reference_id FROM embeddings.multimodal_embeddings
            WHERE reference_type = 'chunk'
        ''')])
        
        chunks_in_metadata = set([row['reference_id'] for row in await conn.fetch('''
            SELECT reference_id FROM metadata.frame_details_chunks
        ''')])
        
        missing_chunks_in_metadata = chunks_in_embeddings - chunks_in_metadata
        missing_chunks_in_embeddings = chunks_in_metadata - chunks_in_embeddings
        
        # Compare chunk reference IDs between multimodal_embeddings_chunks and frame_details_chunks
        chunks_in_mm_chunks = set([row['reference_id'] for row in await conn.fetch('''
            SELECT reference_id FROM embeddings.multimodal_embeddings_chunks
        ''')])
        
        missing_chunks_in_mm_chunks = chunks_in_metadata - chunks_in_mm_chunks
        missing_chunks_in_metadata_from_mm = chunks_in_mm_chunks - chunks_in_metadata
        
        # Report results
        if missing_in_metadata:
            logger.warning(f"⚠️ Found {len(missing_in_metadata)} frame reference IDs in embeddings but not in metadata")
            for ref in list(missing_in_metadata)[:5]:
                logger.warning(f"   - {ref}")
            if len(missing_in_metadata) > 5:
                logger.warning(f"   - ... and {len(missing_in_metadata) - 5} more")
        else:
            logger.info("✅ All frame reference IDs in embeddings exist in metadata")
        
        if missing_in_embeddings:
            logger.warning(f"⚠️ Found {len(missing_in_embeddings)} frame reference IDs in metadata but not in embeddings")
            for ref in list(missing_in_embeddings)[:5]:
                logger.warning(f"   - {ref}")
            if len(missing_in_embeddings) > 5:
                logger.warning(f"   - ... and {len(missing_in_embeddings) - 5} more")
        else:
            logger.info("✅ All frame reference IDs in metadata exist in embeddings")
        
        if missing_chunks_in_metadata:
            logger.warning(f"⚠️ Found {len(missing_chunks_in_metadata)} chunk reference IDs in embeddings but not in metadata")
            for ref in list(missing_chunks_in_metadata)[:5]:
                logger.warning(f"   - {ref}")
            if len(missing_chunks_in_metadata) > 5:
                logger.warning(f"   - ... and {len(missing_chunks_in_metadata) - 5} more")
        else:
            logger.info("✅ All chunk reference IDs in embeddings exist in metadata")
        
        if missing_chunks_in_embeddings:
            logger.warning(f"⚠️ Found {len(missing_chunks_in_embeddings)} chunk reference IDs in metadata but not in embeddings")
            for ref in list(missing_chunks_in_embeddings)[:5]:
                logger.warning(f"   - {ref}")
            if len(missing_chunks_in_embeddings) > 5:
                logger.warning(f"   - ... and {len(missing_chunks_in_embeddings) - 5} more")
        else:
            logger.info("✅ All chunk reference IDs in metadata exist in embeddings")
        
        if missing_chunks_in_mm_chunks:
            logger.warning(f"⚠️ Found {len(missing_chunks_in_mm_chunks)} chunk reference IDs in metadata but not in multimodal_embeddings_chunks")
            for ref in list(missing_chunks_in_mm_chunks)[:5]:
                logger.warning(f"   - {ref}")
            if len(missing_chunks_in_mm_chunks) > 5:
                logger.warning(f"   - ... and {len(missing_chunks_in_mm_chunks) - 5} more")
            consistent = False
        else:
            logger.info("✅ All chunk reference IDs in metadata exist in multimodal_embeddings_chunks")
        
        if missing_chunks_in_metadata_from_mm:
            logger.warning(f"⚠️ Found {len(missing_chunks_in_metadata_from_mm)} chunk reference IDs in multimodal_embeddings_chunks but not in metadata")
            for ref in list(missing_chunks_in_metadata_from_mm)[:5]:
                logger.warning(f"   - {ref}")
            if len(missing_chunks_in_metadata_from_mm) > 5:
                logger.warning(f"   - ... and {len(missing_chunks_in_metadata_from_mm) - 5} more")
            consistent = False
        else:
            logger.info("✅ All chunk reference IDs in multimodal_embeddings_chunks exist in metadata")
    
    return consistent

async def verify_chunk_parent_relationship(pool):
    """Verify that chunk reference IDs properly relate to their parent frames."""
    valid_relationships = True
    async with pool.acquire() as conn:
        logger.info("\nVerifying chunk to frame parent relationships:")
        
        # Get all chunks from metadata
        chunks = await conn.fetch('''
            SELECT chunk_id, reference_id FROM metadata.frame_details_chunks
        ''')
        
        invalid_chunks = []
        for chunk in chunks:
            chunk_ref_id = chunk['reference_id']
            
            # Extract parent frame reference ID
            match = re.match(r'(.+)_chunk_\d+$', chunk_ref_id)
            if not match:
                invalid_chunks.append((chunk_ref_id, "Invalid format"))
                continue
            
            frame_ref_id = match.group(1)
            
            # Check if parent frame exists
            frame_exists = await conn.fetchval('''
                SELECT EXISTS(
                    SELECT 1 FROM metadata.frame_details_full 
                    WHERE reference_id = $1
                )
            ''', frame_ref_id)
            
            if not frame_exists:
                invalid_chunks.append((chunk_ref_id, f"Missing parent frame: {frame_ref_id}"))
        
        if invalid_chunks:
            logger.error(f"❌ Found {len(invalid_chunks)} chunks with invalid parent relationships")
            for chunk, reason in invalid_chunks[:5]:
                logger.error(f"   - {chunk}: {reason}")
            if len(invalid_chunks) > 5:
                logger.error(f"   - ... and {len(invalid_chunks) - 5} more")
            valid_relationships = False
        else:
            logger.info(f"✅ All {len(chunks)} chunks have valid parent frame relationships")
    
    return valid_relationships

async def verify_embedding_vector_dimensions(pool):
    """Verify that embedding vectors have the correct dimensions."""
    valid_dimensions = True
    async with pool.acquire() as conn:
        logger.info("\nVerifying embedding vector dimensions:")
        
        # Check dimensions in multimodal_embeddings
        try:
            mm_dimensions = await conn.fetch('''
                SELECT dimension(embedding) as dim, count(*) 
                FROM embeddings.multimodal_embeddings 
                GROUP BY dimension(embedding)
            ''')
            
            for row in mm_dimensions:
                dim, count = row['dim'], row['count']
                if dim != EMBEDDING_DIM:
                    logger.error(f"❌ Found {count} embeddings with dimension {dim} in multimodal_embeddings (expected {EMBEDDING_DIM})")
                    valid_dimensions = False
                else:
                    logger.info(f"✅ Found {count} embeddings with correct dimension {dim} in multimodal_embeddings")
        except Exception as e:
            logger.error(f"Error checking multimodal_embeddings dimensions: {str(e)}")
            valid_dimensions = False
        
        # Check dimensions in multimodal_embeddings_chunks - use 'embedding' not 'embedding_vector'
        try:
            mm_chunks_dimensions = await conn.fetch('''
                SELECT dimension(embedding) as dim, count(*) 
                FROM embeddings.multimodal_embeddings_chunks 
                GROUP BY dimension(embedding)
            ''')
            
            for row in mm_chunks_dimensions:
                dim, count = row['dim'], row['count']
                if dim != EMBEDDING_DIM:
                    logger.error(f"❌ Found {count} embeddings with dimension {dim} in multimodal_embeddings_chunks (expected {EMBEDDING_DIM})")
                    valid_dimensions = False
                else:
                    logger.info(f"✅ Found {count} embeddings with correct dimension {dim} in multimodal_embeddings_chunks")
        except Exception as e:
            logger.error(f"Error checking multimodal_embeddings_chunks dimensions: {str(e)}")
            valid_dimensions = False
    
    return valid_dimensions

async def verify_chunk_id_consistency(pool):
    """Verify that chunk_id is consistent between tables."""
    consistent = True
    async with pool.acquire() as conn:
        logger.info("\nVerifying chunk_id consistency between tables:")
        
        # Check if chunk_id values in multimodal_embeddings_chunks match metadata.frame_details_chunks
        # Note that frame_id is the primary key in frame_details_chunks, and chunk_id is just a column
        chunks_data = await conn.fetch('''
            SELECT f.frame_id, f.chunk_id, f.reference_id, e.embedding_id
            FROM metadata.frame_details_chunks f
            LEFT JOIN embeddings.multimodal_embeddings_chunks e ON f.chunk_id = e.chunk_id
            WHERE e.embedding_id IS NULL
        ''')
        
        if chunks_data:
            logger.error(f"❌ Found {len(chunks_data)} chunks in metadata without matching embedding")
            for chunk in chunks_data[:5]:
                logger.error(f"   - Frame ID {chunk['frame_id']} with Chunk ID {chunk['chunk_id']} has no matching embedding")
            if len(chunks_data) > 5:
                logger.error(f"   - ... and {len(chunks_data) - 5} more")
            consistent = False
        else:
            logger.info("✅ All chunks in metadata have matching embeddings")
        
        # Check if processes are properly linked
        process_data = await conn.fetch('''
            SELECT f.frame_id, f.chunk_id, f.reference_id, p.id
            FROM metadata.frame_details_chunks f
            LEFT JOIN metadata.process_frames_chunks p ON f.chunk_id = p.chunk_id
            WHERE p.id IS NULL
        ''')
        
        if process_data:
            logger.error(f"❌ Found {len(process_data)} chunks in metadata without processing data")
            for chunk in process_data[:5]:
                logger.error(f"   - Frame ID {chunk['frame_id']} with Chunk ID {chunk['chunk_id']} has no processing data")
            if len(process_data) > 5:
                logger.error(f"   - ... and {len(process_data) - 5} more")
            consistent = False
        else:
            logger.info("✅ All chunks have processing data")
    
    return consistent

async def main():
    """Execute the verification process."""
    logger.info("Starting database verification...")
    
    # Create connection pool
    pool = await create_connection_pool()
    
    try:
        # Run verification steps
        tables_exist = await verify_tables_exist(pool)
        reference_format_valid = await verify_reference_id_format(pool)
        reference_consistency = await verify_reference_id_consistency(pool)
        parent_relationships = await verify_chunk_parent_relationship(pool)
        vector_dimensions = await verify_embedding_vector_dimensions(pool)
        chunk_consistency = await verify_chunk_id_consistency(pool)
        
        # Summarize verification results
        logger.info("\n=== Verification Summary ===")
        logger.info(f"Tables Exist and Have Data: {'✅ PASS' if tables_exist else '❌ FAIL'}")
        logger.info(f"Reference ID Format: {'✅ PASS' if reference_format_valid else '❌ FAIL'}")
        logger.info(f"Reference ID Consistency: {'✅ PASS' if reference_consistency else '⚠️ WARNING'}")
        logger.info(f"Chunk Parent Relationships: {'✅ PASS' if parent_relationships else '❌ FAIL'}")
        logger.info(f"Vector Dimensions: {'✅ PASS' if vector_dimensions else '❌ FAIL'}")
        logger.info(f"Chunk ID Consistency: {'✅ PASS' if chunk_consistency else '❌ FAIL'}")
        
        all_passed = tables_exist and reference_format_valid and parent_relationships and vector_dimensions and chunk_consistency
        logger.info(f"\nOverall Verification: {'✅ PASSED' if all_passed else '❌ FAILED'}")
        
        if not all_passed:
            logger.warning("Some verification checks failed. Please review the log for details.")
        else:
            logger.info("All critical verification checks passed!")
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        raise
    finally:
        # Close connection pool
        await pool.close()
        logger.info("PostgreSQL connection pool closed")

if __name__ == "__main__":
    asyncio.run(main()) 