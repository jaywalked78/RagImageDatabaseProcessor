# Database Schema Updates

This document outlines the updates made to the database schema to ensure proper storage and retrieval of embeddings and metadata.

## Changes Made

1. **Updated Vector Dimensions**
   - Changed embedding dimensions from 500 to 1024 as specified in the `.env` file

2. **Created/Updated Metadata Schema Tables**
   - Added `metadata.frame_details` table with `reference_id` column
   - Created new `metadata.chunk_details` table to store chunk metadata
   - Both tables maintain reference to their respective content tables

3. **Integrated with Embeddings Schema**
   - Ensured embeddings are stored in both `metadata` and `embeddings` schemas
   - Updated `embeddings.multimodal_embeddings` table usage

4. **Reference ID Format**
   - Modified reference ID format to include folder name and file name
   - Frame reference format: `{folder_name}/{frame_name}`
   - Chunk reference format: `{folder_name}/{frame_name}/chunk_{sequence_id}`

5. **Enhanced Logging**
   - Added detailed logging for vector database operations
   - Included schema, table, dimensions, and reference ID in logs

## Database Tables Structure

### Content Schema

```sql
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

CREATE TABLE IF NOT EXISTS content.chunks (
    id SERIAL PRIMARY KEY,
    frame_id INTEGER REFERENCES content.frames(id) ON DELETE CASCADE,
    chunk_sequence_id INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    creation_time TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(frame_id, chunk_sequence_id)
);
```

### Metadata Schema

```sql
CREATE TABLE IF NOT EXISTS metadata.frame_details (
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

CREATE TABLE IF NOT EXISTS metadata.chunk_details (
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

CREATE TABLE IF NOT EXISTS metadata.frame_embeddings (
    id UUID PRIMARY KEY,
    frame_id INTEGER REFERENCES content.frames(id) ON DELETE CASCADE,
    embedding vector(1024),
    model_name TEXT NOT NULL,
    creation_time TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS metadata.chunk_embeddings (
    id UUID PRIMARY KEY,
    chunk_id INTEGER REFERENCES content.chunks(id) ON DELETE CASCADE,
    embedding vector(1024),
    model_name TEXT NOT NULL,
    creation_time TIMESTAMPTZ DEFAULT NOW()
);
```

### Embeddings Schema

```sql
CREATE TABLE IF NOT EXISTS embeddings.multimodal_embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reference_id TEXT NOT NULL,        -- includes folder/filename: "folder/filename" or "folder/filename/chunk_id"
    reference_type TEXT NOT NULL,      -- "frame" or "chunk"
    text_content TEXT,                 -- Text component used for embedding
    image_url TEXT NOT NULL,           -- URL to the image used for embedding
    embedding vector(1024) NOT NULL,   -- Multimodal embedding vector with 1024 dimensions
    model_name TEXT NOT NULL,          -- e.g., 'voyage-multimodal-3'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Implementation Notes

The code now ensures that:

1. When storing frame embeddings:
   - Creates/updates entry in `metadata.frame_embeddings`
   - Creates/updates entry in `metadata.frame_details` with reference_id
   - Creates/updates entry in `embeddings.multimodal_embeddings` with reference_id

2. When storing chunk embeddings:
   - Creates/updates entry in `metadata.chunk_embeddings`
   - Creates/updates entry in `metadata.chunk_details` with reference_id
   - Creates/updates entry in `embeddings.multimodal_embeddings` with reference_id

3. When first connecting to the database:
   - Ensures schemas exist (content, metadata, embeddings)
   - Ensures pgvector extension is available
   - Checks and creates tables if they don't exist
   - Adds reference_id column to existing tables if needed

## Still To Do

1. Verify database connection parameters in `.env` file are correct
2. Check table name discrepancies (test shows "frames" vs "content.frames")
3. Run initial database migration to create all required tables
4. Verify vector dimension in PostgreSQL is set to 1024
5. Populate existing empty tables with data from multimodal_embeddings
6. Create appropriate indexes on reference_id columns for performance 