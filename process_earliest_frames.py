#!/usr/bin/env python3
"""
Script to process the earliest frames in the database.
"""

import os
import sys
import logging
import asyncio
import json
import datetime
import re
from dotenv import load_dotenv
import asyncpg
import uuid
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("process_frames")

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-us-east-1.pooler.supabase.com')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')

# Constants
EMBEDDING_DIM = 1024  # Dimension of the embedding vector

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
            SELECT frame_id, folder_name, file_name, created_at
            FROM content.frames
            ORDER BY created_at ASC
            LIMIT $1
        """, limit)
        
        if not frames:
            logger.warning("No frames found in the database!")
            return []
            
        logger.info(f"Found {len(frames)} earliest frames")
        return frames

async def get_frames_in_numerical_order(pool, limit=5):
    """Get frames in sequential numerical order based on frame_id number."""
    async with pool.acquire() as conn:
        logger.info(f"Retrieving frames in sequential numerical order...")
        
        # Query to get all frames
        frames = await conn.fetch("""
            SELECT frame_id, folder_name, file_name, created_at
            FROM content.frames
        """)
        
        if not frames:
            logger.warning("No frames found in the database!")
            return []
        
        # Extract number from frame_id (e.g., "frame_000123.jpg" -> 123)
        numbered_frames = []
        for frame in frames:
            frame_id = frame['frame_id']
            match = re.search(r'frame_0*(\d+)\.jpg', frame_id)
            if match:
                frame_number = int(match.group(1))
                numbered_frames.append((frame_number, frame))
        
        # Sort by frame number
        numbered_frames.sort(key=lambda x: x[0])
        
        # Apply limit
        if limit and limit < len(numbered_frames):
            numbered_frames = numbered_frames[:limit]
        
        # Extract just the frame data
        sorted_frames = [frame for _, frame in numbered_frames]
        
        logger.info(f"Found {len(sorted_frames)} frames in numerical order")
        for frame in sorted_frames:
            logger.info(f"  - {frame['frame_id']}")
        
        return sorted_frames

async def get_frames_by_folder(pool, folder_name, limit=10):
    """Get frames from a specific folder in numerical order."""
    async with pool.acquire() as conn:
        logger.info(f"Retrieving frames from folder: {folder_name}")
        
        # Query to get all frames from the specified folder
        frames = await conn.fetch("""
            SELECT frame_id, folder_name, file_name, created_at
            FROM content.frames
            WHERE folder_name = $1
        """, folder_name)
        
        if not frames:
            logger.warning(f"No frames found in folder {folder_name}")
            return []
        
        # Extract number from frame_id (e.g., "frame_000123.jpg" -> 123)
        numbered_frames = []
        for frame in frames:
            frame_id = frame['frame_id']
            match = re.search(r'frame_0*(\d+)\.jpg', frame_id)
            if match:
                frame_number = int(match.group(1))
                numbered_frames.append((frame_number, frame))
        
        # Sort by frame number
        numbered_frames.sort(key=lambda x: x[0])
        
        # Apply limit
        if limit and limit < len(numbered_frames):
            numbered_frames = numbered_frames[:limit]
        
        # Extract just the frame data
        sorted_frames = [frame for _, frame in numbered_frames]
        
        logger.info(f"Found {len(sorted_frames)} frames in folder {folder_name}")
        for frame in sorted_frames:
            logger.info(f"  - {frame['frame_id']}")
        
        return sorted_frames

async def ensure_metadata_exists(pool, frame_id, folder_name):
    """Check if metadata exists for a frame, create if not."""
    async with pool.acquire() as conn:
        # Check if metadata exists
        metadata = await conn.fetchrow("""
            SELECT * FROM metadata.frame_details_full
            WHERE frame_id = $1
        """, frame_id)
        
        if metadata:
            logger.info(f"Metadata already exists for frame {frame_id}")
            return True
        
        # Generate reference ID
        reference_id = f"{folder_name}/{frame_id}"
        
        # Create sample metadata
        await conn.execute("""
            INSERT INTO metadata.frame_details_full (
                frame_id, description, summary, tools_used, actions_performed,
                technical_details, workflow_stage, context_relationship, tags, ocr_data, reference_id
            ) VALUES (
                $1, 
                'Sample description for ' || $1,
                'Sample summary for ' || $1,
                ARRAY['tool1', 'tool2'],
                ARRAY['action1', 'action2'],
                $2::jsonb,
                'initial',
                'standalone',
                ARRAY['sample', 'frame'],
                '',
                $3
            )
        """, 
        frame_id,
        json.dumps({
            "processed_timestamp": datetime.datetime.now().isoformat(),
            "processing_version": "1.0.0",
            "sensitive_info_detected": False
        }),
        reference_id)
        
        logger.info(f"Added sample metadata for frame {frame_id}")
        return True

async def update_frame_metadata(pool, frame_id, metadata, reference_id):
    """Update the metadata for a frame."""
    async with pool.acquire() as conn:
        # Convert metadata to proper format
        if isinstance(metadata, dict):
            metadata_json = json.dumps(metadata.get("technical_details", {}))
            description = metadata.get("description", f"Analysis of frame {frame_id}")
            summary = metadata.get("summary", "")
            tools_used = metadata.get("tools_used", [])
            actions_performed = metadata.get("actions_performed", [])
            workflow_stage = metadata.get("workflow_stage", "llm_processed")
            context_relationship = metadata.get("context_relationship", "")
            tags = metadata.get("tags", [])
            ocr_data = metadata.get("ocr_data", "")
        else:
            # Default values if metadata is not a dictionary
            metadata_json = json.dumps({
                "processed_timestamp": datetime.datetime.now().isoformat(),
                "processing_version": "1.0.0"
            })
            description = f"Analysis of frame {frame_id}"
            summary = ""
            tools_used = []
            actions_performed = []
            workflow_stage = "llm_processed"
            context_relationship = ""
            tags = []
            ocr_data = ""
        
        # Update metadata
        await conn.execute("""
            UPDATE metadata.frame_details_full SET
                description = $2,
                summary = $3,
                tools_used = $4,
                actions_performed = $5,
                technical_details = $6::jsonb,
                workflow_stage = $7,
                context_relationship = $8,
                tags = $9,
                ocr_data = $10,
                reference_id = $11
            WHERE frame_id = $1
        """, 
        frame_id, 
        description,
        summary,
        tools_used,
        actions_performed,
        metadata_json,
        workflow_stage,
        context_relationship,
        tags,
        ocr_data,
        reference_id)
        
        logger.info(f"Updated metadata for frame {frame_id}")
        return True

async def ensure_chunk_exists(pool, frame_id, reference_id):
    """Ensure a chunk exists for the frame, create if not."""
    async with pool.acquire() as conn:
        # Check if chunk exists
        chunk = await conn.fetchrow("""
            SELECT chunk_id FROM metadata.frame_details_chunks
            WHERE frame_id = $1
        """, frame_id)
        
        if chunk:
            logger.info(f"Chunk already exists for frame {frame_id}")
            return chunk["chunk_id"]
        
        # Generate chunk ID
        chunk_id = str(uuid.uuid4())
        
        # Create a chunk reference ID
        chunk_reference_id = f"{reference_id}_Chunk1"
        
        # Create basic chunk entry
        await conn.execute("""
            INSERT INTO metadata.frame_details_chunks (
                frame_id, chunk_id, reference_id
            ) VALUES (
                $1, $2, $3
            )
        """, frame_id, chunk_id, chunk_reference_id)
        
        logger.info(f"Created chunk {chunk_id} for frame {frame_id}")
        return chunk_id

async def update_chunk_metadata(pool, chunk_id, frame_id, metadata, reference_id):
    """Update the metadata for a chunk."""
    async with pool.acquire() as conn:
        # Convert metadata to proper format
        if isinstance(metadata, dict):
            metadata_json = json.dumps(metadata.get("technical_details", {}))
            description = metadata.get("description", f"Chunk from frame {frame_id}")
            summary = metadata.get("summary", "")
            tools_used = metadata.get("tools_used", [])
            actions_performed = metadata.get("actions_performed", [])
            workflow_stage = metadata.get("workflow_stage", "llm_processed")
            context_relationship = metadata.get("context_relationship", "")
            tags = metadata.get("tags", [])
            ocr_data = metadata.get("ocr_data", "")
        else:
            # Default values if metadata is not a dictionary
            metadata_json = json.dumps({
                "parent_frame_id": frame_id,
                "processed_timestamp": datetime.datetime.now().isoformat(),
                "processing_version": "1.0.0"
            })
            description = f"Chunk from frame {frame_id}"
            summary = ""
            tools_used = []
            actions_performed = []
            workflow_stage = "llm_processed"
            context_relationship = ""
            tags = []
            ocr_data = ""
        
        # Update chunk metadata
        await conn.execute("""
            UPDATE metadata.frame_details_chunks SET
                description = $3,
                summary = $4,
                tools_used = $5,
                actions_performed = $6,
                technical_details = $7::jsonb,
                workflow_stage = $8,
                context_relationship = $9,
                tags = $10,
                ocr_data = $11,
                reference_id = $12
            WHERE chunk_id = $1 AND frame_id = $2
        """, 
        chunk_id,
        frame_id,
        description,
        summary,
        tools_used,
        actions_performed,
        metadata_json,
        workflow_stage,
        context_relationship,
        tags,
        ocr_data,
        reference_id)
        
        logger.info(f"Updated metadata for chunk {chunk_id}")
        return True

async def ensure_embedding_exists(pool, chunk_id, reference_id):
    """Ensure an embedding exists for the chunk, create if not."""
    async with pool.acquire() as conn:
        # Check if embedding exists
        embedding = await conn.fetchrow("""
            SELECT embedding_id FROM embeddings.multimodal_embeddings_chunks
            WHERE chunk_id = $1
        """, chunk_id)
        
        if embedding:
            logger.info(f"Embedding already exists for chunk {chunk_id}")
            return embedding["embedding_id"]
        
        # Get frame_id from chunk
        frame_info = await conn.fetchrow("""
            SELECT f.frame_id, f.image_url
            FROM metadata.frame_details_chunks c
            JOIN content.frames f ON c.frame_id = f.frame_id
            WHERE c.chunk_id = $1
        """, chunk_id)
        
        if not frame_info:
            logger.error(f"Could not find frame for chunk {chunk_id}")
            return None
        
        frame_id = frame_info["frame_id"]
        image_url = frame_info["image_url"]
        
        # Generate a random vector for the embedding
        random_vector = np.random.rand(EMBEDDING_DIM).astype(np.float32)
        
        # Generate embedding ID
        embedding_id = str(uuid.uuid4())
        
        # Convert the vector to a properly formatted string for PostgreSQL
        # Format: '[value1,value2,...]'
        vector_string = f"[{','.join(str(float(x)) for x in random_vector)}]"
        
        # Create the embedding
        await conn.execute("""
            INSERT INTO embeddings.multimodal_embeddings_chunks (
                embedding_id, chunk_id, reference_id, reference_type, model_name,
                text_content, image_url, embedding
            ) VALUES (
                $1, $2, $3, 'chunk', 'voyage-multimodal-3',
                'Sample text content for ' || $4, $5, $6::vector
            )
        """, embedding_id, chunk_id, reference_id, frame_id, image_url, vector_string)
        
        logger.info(f"Created embedding {embedding_id} for chunk {chunk_id}")
        return embedding_id

async def process_frame(pool, frame):
    """Process a single frame, ensuring all data exists in relevant tables."""
    # Extract frame details
    frame_id = frame["frame_id"]
    folder_name = frame["folder_name"]
    
    logger.info(f"Processing frame: {frame_id}")
    
    # 1. Ensure metadata exists and get reference_id
    reference_id = f"{folder_name}/{frame_id}"
    
    # Create frame metadata
    frame_metadata = {
        "description": f"Analysis of frame {frame_id}",
        "summary": "This is an automatically generated summary for frame processing.",
        "tools_used": ["auto_processor"],
        "actions_performed": ["metadata_generation"],
        "technical_details": {
            "processing_version": "1.0.0",
            "processed_timestamp": datetime.datetime.now().isoformat(),
            "sensitive_info_detected": frame_id.endswith("10.jpg")  # Just for demonstration
        },
        "workflow_stage": "llm_processed",
        "tags": ["frame", "processed", "test_data"],
        "ocr_data": "",
        "context_relationship": ""
    }
    
    # Update metadata in database
    await update_frame_metadata(pool, frame_id, frame_metadata, reference_id)
    
    # 2. Ensure chunk exists
    chunk_id = await ensure_chunk_exists(pool, frame_id, reference_id)
    chunk_reference_id = f"{reference_id}_Chunk1"
    
    # Create chunk-specific metadata derived from frame metadata
    chunk_metadata = {
        "description": f"Analysis of chunk from frame {frame_id}",
        "summary": frame_metadata["summary"],
        "technical_details": {
            "parent_frame_id": frame_id,
            "processing_version": "1.0.0",
            "processed_timestamp": datetime.datetime.now().isoformat()
        },
        "workflow_stage": frame_metadata["workflow_stage"],
        "tags": frame_metadata["tags"]
    }
    
    # 3. Update chunk metadata
    await update_chunk_metadata(pool, chunk_id, frame_id, chunk_metadata, chunk_reference_id)
    
    # 4. Check for and clean duplicate embeddings
    await clean_duplicate_embeddings(pool, chunk_id)
    
    # 5. Ensure embedding exists
    embedding_id = await ensure_embedding_exists(pool, chunk_id, chunk_reference_id)
    
    logger.info(f"Frame {frame_id} processed successfully")
    logger.info(f"  - Metadata updated")
    logger.info(f"  - Chunk {chunk_id} updated")
    logger.info(f"  - Embedding {embedding_id} updated")
    
    return {
        "frame_id": frame_id,
        "reference_id": reference_id,
        "chunk_id": chunk_id,
        "chunk_reference_id": chunk_reference_id,
        "embedding_id": embedding_id
    }

async def clean_duplicate_embeddings(pool, chunk_id):
    """Check for and remove duplicate embeddings for a chunk."""
    async with pool.acquire() as conn:
        # Get all embeddings for this chunk
        embeddings = await conn.fetch("""
            SELECT embedding_id, chunk_id, reference_id 
            FROM embeddings.multimodal_embeddings_chunks
            WHERE chunk_id = $1
        """, chunk_id)
        
        if len(embeddings) <= 1:
            # No duplicates
            return
        
        # Keep the first one, delete the rest
        keep_embedding_id = embeddings[0]['embedding_id']
        
        # Get IDs to delete
        delete_ids = [e['embedding_id'] for e in embeddings[1:]]
        
        if delete_ids:
            logger.info(f"Found {len(delete_ids)} duplicate embeddings for chunk {chunk_id}. Keeping {keep_embedding_id}")
            
            # Delete duplicate embeddings
            for embedding_id in delete_ids:
                await conn.execute("""
                    DELETE FROM embeddings.multimodal_embeddings_chunks
                    WHERE embedding_id = $1
                """, embedding_id)
                logger.info(f"Deleted duplicate embedding {embedding_id}")
                
        return

async def update_embeddings_with_frame_metadata(pool):
    """Update the embeddings.multimodal_embeddings table with frame metadata."""
    async with pool.acquire() as conn:
        logger.info("Updating embeddings.multimodal_embeddings with frame metadata...")
        
        # Check if the table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'embeddings' AND table_name = 'multimodal_embeddings'
            )
        """)
        
        if not table_exists:
            logger.warning("Table embeddings.multimodal_embeddings does not exist")
            return False
        
        # Get all frames with metadata
        frames = await conn.fetch("""
            SELECT f.frame_id, f.folder_name, m.technical_details
            FROM content.frames f
            JOIN metadata.frame_details_full m ON f.frame_id = m.frame_id
        """)
        
        if not frames:
            logger.warning("No frames with metadata found")
            return False
        
        # For each frame, make sure there's a corresponding embedding in multimodal_embeddings
        updated_count = 0
        for frame in frames:
            frame_id = frame["frame_id"]
            folder_name = frame["folder_name"]
            reference_id = f"{folder_name}/{frame_id}"
            
            # Check if an embedding exists
            embedding_exists = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM embeddings.multimodal_embeddings
                    WHERE reference_id = $1
                )
            """, reference_id)
            
            if not embedding_exists:
                # Create a random embedding vector
                random_vector = np.random.rand(EMBEDDING_DIM).astype(np.float32)
                
                # Convert the vector to a properly formatted string for PostgreSQL
                # Format: '[value1,value2,...]'
                vector_string = f"[{','.join(str(float(x)) for x in random_vector)}]"
                
                # Get image URL from frames table
                image_url = await conn.fetchval("""
                    SELECT image_url FROM content.frames
                    WHERE frame_id = $1
                """, frame_id)
                
                if not image_url:
                    image_url = f"/path/to/frames/{frame_id}"
                
                # Insert new embedding
                await conn.execute("""
                    INSERT INTO embeddings.multimodal_embeddings (
                        reference_id, reference_type, text_content, image_url,
                        embedding, model_name
                    ) VALUES (
                        $1, 'frame', 'Text content for frame ' || $2, $3,
                        $4::vector, 'voyage-multimodal-3'
                    )
                """, reference_id, frame_id, image_url, vector_string)
                
                updated_count += 1
                logger.info(f"Created embedding for frame {frame_id}")
        
        logger.info(f"Updated {updated_count} embeddings in multimodal_embeddings")
        return True

async def main():
    """Main function."""
    logger.info("Starting to process frames...")
    
    try:
        # Create connection pool
        pool = await create_connection_pool()
        
        # Define folders to process
        folders = [
            "screen_recording_2025_03_03_at_3_39_52_am",
            "screen_recording_2025_02_20_at_10_59_16_am"
        ]
        
        # Process each folder
        total_processed = 0
        for folder_name in folders:
            logger.info(f"Processing folder: {folder_name}")
            
            # Get frames from the folder in numerical order
            frames = await get_frames_by_folder(pool, folder_name, limit=20)
            if not frames:
                logger.warning(f"No frames found in folder {folder_name}")
                continue
            
            # Process each frame
            results = []
            for frame in frames:
                result = await process_frame(pool, frame)
                results.append(result)
            
            logger.info(f"Successfully processed {len(results)} frames from folder {folder_name}")
            total_processed += len(results)
        
        # Update embeddings.multimodal_embeddings table with frame metadata
        await update_embeddings_with_frame_metadata(pool)
        
        # Verify results
        logger.info(f"Successfully processed a total of {total_processed} frames from {len(folders)} folders")
        
        # Close the connection pool
        await pool.close()
        logger.info("Processing completed. PostgreSQL connection pool closed.")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 