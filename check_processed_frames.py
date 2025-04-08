#!/usr/bin/env python3
"""
Script to check the processing status of the earliest 5 frames
that were targeted by process_earliest_frames.py
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
logger = logging.getLogger("processed_frames_check")

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

async def get_earliest_frames(pool, limit=5):
    """Get the earliest frames by created_at timestamp."""
    async with pool.acquire() as conn:
        logger.info(f"Retrieving the {limit} earliest frames...")
        
        # Query to get earliest frames
        frames = await conn.fetch("""
            SELECT 
                frame_id, 
                folder_name, 
                file_name, 
                created_at
            FROM content.frames
            ORDER BY created_at ASC
            LIMIT $1
        """, limit)
        
        if not frames:
            logger.warning("No frames found in the database!")
            return []
            
        logger.info(f"Found {len(frames)} earliest frames:")
        
        # Display frames
        headers = ["frame_id", "folder_name", "created_at"]
        data = [[frame['frame_id'], frame['folder_name'], frame['created_at']] for frame in frames]
        logger.info("\n" + tabulate(data, headers=headers))
        
        return frames

async def check_frame_processing(pool, frame_ids):
    """Check if frames have corresponding metadata, chunks, and embeddings."""
    results = []
    
    for frame_id in frame_ids:
        result = {
            "frame_id": frame_id,
            "has_metadata": False,
            "has_chunks": False,
            "has_embeddings": False,
            "metadata_updated": None,  # To track technical_details updated timestamp
            "chunk_ids": [],
            "embedding_ids": []
        }
        
        async with pool.acquire() as conn:
            # Check metadata
            metadata = await conn.fetchrow("""
                SELECT technical_details, workflow_stage
                FROM metadata.frame_details_full
                WHERE frame_id = $1
            """, frame_id)
            
            if metadata:
                result["has_metadata"] = True
                result["workflow_stage"] = metadata["workflow_stage"]
                
                # Handle technical_details differently based on type
                tech_details = metadata["technical_details"]
                if tech_details:
                    try:
                        # If it's a string, try to parse it as JSON
                        if isinstance(tech_details, str):
                            tech_details = json.loads(tech_details)
                        
                        # If we have a processed_timestamp, get it
                        if isinstance(tech_details, dict) and "processed_timestamp" in tech_details:
                            result["metadata_updated"] = tech_details["processed_timestamp"]
                    except (json.JSONDecodeError, TypeError):
                        result["metadata_updated"] = "Invalid JSON format"
                
            # Check chunks
            chunks = await conn.fetch("""
                SELECT chunk_id
                FROM metadata.frame_details_chunks
                WHERE frame_id = $1
            """, frame_id)
            
            if chunks:
                result["has_chunks"] = True
                result["chunk_ids"] = [c["chunk_id"] for c in chunks]
                
                # Check embeddings for each chunk
                all_chunk_embeddings = []
                for chunk in chunks:
                    chunk_id = chunk["chunk_id"]
                    embeddings = await conn.fetch("""
                        SELECT embedding_id
                        FROM embeddings.multimodal_embeddings_chunks
                        WHERE chunk_id = $1
                    """, chunk_id)
                    
                    if embeddings:
                        all_chunk_embeddings.extend([e["embedding_id"] for e in embeddings])
                
                if all_chunk_embeddings:
                    result["has_embeddings"] = True
                    result["embedding_ids"] = all_chunk_embeddings
        
        results.append(result)
    
    return results

async def display_processing_results(results):
    """Display the processing results in a table."""
    headers = ["Frame ID", "Has Metadata", "Has Chunks", "Has Embeddings", "Workflow Stage", "Metadata Updated"]
    data = []
    
    for r in results:
        data.append([
            r["frame_id"],
            r["has_metadata"],
            f"{r['has_chunks']} ({len(r['chunk_ids'])})",
            f"{r['has_embeddings']} ({len(r['embedding_ids'])})",
            r.get("workflow_stage", "N/A"),
            r.get("metadata_updated", "N/A")
        ])
    
    logger.info("\nProcessing Status:")
    logger.info("\n" + tabulate(data, headers=headers))
    
    # Check if all frames are fully processed
    all_processed = all([
        r["has_metadata"] and r["has_chunks"] and r["has_embeddings"]
        for r in results
    ])
    
    logger.info(f"\nAll frames are fully processed: {all_processed}")
    return all_processed

async def main():
    """Main function."""
    logger.info("Starting to check the earliest 5 processed frames...")
    
    try:
        # Create connection pool
        pool = await create_connection_pool()
        
        # Get earliest frames
        frames = await get_earliest_frames(pool, limit=5)
        if not frames:
            await pool.close()
            return False
        
        # Extract frame IDs
        frame_ids = [frame["frame_id"] for frame in frames]
        
        # Check if each frame has been fully processed
        processing_results = await check_frame_processing(pool, frame_ids)
        
        # Display results
        success = await display_processing_results(processing_results)
        
        # Close the connection pool
        await pool.close()
        logger.info("Check completed. PostgreSQL connection pool closed.")
        
        return success
        
    except Exception as e:
        logger.error(f"Error during check: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 