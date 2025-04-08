#!/usr/bin/env python3
"""
Database migration script to set up tables and copy data from embeddings.multimodal_embeddings.
"""

import os
import sys
import json
import uuid
import asyncio
import logging
import asyncpg
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path setup
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Import environment variables
try:
    if Path(project_root / '.env').exists():
        # Load .env file if python-dotenv is available
        try:
            from dotenv import load_dotenv
            load_dotenv(project_root / '.env')
            logger.info("Loaded environment from .env file")
        except ImportError:
            logger.warning("python-dotenv not found, using environment variables as is")
except Exception as e:
    logger.error(f"Error loading environment: {e}")

async def get_connection():
    """Get a database connection."""
    # Get connection parameters from environment
    host = os.getenv('POSTGRES_HOST')
    port = os.getenv('POSTGRES_PORT')
    database = os.getenv('POSTGRES_DB')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASS')
    
    # Check if all parameters are available
    if not all([host, port, database, user, password]):
        logger.error("Incomplete PostgreSQL connection information")
        return None
    
    try:
        # Create connection
        dsn = f"postgres://{user}:{password}@{host}:{port}/{database}"
        conn = await asyncpg.connect(dsn=dsn)
        logger.info(f"Connected to PostgreSQL database at {host}:{port}/{database}")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

async def setup_database_schema(conn):
    """Set up database schema, tables, and extensions."""
    try:
        # Create schemas
        await conn.execute("CREATE SCHEMA IF NOT EXISTS content;")
        await conn.execute("CREATE SCHEMA IF NOT EXISTS metadata;")
        await conn.execute("CREATE SCHEMA IF NOT EXISTS embeddings;")
        
        # Create pgvector extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        await conn.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        
        # Create content schema tables
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS content.frames (
            id SERIAL PRIMARY KEY,
            frame_name TEXT NOT NULL,
            folder_path TEXT,
            folder_name TEXT,
            frame_timestamp TIMESTAMPTZ,
            creation_time TIMESTAMPTZ DEFAULT NOW(),
            google_drive_url TEXT,
            airtable_record_id TEXT,
            metadata JSONB,
            UNIQUE(frame_name, folder_path)
        );
        """)
        
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS content.chunks (
            id SERIAL PRIMARY KEY,
            frame_id INTEGER REFERENCES content.frames(id) ON DELETE CASCADE,
            chunk_sequence_id INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            creation_time TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE(frame_id, chunk_sequence_id)
        );
        """)
        
        # Create metadata schema tables
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS metadata.frame_details_full (
            frame_id INTEGER PRIMARY KEY REFERENCES content.frames(id) ON DELETE CASCADE,
            reference_id TEXT NOT NULL,
            description TEXT,
            summary TEXT,
            tools_used TEXT[],
            actions_performed TEXT[],
            technical_details JSONB,
            workflow_stage TEXT,
            context_relationship TEXT,
            tags TEXT[],
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS metadata.frame_details_chunk (
            chunk_id INTEGER PRIMARY KEY REFERENCES content.chunks(id) ON DELETE CASCADE,
            frame_id INTEGER REFERENCES content.frames(id) ON DELETE CASCADE,
            reference_id TEXT NOT NULL,
            chunk_sequence_id INTEGER NOT NULL,
            description TEXT,
            context TEXT,
            tags TEXT[],
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS metadata.frame_embeddings (
            id UUID PRIMARY KEY,
            frame_id INTEGER REFERENCES content.frames(id) ON DELETE CASCADE,
            embedding vector(1024),
            model_name TEXT NOT NULL,
            creation_time TIMESTAMPTZ DEFAULT NOW()
        );
        """)
        
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS metadata.chunk_embeddings (
            id UUID PRIMARY KEY,
            chunk_id INTEGER REFERENCES content.chunks(id) ON DELETE CASCADE,
            embedding vector(1024),
            model_name TEXT NOT NULL,
            creation_time TIMESTAMPTZ DEFAULT NOW()
        );
        """)
        
        # Create embeddings schema tables
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS embeddings.multimodal_embeddings (
            embedding_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            reference_id TEXT NOT NULL,
            reference_type TEXT NOT NULL,
            text_content TEXT,
            image_url TEXT,
            embedding vector(1024) NOT NULL,
            model_name TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Create indexes
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_frames_frame_name ON content.frames (frame_name);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_frames_folder_path ON content.frames (folder_path);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_frame_id ON content.chunks (frame_id);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_frame_details_full_reference_id ON metadata.frame_details_full (reference_id);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_frame_details_chunk_reference_id ON metadata.frame_details_chunk (reference_id);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_multimodal_embeddings_reference_id ON embeddings.multimodal_embeddings (reference_id);")
        
        logger.info("Database schema and tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error setting up database schema: {e}")
        return False

async def migrate_existing_data(conn):
    """Migrate existing data from embeddings.multimodal_embeddings to metadata tables."""
    try:
        # Check if embeddings.multimodal_embeddings has data
        count = await conn.fetchval("SELECT COUNT(*) FROM embeddings.multimodal_embeddings")
        logger.info(f"Found {count} rows in embeddings.multimodal_embeddings")
        
        if count == 0:
            logger.info("No data to migrate")
            return True
        
        # Get frame type embeddings
        frame_embeddings = await conn.fetch("""
        SELECT embedding_id, reference_id, text_content, image_url, embedding, model_name
        FROM embeddings.multimodal_embeddings
        WHERE reference_type = 'frame'
        """)
        
        logger.info(f"Found {len(frame_embeddings)} frame embeddings to migrate")
        
        # Process each frame embedding
        frames_processed = 0
        for row in frame_embeddings:
            reference_id = row['reference_id']
            embedding_id = row['embedding_id']
            
            # Extract folder name and frame name from reference_id
            parts = reference_id.split('/')
            if len(parts) >= 2:
                folder_name = parts[0]
                frame_name = parts[1]
            else:
                folder_name = "unknown_folder"
                frame_name = reference_id
            
            # Insert into content.frames if doesn't exist
            frame_id = await conn.fetchval("""
            INSERT INTO content.frames (frame_name, folder_name, google_drive_url)
            VALUES ($1, $2, $3)
            ON CONFLICT (frame_name, folder_path) DO UPDATE 
            SET folder_name = $2, google_drive_url = $3
            RETURNING id
            """, frame_name, folder_name, row['image_url'])
            
            if frame_id:
                # Create proper reference_id that includes folder name and frame name
                proper_reference_id = f"{folder_name}/{frame_name}"
                
                # Insert into metadata.frame_details_full
                await conn.execute("""
                INSERT INTO metadata.frame_details_full (frame_id, reference_id)
                VALUES ($1, $2)
                ON CONFLICT (frame_id) DO UPDATE
                SET reference_id = $2
                """, frame_id, proper_reference_id)
                
                # Insert into metadata.frame_embeddings
                await conn.execute("""
                INSERT INTO metadata.frame_embeddings (id, frame_id, embedding, model_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE
                SET embedding = $3, model_name = $4
                """, embedding_id, frame_id, row['embedding'], row['model_name'])
                
                # Update reference_id in embeddings.multimodal_embeddings if needed
                if reference_id != proper_reference_id:
                    await conn.execute("""
                    UPDATE embeddings.multimodal_embeddings
                    SET reference_id = $1, updated_at = CURRENT_TIMESTAMP
                    WHERE embedding_id = $2
                    """, proper_reference_id, embedding_id)
                
                frames_processed += 1
        
        logger.info(f"Successfully processed {frames_processed} frame embeddings")
        
        # Get chunk type embeddings
        chunk_embeddings = await conn.fetch("""
        SELECT embedding_id, reference_id, text_content, image_url, embedding, model_name
        FROM embeddings.multimodal_embeddings
        WHERE reference_type = 'chunk'
        """)
        
        logger.info(f"Found {len(chunk_embeddings)} chunk embeddings to migrate")
        
        # Process each chunk embedding
        chunks_processed = 0
        for row in chunk_embeddings:
            reference_id = row['reference_id']
            embedding_id = row['embedding_id']
            
            # Extract folder name, frame name, and chunk sequence from reference_id
            # Expected format: "folder/frame/chunk_sequence"
            parts = reference_id.split('/')
            if len(parts) >= 3 and 'chunk_' in parts[2]:
                folder_name = parts[0]
                frame_name = parts[1]
                chunk_sequence_str = parts[2].replace('chunk_', '')
                try:
                    chunk_sequence_id = int(chunk_sequence_str)
                except ValueError:
                    chunk_sequence_id = 0
            else:
                # Can't determine proper parts
                logger.warning(f"Cannot parse reference_id: {reference_id}")
                continue
            
            # Find frame_id
            frame_id = await conn.fetchval("""
            SELECT id FROM content.frames 
            WHERE frame_name = $1 AND folder_name = $2
            """, frame_name, folder_name)
            
            if not frame_id:
                # Frame doesn't exist, create it
                frame_id = await conn.fetchval("""
                INSERT INTO content.frames (frame_name, folder_name)
                VALUES ($1, $2)
                RETURNING id
                """, frame_name, folder_name)
                
                # Create frame_details_full entry
                proper_frame_reference_id = f"{folder_name}/{frame_name}"
                await conn.execute("""
                INSERT INTO metadata.frame_details_full (frame_id, reference_id)
                VALUES ($1, $2)
                ON CONFLICT (frame_id) DO NOTHING
                """, frame_id, proper_frame_reference_id)
            
            if frame_id:
                # Insert chunk
                chunk_id = await conn.fetchval("""
                INSERT INTO content.chunks (frame_id, chunk_sequence_id, chunk_text)
                VALUES ($1, $2, $3)
                ON CONFLICT (frame_id, chunk_sequence_id) DO UPDATE
                SET chunk_text = $3
                RETURNING id
                """, frame_id, chunk_sequence_id, row['text_content'])
                
                if chunk_id:
                    # Create proper reference_id that includes folder name, frame name, and chunk sequence
                    proper_chunk_reference_id = f"{folder_name}/{frame_name}/chunk_{chunk_sequence_id}"
                    
                    # Insert into metadata.frame_details_chunk
                    await conn.execute("""
                    INSERT INTO metadata.frame_details_chunk (
                        chunk_id, frame_id, reference_id, chunk_sequence_id
                    ) VALUES ($1, $2, $3, $4)
                    ON CONFLICT (chunk_id) DO UPDATE
                    SET reference_id = $3
                    """, chunk_id, frame_id, proper_chunk_reference_id, chunk_sequence_id)
                    
                    # Insert into metadata.chunk_embeddings
                    await conn.execute("""
                    INSERT INTO metadata.chunk_embeddings (id, chunk_id, embedding, model_name)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (id) DO UPDATE
                    SET embedding = $3, model_name = $4
                    """, embedding_id, chunk_id, row['embedding'], row['model_name'])
                    
                    # Update reference_id in embeddings.multimodal_embeddings if needed
                    if reference_id != proper_chunk_reference_id:
                        await conn.execute("""
                        UPDATE embeddings.multimodal_embeddings
                        SET reference_id = $1, updated_at = CURRENT_TIMESTAMP
                        WHERE embedding_id = $2
                        """, proper_chunk_reference_id, embedding_id)
                    
                    chunks_processed += 1
        
        logger.info(f"Successfully processed {chunks_processed} chunk embeddings")
        return True
        
    except Exception as e:
        logger.error(f"Error migrating data: {e}")
        return False

async def migrate_old_tables(conn):
    """Migrate data from old tables if they exist."""
    try:
        # Check if old tables exist
        frame_details_exists = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'metadata' AND table_name = 'frame_details'
        )
        """)
        
        chunk_details_exists = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'metadata' AND table_name = 'chunk_details'
        )
        """)
        
        # Migrate from frame_details to frame_details_full if needed
        if frame_details_exists:
            logger.info("Old table metadata.frame_details exists, migrating data...")
            
            # Copy data
            await conn.execute("""
            INSERT INTO metadata.frame_details_full (
                frame_id, reference_id, description, summary, 
                tools_used, actions_performed, technical_details,
                workflow_stage, context_relationship, tags,
                created_at, updated_at
            )
            SELECT 
                frame_id, 
                COALESCE(
                    reference_id, 
                    (SELECT COALESCE(folder_name, 'unknown_folder') || '/' || frame_name 
                     FROM content.frames WHERE id = frame_id)
                ) as reference_id,
                description, summary, tools_used, actions_performed, 
                technical_details, workflow_stage, context_relationship, 
                tags, created_at, updated_at
            FROM metadata.frame_details
            ON CONFLICT (frame_id) DO UPDATE SET
                reference_id = EXCLUDED.reference_id,
                description = EXCLUDED.description,
                summary = EXCLUDED.summary,
                tools_used = EXCLUDED.tools_used,
                actions_performed = EXCLUDED.actions_performed,
                technical_details = EXCLUDED.technical_details,
                workflow_stage = EXCLUDED.workflow_stage,
                context_relationship = EXCLUDED.context_relationship,
                tags = EXCLUDED.tags,
                updated_at = CURRENT_TIMESTAMP
            """)
            
            count = await conn.fetchval("SELECT COUNT(*) FROM metadata.frame_details")
            logger.info(f"Migrated {count} rows from frame_details to frame_details_full")
        
        # Migrate from chunk_details to frame_details_chunk if needed
        if chunk_details_exists:
            logger.info("Old table metadata.chunk_details exists, migrating data...")
            
            # Copy data
            await conn.execute("""
            INSERT INTO metadata.frame_details_chunk (
                chunk_id, frame_id, reference_id, chunk_sequence_id,
                description, context, tags, created_at, updated_at
            )
            SELECT 
                chunk_id, frame_id, 
                COALESCE(
                    reference_id,
                    (
                        SELECT 
                            COALESCE(f.folder_name, 'unknown_folder') || '/' || 
                            f.frame_name || '/chunk_' || c.chunk_sequence_id
                        FROM content.chunks c
                        JOIN content.frames f ON c.frame_id = f.id
                        WHERE c.id = chunk_id
                    )
                ) as reference_id,
                chunk_sequence_id, description, context, tags, 
                created_at, updated_at
            FROM metadata.chunk_details
            ON CONFLICT (chunk_id) DO UPDATE SET
                reference_id = EXCLUDED.reference_id,
                frame_id = EXCLUDED.frame_id,
                chunk_sequence_id = EXCLUDED.chunk_sequence_id,
                description = EXCLUDED.description,
                context = EXCLUDED.context,
                tags = EXCLUDED.tags,
                updated_at = CURRENT_TIMESTAMP
            """)
            
            count = await conn.fetchval("SELECT COUNT(*) FROM metadata.chunk_details")
            logger.info(f"Migrated {count} rows from chunk_details to frame_details_chunk")
        
        return True
    except Exception as e:
        logger.error(f"Error migrating old tables: {e}")
        return False

async def main():
    """Main migration function."""
    logger.info("Starting database migration")
    
    # Get database connection
    conn = await get_connection()
    if not conn:
        logger.error("Could not connect to database. Migration aborted.")
        return
    
    try:
        # Set up schema and tables
        schema_success = await setup_database_schema(conn)
        if not schema_success:
            logger.error("Failed to set up database schema. Migration aborted.")
            return
        
        # Migrate data from old tables if they exist
        old_tables_migration = await migrate_old_tables(conn)
        if not old_tables_migration:
            logger.warning("Failed to migrate data from old tables, continuing with next steps")
        
        # Migrate existing data from multimodal_embeddings
        migration_success = await migrate_existing_data(conn)
        if not migration_success:
            logger.error("Failed to migrate existing data.")
        else:
            logger.info("Data migration completed successfully")
        
    finally:
        # Close connection
        await conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    asyncio.run(main()) 