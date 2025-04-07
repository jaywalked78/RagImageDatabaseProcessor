#!/usr/bin/env python
"""
Database initialization script.
Creates necessary tables and extensions.
"""

import argparse
import logging
import sys

from src.db.database_client import DatabaseClient
from src.config.settings import EMBEDDING_DIM

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("db_init")

def initialize_database(reset: bool = False):
    """Initialize the database, creating tables and extensions."""
    try:
        db_client = DatabaseClient()
        logger.info("Database client initialized.")

        # Check connection
        if not db_client.check_connection():
            logger.error("Database connection failed. Please check your settings.")
            return False
        
        logger.info("Successfully connected to the database.")

        with db_client.get_connection() as conn:
            with conn.cursor() as cur:
                if reset:
                    logger.warning("Resetting database: Dropping existing tables...")
                    cur.execute("DROP TABLE IF EXISTS frame_chunks CASCADE;")
                    logger.info("Existing tables dropped.")
                
                # Create pgvector extension if not exists
                logger.info("Checking for pgvector extension...")
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                logger.info("pgvector extension ensured.")

                # Create frame_chunks table
                logger.info("Creating frame_chunks table...")
                create_table_query = f"""
                CREATE TABLE IF NOT EXISTS frame_chunks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    airtable_record_id TEXT NOT NULL,
                    frame_path TEXT NOT NULL, -- Relative path or identifier
                    chunk_sequence_id INT NOT NULL, -- 0-indexed chunk number for a given frame
                    chunk_text TEXT,
                    full_metadata JSONB, -- Store structured metadata here
                    embedding vector({EMBEDDING_DIM}), -- Ensure dimension matches config
                    created_at TIMESTAMPTZ DEFAULT now(),
                    -- Ensure unique combination of frame and chunk sequence
                    UNIQUE (airtable_record_id, chunk_sequence_id)
                );
                """
                cur.execute(create_table_query)
                logger.info("frame_chunks table created successfully.")

                # Create indexes
                logger.info("Creating indexes on frame_chunks table...")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_airtable_record_id ON frame_chunks (airtable_record_id);")
                cur.execute(f"CREATE INDEX IF NOT EXISTS idx_embedding ON frame_chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_full_metadata ON frame_chunks USING gin (full_metadata jsonb_path_ops);")
                logger.info("Indexes created successfully.")

            conn.commit()
            logger.info("Database initialization complete.")
            return True

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        return False
    finally:
        if 'db_client' in locals() and db_client:
            db_client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize the application database.")
    parser.add_argument("--reset", action="store_true", help="Drop existing tables before initializing.")
    args = parser.parse_args()
    
    print("🚀 Starting database initialization...")
    success = initialize_database(reset=args.reset)
    
    if success:
        print("✅ Database initialization successful!")
        sys.exit(0)
    else:
        print("❌ Database initialization failed. Check logs for details.")
        sys.exit(1) 