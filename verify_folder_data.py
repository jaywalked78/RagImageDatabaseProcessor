#!/usr/bin/env python3
"""
Script to verify data for a specific folder in Supabase database.
Checks frames, chunks, and embeddings for a given folder name or pattern.
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
logger = logging.getLogger("folder_verifier")

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

async def get_available_folders(pool):
    """Get list of available folders in the database."""
    async with pool.acquire() as conn:
        folders = await conn.fetch("""
            SELECT DISTINCT folder_name
            FROM content.frames
            ORDER BY folder_name
        """)
        
        if not folders:
            logger.warning("No folders found in the database!")
            return []
            
        return [folder['folder_name'] for folder in folders]

async def check_folder_frames(pool, folder_name):
    """Check frames for a specific folder."""
    async with pool.acquire() as conn:
        logger.info(f"Checking frames for folder: {folder_name}")
        
        # Count frames
        frames_count = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM content.frames 
            WHERE folder_name = $1
        """, folder_name)
        
        logger.info(f"Found {frames_count} frames in folder {folder_name}")
        
        # Get sample frames
        frames = await conn.fetch("""
            SELECT frame_id, file_name, image_url, created_at
            FROM content.frames
            WHERE folder_name = $1
            ORDER BY frame_id
            LIMIT 10
        """, folder_name)
        
        if frames:
            # Display data
            headers = ["frame_id", "file_name", "image_url", "created_at"]
            data = [[frame['frame_id'], frame['file_name'], 
                    frame['image_url'][:50] + "..." if frame['image_url'] and len(frame['image_url']) > 50 else frame['image_url'],
                    frame['created_at']] for frame in frames]
            
            logger.info("Sample frames:")
            logger.info("\n" + tabulate(data, headers=headers))
        else:
            logger.warning(f"No frames found for folder {folder_name}!")
            
        return frames_count

async def check_folder_reference_ids(pool, folder_name):
    """Check reference IDs for a specific folder."""
    async with pool.acquire() as conn:
        logger.info(f"\nChecking reference IDs for folder: {folder_name}")
        
        # Get frames with reference IDs
        frames_with_refs = await conn.fetch("""
            SELECT f.frame_id, m.reference_id
            FROM content.frames f
            LEFT JOIN metadata.frame_details_full m ON f.frame_id = m.frame_id
            WHERE f.folder_name = $1
            ORDER BY f.frame_id
        """, folder_name)
        
        if not frames_with_refs:
            logger.warning(f"No frames with reference IDs found for folder {folder_name}!")
            return 0
            
        logger.info(f"Found {len(frames_with_refs)} frames with reference IDs")
        
        # Check if reference IDs match expected pattern
        correct_pattern = 0
        incorrect_pattern = 0
        
        for frame in frames_with_refs:
            if frame['reference_id'] is None:
                logger.warning(f"Frame {frame['frame_id']} has no reference ID")
                incorrect_pattern += 1
            elif frame['reference_id'].startswith(f"{folder_name}/"):
                correct_pattern += 1
            else:
                logger.warning(f"Frame {frame['frame_id']} has incorrect reference ID format: {frame['reference_id']}")
                incorrect_pattern += 1
                
        logger.info(f"Reference ID check: {correct_pattern} correct, {incorrect_pattern} incorrect")
        
        # Show sample reference IDs
        if frames_with_refs:
            headers = ["frame_id", "reference_id"]
            data = [[frame['frame_id'], frame['reference_id']] for frame in frames_with_refs[:5]]
            
            logger.info("Sample frame reference IDs:")
            logger.info("\n" + tabulate(data, headers=headers))
            
        return len(frames_with_refs)

async def check_folder_chunks(pool, folder_name):
    """Check chunks for a specific folder."""
    async with pool.acquire() as conn:
        logger.info(f"\nChecking chunks for folder: {folder_name}")
        
        # Get frames for this folder
        frames = await conn.fetch("""
            SELECT frame_id
            FROM content.frames
            WHERE folder_name = $1
        """, folder_name)
        
        if not frames:
            logger.warning(f"No frames found for folder {folder_name}, cannot check chunks!")
            return 0
            
        # Get frame IDs list
        frame_ids = [frame['frame_id'] for frame in frames]
        
        # Use ANY to match against the array of frame_ids
        chunks = await conn.fetch("""
            SELECT c.chunk_id, c.frame_id, c.reference_id, c.workflow_stage
            FROM metadata.frame_details_chunks c
            WHERE c.frame_id = ANY($1)
            ORDER BY c.frame_id, c.chunk_id
        """, frame_ids)
        
        logger.info(f"Found {len(chunks)} chunks for {len(frames)} frames in folder {folder_name}")
        
        # Calculate chunks per frame
        if len(frames) > 0:
            chunks_per_frame = len(chunks) / len(frames)
            logger.info(f"Average chunks per frame: {chunks_per_frame:.2f}")
            
        # Check if all frames have chunks
        frames_with_chunks = set(chunk['frame_id'] for chunk in chunks)
        frames_without_chunks = [frame_id for frame_id in frame_ids if frame_id not in frames_with_chunks]
        
        if frames_without_chunks:
            logger.warning(f"Found {len(frames_without_chunks)} frames without chunks:")
            for frame_id in frames_without_chunks[:5]:  # Show first 5
                logger.warning(f"  - Frame {frame_id} has no chunks")
        else:
            logger.info("All frames have at least one chunk")
            
        # Show sample chunks
        if chunks:
            headers = ["chunk_id", "frame_id", "reference_id", "workflow_stage"]
            data = [[chunk['chunk_id'], chunk['frame_id'], chunk['reference_id'], chunk['workflow_stage']] 
                   for chunk in chunks[:5]]
            
            logger.info("Sample chunks:")
            logger.info("\n" + tabulate(data, headers=headers))
            
        return len(chunks)

async def check_folder_embeddings(pool, folder_name):
    """Check embeddings for a specific folder."""
    async with pool.acquire() as conn:
        logger.info(f"\nChecking embeddings for folder: {folder_name}")
        
        # Get embeddings with reference IDs that include the folder name
        embeddings = await conn.fetch("""
            SELECT e.embedding_id, e.chunk_id, e.reference_id, e.model_name
            FROM embeddings.multimodal_embeddings_chunks e
            WHERE e.reference_id LIKE $1
            ORDER BY e.reference_id
            LIMIT 100
        """, f"{folder_name}/%")
        
        logger.info(f"Found {len(embeddings)} embeddings with reference IDs containing folder {folder_name}")
        
        # Show sample embeddings
        if embeddings:
            headers = ["embedding_id", "chunk_id", "reference_id", "model_name"]
            data = [[emb['embedding_id'], emb['chunk_id'], emb['reference_id'], emb['model_name']] 
                   for emb in embeddings[:5]]
            
            logger.info("Sample embeddings:")
            logger.info("\n" + tabulate(data, headers=headers))
            
        # Check for duplicate embeddings (same chunk_id)
        chunk_counts = {}
        for emb in embeddings:
            chunk_id = emb['chunk_id']
            chunk_counts[chunk_id] = chunk_counts.get(chunk_id, 0) + 1
            
        duplicates = {chunk_id: count for chunk_id, count in chunk_counts.items() if count > 1}
        if duplicates:
            logger.warning(f"Found {len(duplicates)} chunks with multiple embeddings:")
            for chunk_id, count in list(duplicates.items())[:5]:  # Show first 5
                logger.warning(f"  - Chunk {chunk_id} has {count} embeddings")
                
                # Show the duplicate embeddings for this chunk
                chunk_embeddings = [emb for emb in embeddings if emb['chunk_id'] == chunk_id]
                for emb in chunk_embeddings:
                    logger.warning(f"      - Embedding ID: {emb['embedding_id']}, Reference: {emb['reference_id']}")
        else:
            logger.info("No duplicate embeddings found")
            
        # Check for orphaned embeddings (invalid chunk_id - not in metadata.frame_details_chunks)
        orphaned_embeddings = await conn.fetch("""
            SELECT e.embedding_id, e.chunk_id, e.reference_id
            FROM embeddings.multimodal_embeddings_chunks e
            LEFT JOIN metadata.frame_details_chunks c ON e.chunk_id = c.chunk_id
            WHERE e.reference_id LIKE $1
            AND c.chunk_id IS NULL
        """, f"{folder_name}/%")
        
        if orphaned_embeddings:
            logger.warning(f"Found {len(orphaned_embeddings)} orphaned embeddings:")
            for emb in orphaned_embeddings[:5]:  # Show first 5
                logger.warning(f"  - Embedding {emb['embedding_id']} references invalid chunk {emb['chunk_id']}")
        else:
            logger.info("No orphaned embeddings found")
            
        return len(embeddings)

async def main():
    """Main function."""
    logger.info("Starting folder data verification...")
    
    try:
        # Create connection pool
        pool = await create_connection_pool()
        
        # Get available folders
        folders = await get_available_folders(pool)
        
        if not folders:
            logger.error("No folders found in the database. Exiting.")
            await pool.close()
            return
            
        logger.info(f"Found {len(folders)} folders in the database:")
        for folder in folders:
            logger.info(f"  - {folder}")
            
        # Process each folder or ask user to select one
        if len(folders) == 1:
            # If only one folder, use it automatically
            selected_folder = folders[0]
        else:
            # Use the most recent folder (assuming it's the test folder)
            selected_folder = folders[-1]
            
        logger.info(f"\nVerifying data for folder: {selected_folder}")
        
        # Run verification for the selected folder
        frames_count = await check_folder_frames(pool, selected_folder)
        refs_count = await check_folder_reference_ids(pool, selected_folder)
        chunks_count = await check_folder_chunks(pool, selected_folder)
        embeddings_count = await check_folder_embeddings(pool, selected_folder)
        
        # Summary
        logger.info("\nSummary for folder: " + selected_folder)
        logger.info(f"  - {frames_count} frames")
        logger.info(f"  - {refs_count} frames with reference IDs")
        logger.info(f"  - {chunks_count} chunks")
        logger.info(f"  - {embeddings_count} embeddings")
        
        # Check if everything lines up
        if frames_count > 0:
            frames_to_chunks = chunks_count / frames_count
            logger.info(f"  - Chunks per frame: {frames_to_chunks:.2f}")
            
            if chunks_count > 0:
                chunks_to_embeddings = embeddings_count / chunks_count
                logger.info(f"  - Embeddings per chunk: {chunks_to_embeddings:.2f}")
                
        # Close the connection pool
        await pool.close()
        logger.info("\nFolder data verification complete")
        logger.info("PostgreSQL connection pool closed")
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        
if __name__ == "__main__":
    asyncio.run(main()) 