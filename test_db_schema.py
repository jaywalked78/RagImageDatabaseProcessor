#!/usr/bin/env python3
"""
Test script for the updated database schema and storage operations.
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from src.database.postgres_vector_store import PostgresVectorStore

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_database_operations():
    """Test the updated database operations with schemas and reference IDs."""
    logger.info("Starting database schema and storage test")
    
    # Create PostgresVectorStore instance
    store = PostgresVectorStore()
    
    try:
        # Connect to the database
        connected = await store.connect()
        if not connected:
            logger.error("Failed to connect to PostgreSQL database")
            return
            
        logger.info("Successfully connected to the database")
        
        # 1. Store a test frame
        frame_name = "test_frame_db_schema"
        folder_path = "/test/folder/path"
        folder_name = "TestFolder"
        frame_timestamp = datetime.now().isoformat()
        
        frame_id = await store.store_frame(
            frame_name=frame_name,
            folder_path=folder_path,
            folder_name=folder_name,
            frame_timestamp=frame_timestamp,
            google_drive_url="https://example.com/testframe.jpg",
            airtable_record_id="recTestAirtable123",
            metadata={"test": "metadata", "source": "test_script"}
        )
        
        if not frame_id:
            logger.error("Failed to store test frame")
            return
            
        logger.info(f"Successfully stored test frame with ID: {frame_id}")
        
        # 2. Store test chunks
        chunk_ids = []
        for i in range(3):
            chunk_id = await store.store_chunk(
                frame_id=frame_id,
                chunk_sequence_id=i,
                chunk_text=f"This is test chunk {i} for frame {frame_name}. It contains sample text for testing."
            )
            
            if not chunk_id:
                logger.error(f"Failed to store test chunk {i}")
                continue
                
            logger.info(f"Successfully stored test chunk with ID: {chunk_id}")
            chunk_ids.append(chunk_id)
        
        # 3. Create test embeddings (1024 dimensions)
        test_embedding = [0.1] * 1024  # Create a 1024-dimensional vector
        
        # 4. Store frame embedding
        frame_embedding_id = await store.store_frame_embedding(
            frame_id=frame_id,
            embedding=test_embedding,
            model_name="test-model-1024-dim"
        )
        
        if not frame_embedding_id:
            logger.error("Failed to store frame embedding")
        else:
            logger.info(f"Successfully stored frame embedding with ID: {frame_embedding_id}")
            
        # 5. Store chunk embeddings
        for i, chunk_id in enumerate(chunk_ids):
            chunk_embedding_id = await store.store_chunk_embedding(
                chunk_id=chunk_id,
                embedding=test_embedding,
                model_name="test-model-1024-dim"
            )
            
            if not chunk_embedding_id:
                logger.error(f"Failed to store chunk {chunk_id} embedding")
            else:
                logger.info(f"Successfully stored chunk {chunk_id} embedding with ID: {chunk_embedding_id}")
                
        # 6. Verify the tables structure and data
        await verify_tables(store)
        
    except Exception as e:
        logger.error(f"Error during database test: {e}")
        
    finally:
        # Close database connection
        await store.close()
        logger.info("Test completed")

async def verify_tables(store):
    """Verify tables structure and data."""
    if not store.connection_pool:
        logger.error("No database connection")
        return
        
    try:
        async with store.connection_pool.acquire() as conn:
            # Check metadata.frame_details_full table
            logger.info("Checking metadata.frame_details_full table...")
            query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'metadata' AND table_name = 'frame_details_full'
            )
            """
            frame_details_exists = await conn.fetchval(query)
            
            if frame_details_exists:
                logger.info("Table metadata.frame_details_full exists")
                
                # Check data in frame_details_full
                query = "SELECT COUNT(*) FROM metadata.frame_details_full"
                count = await conn.fetchval(query)
                logger.info(f"metadata.frame_details_full has {count} rows")
                
                # Check reference_id format in frame_details_full
                query = "SELECT reference_id FROM metadata.frame_details_full LIMIT 5"
                rows = await conn.fetch(query)
                for row in rows:
                    logger.info(f"Frame reference_id example: {row['reference_id']}")
            else:
                logger.error("Table metadata.frame_details_full does not exist")
            
            # Check metadata.frame_details_chunk table
            logger.info("Checking metadata.frame_details_chunk table...")
            query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'metadata' AND table_name = 'frame_details_chunk'
            )
            """
            chunk_details_exists = await conn.fetchval(query)
            
            if chunk_details_exists:
                logger.info("Table metadata.frame_details_chunk exists")
                
                # Check data in frame_details_chunk
                query = "SELECT COUNT(*) FROM metadata.frame_details_chunk"
                count = await conn.fetchval(query)
                logger.info(f"metadata.frame_details_chunk has {count} rows")
                
                # Check reference_id format in frame_details_chunk
                query = "SELECT reference_id FROM metadata.frame_details_chunk LIMIT 5"
                rows = await conn.fetch(query)
                for row in rows:
                    logger.info(f"Chunk reference_id example: {row['reference_id']}")
            else:
                logger.error("Table metadata.frame_details_chunk does not exist")
            
            # Check embeddings.multimodal_embeddings table
            logger.info("Checking embeddings.multimodal_embeddings table...")
            query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'embeddings' AND table_name = 'multimodal_embeddings'
            )
            """
            multimodal_exists = await conn.fetchval(query)
            
            if multimodal_exists:
                logger.info("Table embeddings.multimodal_embeddings exists")
                
                # Check data in multimodal_embeddings
                query = "SELECT COUNT(*) FROM embeddings.multimodal_embeddings"
                count = await conn.fetchval(query)
                logger.info(f"embeddings.multimodal_embeddings has {count} rows")
                
                # Check reference_id format in multimodal_embeddings
                query = "SELECT reference_id, reference_type FROM embeddings.multimodal_embeddings LIMIT 5"
                rows = await conn.fetch(query)
                for row in rows:
                    logger.info(f"Multimodal reference_id example: {row['reference_id']} (type: {row['reference_type']})")
            else:
                logger.error("Table embeddings.multimodal_embeddings does not exist")
                
    except Exception as e:
        logger.error(f"Error verifying tables: {e}")

if __name__ == "__main__":
    asyncio.run(test_database_operations()) 