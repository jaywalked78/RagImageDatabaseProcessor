#!/usr/bin/env python3
"""
Comprehensive data pipeline verification script.
Validates the integrity of the data pipeline from frames to chunks to embeddings,
identifying any gaps or inconsistencies in the data.
"""

import os
import sys
import logging
import asyncio
import json
from dotenv import load_dotenv
import asyncpg
from tabulate import tabulate
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("pipeline_verifier")

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

async def check_frames_to_chunks_integrity(pool):
    """Verify integrity between frames and chunks."""
    async with pool.acquire() as conn:
        logger.info("Checking frames to chunks integrity...")
        
        # Get counts for frames and chunks
        frames_count = await conn.fetchval("SELECT COUNT(*) FROM content.frames")
        chunks_count = await conn.fetchval("SELECT COUNT(*) FROM metadata.frame_details_chunks")
        
        logger.info(f"Found {frames_count} frames and {chunks_count} chunks")
        
        # Check frames without chunks
        frames_without_chunks = await conn.fetch("""
            SELECT f.frame_id
            FROM content.frames f
            LEFT JOIN metadata.frame_details_chunks c ON f.frame_id = c.frame_id
            WHERE c.chunk_id IS NULL
        """)
        
        if frames_without_chunks:
            logger.warning(f"Found {len(frames_without_chunks)} frames without chunks:")
            for frame in frames_without_chunks[:5]:  # Show first 5 examples
                logger.warning(f"  - Frame {frame['frame_id']} has no chunks")
        else:
            logger.info("All frames have associated chunks")
            
        # Check average number of chunks per frame
        if frames_count > 0:
            chunks_per_frame = await conn.fetch("""
                SELECT f.frame_id, COUNT(c.chunk_id) as chunk_count
                FROM content.frames f
                LEFT JOIN metadata.frame_details_chunks c ON f.frame_id = c.frame_id
                GROUP BY f.frame_id
                ORDER BY chunk_count DESC
            """)
            
            # Calculate stats
            counts = [row['chunk_count'] for row in chunks_per_frame]
            avg_chunks = sum(counts) / len(counts)
            max_chunks = max(counts) if counts else 0
            min_chunks = min(counts) if counts else 0
            
            logger.info(f"Chunks per frame: avg={avg_chunks:.2f}, min={min_chunks}, max={max_chunks}")
            
            # Show distribution
            distribution = {}
            for count in counts:
                distribution[count] = distribution.get(count, 0) + 1
                
            logger.info("Chunks per frame distribution:")
            for count, frames in sorted(distribution.items()):
                logger.info(f"  - {count} chunks: {frames} frames ({frames/frames_count*100:.1f}%)")

async def check_chunks_to_embeddings_integrity(pool):
    """Verify integrity between chunks and embeddings."""
    async with pool.acquire() as conn:
        logger.info("\nChecking chunks to embeddings integrity...")
        
        # Get counts for chunks and embeddings
        chunks_count = await conn.fetchval("SELECT COUNT(*) FROM metadata.frame_details_chunks")
        embeddings_count = await conn.fetchval("SELECT COUNT(*) FROM embeddings.multimodal_embeddings_chunks")
        
        logger.info(f"Found {chunks_count} chunks and {embeddings_count} embeddings")
        
        # Check chunks without embeddings
        chunks_without_embeddings = await conn.fetch("""
            SELECT c.chunk_id, c.frame_id
            FROM metadata.frame_details_chunks c
            LEFT JOIN embeddings.multimodal_embeddings_chunks e ON c.chunk_id = e.chunk_id
            WHERE e.embedding_id IS NULL
        """)
        
        if chunks_without_embeddings:
            logger.warning(f"Found {len(chunks_without_embeddings)} chunks without embeddings:")
            for chunk in chunks_without_embeddings[:5]:  # Show first 5 examples
                logger.warning(f"  - Chunk {chunk['chunk_id']} (Frame {chunk['frame_id']}) has no embeddings")
        else:
            logger.info("All chunks have associated embeddings")
            
        # Check embeddings without valid chunks
        embeddings_without_valid_chunks = await conn.fetch("""
            SELECT e.embedding_id, e.chunk_id, e.reference_id
            FROM embeddings.multimodal_embeddings_chunks e
            LEFT JOIN metadata.frame_details_chunks c ON e.chunk_id = c.chunk_id
            WHERE c.chunk_id IS NULL
        """)
        
        if embeddings_without_valid_chunks:
            logger.warning(f"Found {len(embeddings_without_valid_chunks)} embeddings without valid chunks:")
            for embedding in embeddings_without_valid_chunks[:5]:  # Show first 5 examples
                logger.warning(f"  - Embedding {embedding['embedding_id']} references invalid chunk {embedding['chunk_id']}")
        else:
            logger.info("All embeddings reference valid chunks")
            
        # Check average number of embeddings per chunk
        embeddings_per_chunk = await conn.fetch("""
            SELECT c.chunk_id, COUNT(e.embedding_id) as embedding_count
            FROM metadata.frame_details_chunks c
            LEFT JOIN embeddings.multimodal_embeddings_chunks e ON c.chunk_id = e.chunk_id
            GROUP BY c.chunk_id
            ORDER BY embedding_count DESC
        """)
        
        # Calculate stats
        counts = [row['embedding_count'] for row in embeddings_per_chunk]
        if counts:
            avg_embeddings = sum(counts) / len(counts)
            max_embeddings = max(counts)
            min_embeddings = min(counts)
            
            logger.info(f"Embeddings per chunk: avg={avg_embeddings:.2f}, min={min_embeddings}, max={max_embeddings}")
            
            # Show distribution
            distribution = {}
            for count in counts:
                distribution[count] = distribution.get(count, 0) + 1
                
            logger.info("Embeddings per chunk distribution:")
            for count, chunks in sorted(distribution.items()):
                logger.info(f"  - {count} embeddings: {chunks} chunks ({chunks/chunks_count*100:.1f}%)")

async def check_reference_ids_consistency(pool):
    """Verify consistency of reference IDs across tables."""
    async with pool.acquire() as conn:
        logger.info("\nChecking reference IDs consistency...")
        
        # Check frames reference IDs format
        frame_reference_ids = await conn.fetch("""
            SELECT frame_id, reference_id
            FROM metadata.frame_details_full
            LIMIT 5
        """)
        
        if frame_reference_ids:
            logger.info("Sample frame reference IDs:")
            for frame in frame_reference_ids:
                logger.info(f"  - Frame {frame['frame_id']}: {frame['reference_id']}")
                
        # Check chunks reference IDs format
        chunk_reference_ids = await conn.fetch("""
            SELECT chunk_id, frame_id, reference_id
            FROM metadata.frame_details_chunks
            LIMIT 5
        """)
        
        if chunk_reference_ids:
            logger.info("Sample chunk reference IDs:")
            for chunk in chunk_reference_ids:
                logger.info(f"  - Chunk {chunk['chunk_id']} (Frame {chunk['frame_id']}): {chunk['reference_id']}")
                
        # Check embeddings reference IDs format
        embedding_reference_ids = await conn.fetch("""
            SELECT embedding_id, chunk_id, reference_id
            FROM embeddings.multimodal_embeddings_chunks
            LIMIT 5
        """)
        
        if embedding_reference_ids:
            logger.info("Sample embedding reference IDs:")
            for embedding in embedding_reference_ids:
                logger.info(f"  - Embedding {embedding['embedding_id']} (Chunk {embedding['chunk_id']}): {embedding['reference_id']}")
                
        # Check for consistency between frame and chunk reference IDs
        inconsistent_chunk_refs = await conn.fetch("""
            SELECT c.chunk_id, c.frame_id, f.reference_id AS frame_ref, c.reference_id AS chunk_ref
            FROM metadata.frame_details_chunks c
            JOIN metadata.frame_details_full f ON c.frame_id = f.frame_id
            WHERE NOT c.reference_id LIKE f.reference_id || '\_%'
            LIMIT 10
        """)
        
        if inconsistent_chunk_refs:
            logger.warning(f"Found {len(inconsistent_chunk_refs)} chunks with inconsistent reference IDs:")
            for chunk in inconsistent_chunk_refs:
                logger.warning(f"  - Chunk {chunk['chunk_id']} (Frame {chunk['frame_id']}): {chunk['chunk_ref']} does not match frame {chunk['frame_ref']}")
        else:
            logger.info("All chunk reference IDs are consistent with their parent frame reference IDs")
            
        # Check for consistency between chunk and embedding reference IDs
        inconsistent_embedding_refs = await conn.fetch("""
            SELECT e.embedding_id, e.chunk_id, c.reference_id AS chunk_ref, e.reference_id AS embedding_ref
            FROM embeddings.multimodal_embeddings_chunks e
            JOIN metadata.frame_details_chunks c ON e.chunk_id = c.chunk_id
            WHERE e.reference_id != c.reference_id
            LIMIT 10
        """)
        
        if inconsistent_embedding_refs:
            logger.warning(f"Found {len(inconsistent_embedding_refs)} embeddings with inconsistent reference IDs:")
            for embedding in inconsistent_embedding_refs:
                logger.warning(f"  - Embedding {embedding['embedding_id']} (Chunk {embedding['chunk_id']}): {embedding['embedding_ref']} does not match chunk {embedding['chunk_ref']}")
        else:
            logger.info("All embedding reference IDs are consistent with their chunk reference IDs")

async def check_metadata_completeness(pool):
    """Verify completeness of metadata in all tables."""
    async with pool.acquire() as conn:
        logger.info("\nChecking metadata completeness...")
        
        # Check frames with missing metadata
        frames_missing_metadata = await conn.fetch("""
            SELECT f.frame_id
            FROM content.frames f
            LEFT JOIN metadata.frame_details_full m ON f.frame_id = m.frame_id
            WHERE m.frame_id IS NULL
               OR m.description IS NULL
               OR m.workflow_stage IS NULL
        """)
        
        if frames_missing_metadata:
            logger.warning(f"Found {len(frames_missing_metadata)} frames with missing metadata:")
            for frame in frames_missing_metadata[:5]:  # Show first 5 examples
                logger.warning(f"  - Frame {frame['frame_id']} has incomplete metadata")
        else:
            logger.info("All frames have complete metadata")
            
        # Check chunks with missing metadata
        chunks_missing_metadata = await conn.fetch("""
            SELECT c.chunk_id, c.frame_id
            FROM metadata.frame_details_chunks c
            WHERE c.description IS NULL
               OR c.workflow_stage IS NULL
        """)
        
        if chunks_missing_metadata:
            logger.warning(f"Found {len(chunks_missing_metadata)} chunks with missing metadata:")
            for chunk in chunks_missing_metadata[:5]:  # Show first 5 examples
                logger.warning(f"  - Chunk {chunk['chunk_id']} (Frame {chunk['frame_id']}) has incomplete metadata")
        else:
            logger.info("All chunks have complete metadata")
            
        # Check for empty vectors in embeddings
        embeddings_missing_vectors = await conn.fetch("""
            SELECT embedding_id, chunk_id
            FROM embeddings.multimodal_embeddings_chunks
            WHERE embedding IS NULL
        """)
        
        if embeddings_missing_vectors:
            logger.warning(f"Found {len(embeddings_missing_vectors)} embeddings with missing vectors:")
            for embedding in embeddings_missing_vectors[:5]:  # Show first 5 examples
                logger.warning(f"  - Embedding {embedding['embedding_id']} (Chunk {embedding['chunk_id']}) has no vector")
        else:
            logger.info("All embeddings have vectors")

async def check_sensitive_info_consistency(pool):
    """Verify consistency of sensitive information flags across tables."""
    async with pool.acquire() as conn:
        logger.info("\nChecking sensitive information consistency...")
        
        # Check frames with sensitive info
        try:
            frames_with_sensitive_info = await conn.fetch("""
                SELECT frame_id, technical_details->>'sensitive_info_detected' as has_sensitive
                FROM metadata.frame_details_full
                WHERE technical_details->>'sensitive_info_detected' = 'true'
            """)
            
            if frames_with_sensitive_info:
                logger.info(f"Found {len(frames_with_sensitive_info)} frames with sensitive information:")
                for frame in frames_with_sensitive_info[:5]:  # Show first 5 examples
                    logger.info(f"  - Frame {frame['frame_id']} contains sensitive information")
                    
                # Check if sensitive info in frames propagated to chunks
                for frame in frames_with_sensitive_info[:3]:  # Check first 3 examples
                    frame_id = frame['frame_id']
                    chunks = await conn.fetch("""
                        SELECT chunk_id, technical_details->>'sensitive_info_detected' as has_sensitive
                        FROM metadata.frame_details_chunks
                        WHERE frame_id = $1
                    """, frame_id)
                    
                    sensitive_chunks = [c for c in chunks if c['has_sensitive'] == 'true']
                    logger.info(f"  - Frame {frame_id} has {len(sensitive_chunks)} of {len(chunks)} chunks with sensitive info")
            else:
                logger.info("No frames with sensitive information found")
        except Exception as e:
            logger.error(f"Error checking sensitive information: {str(e)}")

async def main():
    """Main function."""
    logger.info("Starting comprehensive data pipeline verification...")
    
    try:
        # Create connection pool
        pool = await create_connection_pool()
        
        # Run each verification check
        try:
            await check_frames_to_chunks_integrity(pool)
        except Exception as e:
            logger.error(f"Error checking frames to chunks integrity: {str(e)}")
        
        try:
            await check_chunks_to_embeddings_integrity(pool)
        except Exception as e:
            logger.error(f"Error checking chunks to embeddings integrity: {str(e)}")
        
        try:
            await check_reference_ids_consistency(pool)
        except Exception as e:
            logger.error(f"Error checking reference IDs consistency: {str(e)}")
        
        try:
            await check_metadata_completeness(pool)
        except Exception as e:
            logger.error(f"Error checking metadata completeness: {str(e)}")
        
        try:
            await check_sensitive_info_consistency(pool)
        except Exception as e:
            logger.error(f"Error checking sensitive info consistency: {str(e)}")
        
        # Close the connection pool
        await pool.close()
        logger.info("\nData pipeline verification complete")
        logger.info("PostgreSQL connection pool closed")
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        
if __name__ == "__main__":
    asyncio.run(main()) 