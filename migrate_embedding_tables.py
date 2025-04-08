#!/usr/bin/env python3
"""
Migration script to populate Supabase embedding and metadata tables with correct reference IDs.
This script migrates data from multimodal_embeddings to ensure all tables have consistent
reference IDs and populates empty tables.
"""

import os
import sys
import logging
import asyncio
import json
import uuid
import re
from datetime import datetime
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
logger = logging.getLogger('migration')

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

async def ensure_schemas_exist(pool):
    """Ensure that all required schemas exist in the database."""
    schemas = ['embeddings', 'metadata', 'content']
    async with pool.acquire() as conn:
        for schema in schemas:
            await conn.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')
        logger.info("Verified required schemas exist")

async def ensure_tables_exist(pool):
    """Ensure the required tables exist in the database."""
    async with pool.acquire() as conn:
        # Check if the source table exists
        embeddings_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'embeddings' AND table_name = 'multimodal_embeddings')"
        )
        
        if not embeddings_exists:
            logger.error("Source table embeddings.multimodal_embeddings does not exist")
            sys.exit(1)
        
        # Create metadata.frame_details_full table if it doesn't exist
        frame_details_full_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'metadata' AND table_name = 'frame_details_full')"
        )
        
        if not frame_details_full_exists:
            logger.info("Creating table metadata.frame_details_full")
            await conn.execute("""
                CREATE TABLE metadata.frame_details_full (
                    frame_id TEXT PRIMARY KEY,
                    description TEXT,
                    summary TEXT,
                    tools_used TEXT[],
                    actions_performed TEXT[],
                    technical_details JSONB,
                    workflow_stage TEXT,
                    context_relationship TEXT,
                    tags TEXT[],
                    ocr_data TEXT,
                    reference_id TEXT
                )
            """)
        else:
            logger.info("Table metadata.frame_details_full already exists")
        
        # Create metadata.frame_details_chunks table if it doesn't exist
        frame_details_chunks_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'metadata' AND table_name = 'frame_details_chunks')"
        )
        
        if not frame_details_chunks_exists:
            logger.info("Creating table metadata.frame_details_chunks")
            await conn.execute("""
                CREATE TABLE metadata.frame_details_chunks (
                    frame_id TEXT PRIMARY KEY,
                    description TEXT,
                    summary TEXT,
                    tools_used TEXT[],
                    actions_performed TEXT[],
                    technical_details JSONB,
                    workflow_stage TEXT,
                    context_relationship TEXT,
                    tags TEXT[],
                    ocr_data TEXT,
                    chunk_id TEXT,
                    reference_id TEXT
                )
            """)
        else:
            logger.info("Table metadata.frame_details_chunks already exists")
        
        # First drop the process_frames_chunks table if it exists to avoid constraint issues
        await conn.execute('DROP TABLE IF EXISTS metadata.process_frames_chunks')
        
        # Create metadata.process_frames_chunks fresh with correct data types
        # Remove direct foreign key references to avoid constraint issues
        await conn.execute('''
            CREATE TABLE metadata.process_frames_chunks (
                id SERIAL PRIMARY KEY,
                frame_id TEXT,
                chunk_id TEXT, 
                airtable_record_id TEXT,
                processing_status TEXT,
                chunk_type TEXT,
                chunk_format TEXT,
                processing_metadata JSONB,
                processing_timestamp TIMESTAMPTZ DEFAULT NOW()
            )
        ''')
        
        logger.info("Created table metadata.process_frames_chunks")
        
        # Create embeddings.multimodal_embeddings_chunks table if it doesn't exist
        multimodal_embeddings_chunks_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'embeddings' AND table_name = 'multimodal_embeddings_chunks')"
        )
        
        if not multimodal_embeddings_chunks_exists:
            logger.info("Creating table embeddings.multimodal_embeddings_chunks")
            await conn.execute("""
                CREATE TABLE embeddings.multimodal_embeddings_chunks (
                    embedding_id UUID PRIMARY KEY,
                    reference_id TEXT NOT NULL,
                    reference_type TEXT NOT NULL,
                    text_content TEXT,
                    image_url TEXT NOT NULL,
                    embedding VECTOR(1024) NOT NULL,
                    model_name TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    chunk_id TEXT
                )
            """)
        else:
            logger.info("Table embeddings.multimodal_embeddings_chunks already exists")

async def normalize_reference_ids(pool):
    """Normalize reference IDs to use underscores instead of slashes."""
    async with pool.acquire() as conn:
        # Get all reference IDs from multimodal_embeddings
        rows = await conn.fetch('''
            SELECT embedding_id, reference_id, reference_type 
            FROM embeddings.multimodal_embeddings
        ''')
        
        update_count = 0
        for row in rows:
            old_ref_id = row['reference_id']
            # Replace slashes with underscores
            new_ref_id = old_ref_id.replace('/', '_')
            
            if old_ref_id != new_ref_id:
                await conn.execute('''
                    UPDATE embeddings.multimodal_embeddings
                    SET reference_id = $1
                    WHERE embedding_id = $2
                ''', new_ref_id, row['embedding_id'])
                update_count += 1
                
        logger.info(f"Normalized {update_count} reference IDs in multimodal_embeddings")

async def migrate_frame_data(pool):
    """Migrate frame data from embeddings.multimodal_embeddings to metadata tables."""
    logger.info("Migrating frame data")
    
    async with pool.acquire() as conn:
        # Get all unique frames from multimodal embeddings
        frames = await conn.fetch("""
            SELECT DISTINCT reference_id, reference_type
            FROM embeddings.multimodal_embeddings
            WHERE reference_type = 'frame'
        """)
        
        logger.info(f"Found {len(frames)} unique frames to migrate")
        
        for frame in frames:
            reference_id = frame['reference_id']
            
            # Check if the reference_id is already in content.frames
            content_frame = await conn.fetchrow("""
                SELECT frame_id FROM content.frames
                WHERE frame_id = $1
            """, reference_id)
            
            # Use the actual frame_id from content.frames if it exists
            frame_id = reference_id
            
            # Get the embedding for this frame
            embedding = await conn.fetchrow("""
                SELECT reference_id, text_content, image_url
                FROM embeddings.multimodal_embeddings
                WHERE reference_id = $1 AND reference_type = 'frame'
                LIMIT 1
            """, reference_id)
            
            if not embedding:
                logger.warning(f"No embedding found for frame {reference_id}")
                continue
            
            # Check if this frame already exists in metadata.frame_details_full
            existing_frame = await conn.fetchrow("""
                SELECT frame_id FROM metadata.frame_details_full
                WHERE reference_id = $1
            """, reference_id)
            
            if existing_frame:
                logger.info(f"Frame {reference_id} already exists in metadata.frame_details_full, skipping")
                continue
            
            # Insert frame data into metadata.frame_details_full
            try:
                await conn.execute("""
                    INSERT INTO metadata.frame_details_full
                    (frame_id, description, summary, tools_used, actions_performed, ocr_data, reference_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    ON CONFLICT (frame_id) DO UPDATE
                    SET description = $2, summary = $3, tools_used = $4, actions_performed = $5, 
                        ocr_data = $6, reference_id = $7
                """, 
                    frame_id,                      # frame_id
                    f"Description for {reference_id}", # description
                    embedding['text_content'],     # summary
                    ["AutoTokenizer"],             # tools_used
                    ["OCR Processing"],            # actions_performed
                    embedding['text_content'],     # ocr_data
                    reference_id                   # reference_id
                )
                
                logger.info(f"Migrated frame data for {reference_id} to metadata.frame_details_full")
            except Exception as e:
                logger.error(f"Error migrating frame data for {reference_id}: {e}")
    
    logger.info("Frame data migration complete")

async def migrate_chunk_data(pool):
    """Migrate chunk data from embeddings.multimodal_embeddings to metadata tables."""
    logger.info("Migrating chunk data")
    
    async with pool.acquire() as conn:
        # Get all multimodal embeddings
        embeddings = await conn.fetch("""
            SELECT embedding_id, reference_id, reference_type, text_content, image_url, embedding, model_name
            FROM embeddings.multimodal_embeddings
        """)
        
        logger.info(f"Found {len(embeddings)} embeddings to process for chunks")
        
        for embedding_row in embeddings:
            embedding_id = embedding_row['embedding_id']
            reference_id = embedding_row['reference_id']
            reference_type = embedding_row['reference_type']
            text_content = embedding_row['text_content']
            image_url = embedding_row['image_url']
            embedding_vector = embedding_row['embedding']
            model_name = embedding_row['model_name']
            
            # Generate a unique chunk ID
            chunk_id = str(uuid.uuid4())
            
            # Insert into embeddings.multimodal_embeddings_chunks
            try:
                # Insert into embeddings.multimodal_embeddings_chunks
                await conn.execute("""
                    INSERT INTO embeddings.multimodal_embeddings_chunks
                    (embedding_id, reference_id, reference_type, text_content, image_url, embedding, model_name, created_at, updated_at, chunk_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (embedding_id) DO UPDATE
                    SET reference_id = $2, reference_type = $3, text_content = $4, image_url = $5,
                        embedding = $6, model_name = $7, updated_at = $9, chunk_id = $10
                """,
                    embedding_id,                # embedding_id
                    reference_id,                # reference_id
                    reference_type,              # reference_type
                    text_content,                # text_content
                    image_url,                   # image_url
                    embedding_vector,            # embedding (not embedding_vector)
                    model_name or 'voyage-multimodal-3',  # model_name
                    datetime.now(),              # created_at
                    datetime.now(),              # updated_at
                    chunk_id                     # chunk_id
                )
                
                logger.info(f"Migrated embedding {embedding_id} to embeddings.multimodal_embeddings_chunks with chunk_id {chunk_id}")
                
                # Insert into metadata.frame_details_chunks
                if reference_type == 'frame':
                    # Check if this frame already exists in metadata.frame_details_chunks
                    existing_chunk = await conn.fetchrow("""
                        SELECT frame_id FROM metadata.frame_details_chunks
                        WHERE frame_id = $1
                    """, reference_id)
                    
                    if existing_chunk:
                        logger.info(f"Frame {reference_id} already exists in metadata.frame_details_chunks, updating")
                        
                    await conn.execute("""
                        INSERT INTO metadata.frame_details_chunks
                        (frame_id, description, summary, tools_used, actions_performed, ocr_data, chunk_id, reference_id)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (frame_id) DO UPDATE
                        SET description = $2, summary = $3, tools_used = $4, actions_performed = $5,
                            ocr_data = $6, chunk_id = $7, reference_id = $8
                    """,
                        reference_id,                   # frame_id (primary key in this table)
                        f"Chunk for {reference_id}",    # description
                        text_content,                   # summary
                        ["AutoTokenizer"],              # tools_used as TEXT[]
                        ["OCR Processing"],             # actions_performed as TEXT[]
                        text_content,                   # ocr_data
                        chunk_id,                       # chunk_id
                        reference_id                    # reference_id
                    )
                    
                    logger.info(f"Migrated chunk {chunk_id} to metadata.frame_details_chunks with frame_id {reference_id}")
                    
                    # Check if this frame already has a process record
                    existing_process = await conn.fetchrow("""
                        SELECT id FROM metadata.process_frames_chunks
                        WHERE frame_id = $1 AND chunk_id = $2
                    """, reference_id, chunk_id)
                    
                    if not existing_process:
                        # Insert into metadata.process_frames_chunks
                        await conn.execute("""
                            INSERT INTO metadata.process_frames_chunks
                            (frame_id, chunk_id, processing_status, chunk_type, chunk_format, processing_metadata)
                            VALUES ($1, $2, $3, $4, $5, $6)
                        """,
                            reference_id,                            # frame_id
                            chunk_id,                                # chunk_id
                            'completed',                             # processing_status
                            'text',                                  # chunk_type
                            'text/plain',                            # chunk_format
                            {"processor": "AutoTokenizer", "version": "1.0"}  # processing_metadata
                        )
                        
                        logger.info(f"Added process record for chunk {chunk_id} to metadata.process_frames_chunks")
            
            except Exception as e:
                logger.error(f"Error migrating chunk data for embedding {embedding_id}: {e}")
    
    logger.info("Chunk data migration complete")

async def populate_multimodal_embeddings_chunks(pool):
    """
    Populate embeddings.multimodal_embeddings_chunks from multimodal_embeddings.
    Copy all chunk embeddings to the new chunks table.
    """
    async with pool.acquire() as conn:
        # Get all chunk embeddings
        chunk_rows = await conn.fetch('''
            SELECT embedding_id, reference_id, reference_type, text_content, 
                   image_url, embedding, model_name, created_at
            FROM embeddings.multimodal_embeddings
            WHERE reference_type = 'chunk'
        ''')
        
        count = 0
        for row in chunk_rows:
            chunk_ref_id = row['reference_id']
            
            # Get the chunk_id from frame_details_chunks
            chunk_row = await conn.fetchrow('''
                SELECT chunk_id FROM metadata.frame_details_chunks
                WHERE reference_id = $1
            ''', chunk_ref_id)
            
            if not chunk_row:
                logger.warning(f"No metadata found for chunk: {chunk_ref_id}")
                continue
                
            chunk_id = chunk_row['chunk_id']
            
            # Check if this chunk embedding already exists
            existing = await conn.fetchrow('''
                SELECT embedding_id FROM embeddings.multimodal_embeddings_chunks
                WHERE reference_id = $1
            ''', chunk_ref_id)
            
            if not existing:
                # Insert into multimodal_embeddings_chunks
                await conn.execute('''
                    INSERT INTO embeddings.multimodal_embeddings_chunks
                    (embedding_id, reference_id, reference_type, text_content, 
                     image_url, embedding, model_name, created_at, updated_at, chunk_id)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                ''', 
                uuid.uuid4(), # new embedding_id
                chunk_ref_id, # reference_id
                'chunk', # reference_type
                row['text_content'], # text_content
                row['image_url'], # image_url
                row['embedding'], # embedding
                row['model_name'], # model_name
                row['created_at'], # created_at
                datetime.now(), # updated_at
                chunk_id # chunk_id
                )
                
                count += 1
        
        logger.info(f"Migrated {count} chunk embeddings to multimodal_embeddings_chunks")

async def create_frames_for_embeddings(pool):
    """Create entries in content.frames for each unique frame_id from embeddings.multimodal_embeddings."""
    logger.info("Creating frames in content.frames...")
    
    async with pool.acquire() as conn:
        # Get all unique frame reference_ids from multimodal_embeddings
        frames = await conn.fetch("""
            SELECT DISTINCT reference_id, image_url
            FROM embeddings.multimodal_embeddings
            WHERE reference_type = 'frame'
        """)
        
        logger.info(f"Found {len(frames)} unique frames to create in content.frames")
        
        count = 0
        for frame in frames:
            reference_id = frame['reference_id']
            image_url = frame['image_url']
            
            # Check if the frame already exists
            existing = await conn.fetchval("""
                SELECT 1 FROM content.frames 
                WHERE frame_id = $1
            """, reference_id)
            
            if existing:
                logger.info(f"Frame {reference_id} already exists in content.frames, skipping")
                continue
            
            # Extract timestamp and frame_number from frame_id if possible
            # Format is typically frame_000051.jpg
            frame_number = None
            timestamp = 0.0
            filename = reference_id
            folder_name = None
            
            try:
                if filename.startswith("frame_"):
                    # Extract frame number if possible
                    parts = filename.replace(".jpg", "").split("_")
                    if len(parts) > 1:
                        frame_number = int(parts[1])
                        # Use frame number as timestamp as a fallback
                        timestamp = float(frame_number) / 30.0  # Assume 30fps
                
                # Extract folder name from image_url if possible
                if image_url:
                    path_parts = image_url.split('/')
                    if len(path_parts) > 2:
                        folder_name = path_parts[-2]
            except:
                pass
            
            try:
                # Insert into content.frames
                await conn.execute("""
                    INSERT INTO content.frames
                    (frame_id, timestamp, frame_number, image_url, folder_name, file_name, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                    reference_id,  # frame_id
                    timestamp,     # timestamp
                    frame_number,  # frame_number
                    image_url,     # image_url
                    folder_name,   # folder_name
                    filename,      # file_name
                    datetime.now() # created_at
                )
                
                count += 1
                logger.info(f"Created frame {reference_id} in content.frames")
            except Exception as e:
                logger.error(f"Error creating frame {reference_id} in content.frames: {e}")
        
        logger.info(f"Created {count} frames in content.frames")

async def create_indexes(pool):
    """Create necessary indexes for better query performance."""
    async with pool.acquire() as conn:
        # Indexes on embeddings.multimodal_embeddings
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_multimodal_embeddings_reference_id ON embeddings.multimodal_embeddings(reference_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_multimodal_embeddings_reference_type ON embeddings.multimodal_embeddings(reference_type)')
        
        # Indexes on embeddings.multimodal_embeddings_chunks
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_multimodal_embeddings_chunks_reference_id ON embeddings.multimodal_embeddings_chunks(reference_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_multimodal_embeddings_chunks_chunk_id ON embeddings.multimodal_embeddings_chunks(chunk_id)')
        
        # Indexes on metadata.frame_details_full
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_frame_details_full_reference_id ON metadata.frame_details_full(reference_id)')
        
        # Indexes on metadata.frame_details_chunks
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_frame_details_chunks_reference_id ON metadata.frame_details_chunks(reference_id)')
        await conn.execute('CREATE INDEX IF NOT EXISTS idx_frame_details_chunks_frame_id ON metadata.frame_details_chunks(frame_id)')
        
        logger.info("Created performance indexes")

async def populate_process_frames_chunks(pool):
    """Populate process_frames_chunks table with data from frame_details_chunks."""
    async with pool.acquire() as conn:
        # Get chunks that don't have an entry in process_frames_chunks
        chunks = await conn.fetch('''
            SELECT c.chunk_id, c.frame_id, c.reference_id
            FROM metadata.frame_details_chunks c
            LEFT JOIN metadata.process_frames_chunks p ON c.chunk_id = p.chunk_id
            WHERE p.id IS NULL
        ''')
        
        count = 0
        for chunk in chunks:
            # Get the frame's airtable_record_id (if available)
            frame = await conn.fetchrow('''
                SELECT technical_details->>'airtable_record_id' as airtable_record_id 
                FROM metadata.frame_details_full 
                WHERE frame_id = $1
            ''', chunk['frame_id'])
            
            airtable_record_id = frame['airtable_record_id'] if frame and frame['airtable_record_id'] else None
            
            # Create processing metadata
            processing_metadata = {
                'source': 'migration',
                'migration_timestamp': datetime.now().isoformat(),
                'chunk_reference_id': chunk['reference_id']
            }
            
            # Insert into process_frames_chunks
            await conn.execute('''
                INSERT INTO metadata.process_frames_chunks
                (frame_id, chunk_id, airtable_record_id, processing_status, chunk_type, chunk_format, 
                 processing_metadata, processing_timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ''', 
            chunk['frame_id'], 
            chunk['chunk_id'], 
            airtable_record_id,
            'migrated', 
            'text', 
            'plain', 
            json.dumps(processing_metadata),
            datetime.now()
            )
            
            count += 1
        
        logger.info(f"Created {count} entries in process_frames_chunks")

async def verify_table_counts(pool):
    """Verify table counts after migration."""
    async with pool.acquire() as conn:
        tables = [
            'embeddings.multimodal_embeddings',
            'embeddings.multimodal_embeddings_chunks',
            'metadata.frame_details_full',
            'metadata.frame_details_chunks',
            'metadata.process_frames_chunks'
        ]
        
        logger.info("Table counts after migration:")
        for table in tables:
            count = await conn.fetchval(f'SELECT COUNT(*) FROM {table}')
            logger.info(f"  {table}: {count} rows")

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
        
        # Check dimensions in multimodal_embeddings_chunks
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

async def main():
    """Execute the migration process."""
    logger.info("Starting migration process...")
    
    # Create connection pool
    pool = await create_connection_pool()
    
    try:
        # Run migration steps
        await ensure_schemas_exist(pool)
        await ensure_tables_exist(pool)
        await normalize_reference_ids(pool)
        
        # Create frames first
        await create_frames_for_embeddings(pool)
        
        # Then migrate data to dependent tables
        await migrate_frame_data(pool)
        await migrate_chunk_data(pool)
        await populate_multimodal_embeddings_chunks(pool)
        await create_indexes(pool)
        await populate_process_frames_chunks(pool)
        await verify_table_counts(pool)
        await verify_embedding_vector_dimensions(pool)
        
        logger.info("Migration completed successfully")
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        # Close connection pool
        await pool.close()
        logger.info("PostgreSQL connection pool closed")

if __name__ == "__main__":
    asyncio.run(main()) 