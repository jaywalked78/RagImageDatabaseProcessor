#!/usr/bin/env python3
"""
Script to clean up orphaned embeddings in Supabase database.
Identifies and removes embeddings that reference non-existent chunks.
"""

import os
import sys
import logging
import asyncio
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
logger = logging.getLogger("embedding_cleaner")

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-us-east-1.pooler.supabase.com')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')

# Safety flag - set to True to actually delete orphaned embeddings
DELETE_ORPHANED_EMBEDDINGS = True

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

async def identify_orphaned_embeddings(pool, folder_name=None):
    """Identify embeddings that reference non-existent chunks."""
    async with pool.acquire() as conn:
        logger.info("Identifying orphaned embeddings...")
        
        # Build query based on whether a folder name is provided
        query = """
            SELECT e.embedding_id, e.chunk_id, e.reference_id, e.model_name
            FROM embeddings.multimodal_embeddings_chunks e
            LEFT JOIN metadata.frame_details_chunks c ON e.chunk_id = c.chunk_id
            WHERE c.chunk_id IS NULL
        """
        
        params = []
        if folder_name:
            query += " AND e.reference_id LIKE $1"
            params.append(f"{folder_name}/%")
            
        # Add order and limit
        query += " ORDER BY e.reference_id LIMIT 1000"
        
        # Execute query
        orphaned_embeddings = await conn.fetch(query, *params)
        
        if not orphaned_embeddings:
            logger.info("No orphaned embeddings found.")
            return []
            
        logger.info(f"Found {len(orphaned_embeddings)} orphaned embeddings.")
        
        # Display sample of orphaned embeddings
        if orphaned_embeddings:
            headers = ["embedding_id", "chunk_id", "reference_id", "model_name"]
            data = [[emb['embedding_id'], emb['chunk_id'], emb['reference_id'], emb['model_name']] 
                   for emb in orphaned_embeddings[:10]]  # Show first 10
            
            logger.info("Sample orphaned embeddings:")
            logger.info("\n" + tabulate(data, headers=headers))
            
        return orphaned_embeddings

async def find_duplicate_embeddings(pool):
    """Find embeddings that have duplicates (multiple embeddings for the same chunk)."""
    async with pool.acquire() as conn:
        logger.info("\nChecking for duplicate embeddings...")
        
        # Query to find chunks with multiple embeddings
        duplicates = await conn.fetch("""
            SELECT chunk_id, COUNT(*) as count
            FROM embeddings.multimodal_embeddings_chunks
            GROUP BY chunk_id
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 100
        """)
        
        if not duplicates:
            logger.info("No chunks with duplicate embeddings found.")
            return []
            
        logger.info(f"Found {len(duplicates)} chunks with multiple embeddings:")
        
        # Show details for each duplicate set
        duplicate_details = []
        for dup in duplicates[:10]:  # Process first 10 duplicate sets
            chunk_id = dup['chunk_id']
            count = dup['count']
            logger.info(f"  - Chunk {chunk_id} has {count} embeddings")
            
            # Get the embeddings for this chunk
            chunk_embeddings = await conn.fetch("""
                SELECT embedding_id, reference_id, model_name, created_at
                FROM embeddings.multimodal_embeddings_chunks
                WHERE chunk_id = $1
                ORDER BY created_at DESC
            """, chunk_id)
            
            # Keep the newest one, mark others for deletion
            newest = chunk_embeddings[0]
            to_delete = chunk_embeddings[1:]
            
            logger.info(f"    - Keeping: {newest['embedding_id']} (created: {newest['created_at']})")
            for emb in to_delete:
                logger.info(f"    - Will delete: {emb['embedding_id']} (created: {emb['created_at']})")
                duplicate_details.append({
                    'embedding_id': emb['embedding_id'],
                    'chunk_id': chunk_id,
                    'reference_id': emb['reference_id'],
                    'model_name': emb['model_name'],
                    'created_at': emb['created_at']
                })
                
        return duplicate_details

async def delete_orphaned_embeddings(pool, orphaned_embeddings):
    """Delete orphaned embeddings from the database."""
    if not DELETE_ORPHANED_EMBEDDINGS:
        logger.warning("\nSAFETY FLAG IS OFF - No embeddings will be deleted.")
        logger.warning("To actually delete embeddings, set DELETE_ORPHANED_EMBEDDINGS = True in the script.")
        return 0
        
    if not orphaned_embeddings:
        logger.info("No orphaned embeddings to delete.")
        return 0
        
    async with pool.acquire() as conn:
        logger.info(f"\nDeleting {len(orphaned_embeddings)} orphaned embeddings...")
        
        # Get embedding IDs
        embedding_ids = [emb['embedding_id'] for emb in orphaned_embeddings]
        
        # Delete in batches to avoid potential issues with very large lists
        batch_size = 100
        deleted_count = 0
        
        for i in range(0, len(embedding_ids), batch_size):
            batch = embedding_ids[i:i+batch_size]
            result = await conn.execute("""
                DELETE FROM embeddings.multimodal_embeddings_chunks
                WHERE embedding_id = ANY($1)
            """, batch)
            
            # Parse result to get count (format: "DELETE count")
            try:
                count = int(result.split()[1])
                deleted_count += count
                logger.info(f"  - Deleted batch of {count} embeddings")
            except (IndexError, ValueError):
                logger.warning(f"  - Couldn't parse deletion count from result: {result}")
        
        logger.info(f"Successfully deleted {deleted_count} orphaned embeddings.")
        return deleted_count

async def delete_duplicate_embeddings(pool, duplicate_embeddings):
    """Delete duplicate embeddings from the database."""
    if not DELETE_ORPHANED_EMBEDDINGS:
        logger.warning("\nSAFETY FLAG IS OFF - No duplicate embeddings will be deleted.")
        logger.warning("To actually delete embeddings, set DELETE_ORPHANED_EMBEDDINGS = True in the script.")
        return 0
        
    if not duplicate_embeddings:
        logger.info("No duplicate embeddings to delete.")
        return 0
        
    async with pool.acquire() as conn:
        logger.info(f"\nDeleting {len(duplicate_embeddings)} duplicate embeddings...")
        
        # Get embedding IDs
        embedding_ids = [emb['embedding_id'] for emb in duplicate_embeddings]
        
        # Delete in batches
        batch_size = 100
        deleted_count = 0
        
        for i in range(0, len(embedding_ids), batch_size):
            batch = embedding_ids[i:i+batch_size]
            result = await conn.execute("""
                DELETE FROM embeddings.multimodal_embeddings_chunks
                WHERE embedding_id = ANY($1)
            """, batch)
            
            # Parse result
            try:
                count = int(result.split()[1])
                deleted_count += count
                logger.info(f"  - Deleted batch of {count} duplicate embeddings")
            except (IndexError, ValueError):
                logger.warning(f"  - Couldn't parse deletion count from result: {result}")
        
        logger.info(f"Successfully deleted {deleted_count} duplicate embeddings.")
        return deleted_count

async def main():
    """Main function."""
    logger.info("Starting orphaned embeddings cleanup...")
    
    try:
        # Create connection pool
        pool = await create_connection_pool()
        
        # Get available folders
        async with pool.acquire() as conn:
            folders = await conn.fetch("""
                SELECT DISTINCT folder_name
                FROM content.frames
                ORDER BY folder_name
            """)
            
            folder_names = [folder['folder_name'] for folder in folders]
            
        logger.info(f"Found {len(folder_names)} folders in the database:")
        for folder in folder_names:
            logger.info(f"  - {folder}")
            
        # Process each folder
        all_orphaned = []
        for folder in folder_names:
            logger.info(f"\nProcessing folder: {folder}")
            orphaned = await identify_orphaned_embeddings(pool, folder)
            all_orphaned.extend(orphaned)
            
        # Find duplicate embeddings
        duplicates = await find_duplicate_embeddings(pool)
        
        # Delete orphaned embeddings if flag is set
        deleted_orphaned = await delete_orphaned_embeddings(pool, all_orphaned)
        
        # Delete duplicate embeddings if flag is set
        deleted_duplicates = await delete_duplicate_embeddings(pool, duplicates)
        
        # Summary
        logger.info("\nCleanup Summary:")
        logger.info(f"  - Found {len(all_orphaned)} orphaned embeddings")
        logger.info(f"  - Found {len(duplicates)} duplicate embeddings")
        logger.info(f"  - Deleted {deleted_orphaned} orphaned embeddings")
        logger.info(f"  - Deleted {deleted_duplicates} duplicate embeddings")
        
        if not DELETE_ORPHANED_EMBEDDINGS and (all_orphaned or duplicates):
            logger.warning("\nNOTE: No deletions were performed because the safety flag is off.")
            logger.warning("To perform actual deletions, set DELETE_ORPHANED_EMBEDDINGS = True in the script.")
            
        # Close the connection pool
        await pool.close()
        logger.info("\nOrphaned embeddings cleanup complete")
        logger.info("PostgreSQL connection pool closed")
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        
if __name__ == "__main__":
    asyncio.run(main()) 