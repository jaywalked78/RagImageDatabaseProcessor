#!/usr/bin/env python3
"""
Test script for vector database logging enhancements.
"""

import asyncio
import logging
from src.database.postgres_vector_store import PostgresVectorStore

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_vector_db_logging():
    """Test vector database operations with enhanced logging."""
    logger.info("Starting vector database logging test")
    
    # Create PostgresVectorStore instance
    store = PostgresVectorStore()
    
    # Connect to the database
    try:
        connected = await store.connect()
        if not connected:
            logger.error("Failed to connect to PostgreSQL database")
            return
    except Exception as e:
        logger.error(f"Exception connecting to database: {e}")
        return
    
    try:
        # Test frame embedding storage
        frame_id = 12345
        test_embedding = [0.1, 0.2, 0.3, 0.4, 0.5] * 100  # 500-dimensional vector
        model_name = "test-embedding-model"
        
        logger.info(f"Testing frame embedding storage for frame {frame_id}")
        await store.store_frame_embedding(frame_id, test_embedding, model_name)
        
        # Test chunk embedding storage
        chunk_id = 54321
        logger.info(f"Testing chunk embedding storage for chunk {chunk_id}")
        await store.store_chunk_embedding(chunk_id, test_embedding, model_name)
        
    except Exception as e:
        logger.error(f"Error during vector operations: {e}")
    
    finally:
        # Close connection
        store.close()
        logger.info("Vector database test completed")

# Run the async test function
if __name__ == "__main__":
    asyncio.run(test_vector_db_logging()) 