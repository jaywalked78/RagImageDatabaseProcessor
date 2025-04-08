# Database Migration and Verification

This document provides instructions for migrating and verifying the embedding tables and their reference IDs in the Supabase database.

## Overview

The migration involves:

1. Updating reference IDs to use underscores instead of slashes (`folder_name_filename` instead of `folder_name/filename`)
2. Populating the `multimodal_embeddings_chunks` table in the `embeddings` schema
3. Populating the `frame_details_full` and `frame_details_chunks` tables in the `metadata` schema
4. Ensuring consistent reference IDs across all tables

## Prerequisites

Ensure you have the following:

1. Python 3.8 or higher
2. Required Python packages: `asyncpg`, `dotenv`
3. Database connection credentials in a `.env` file

Create a `.env` file with the following variables:

```
SUPABASE_DB_HOST=aws-0-us-east-1.pooler.supabase.com
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=your_username
SUPABASE_DB_PASSWORD=your_password
EMBEDDING_DIM=1024
```

## Migration Steps

### 1. Run the Migration Script

The migration script will:
- Ensure all necessary schemas and tables exist
- Migrate data from `multimodal_embeddings` to `multimodal_embeddings_chunks`
- Update reference IDs to use underscores instead of slashes
- Populate metadata tables using data from embedding tables

```bash
python migrate_embedding_tables.py
```

### 2. Verify the Migration

After migration, run the verification script to ensure all tables have consistent data and correct reference ID formats:

```bash
python verify_embedding_tables.py
```

This script will check:
- All required tables exist and have data
- All reference IDs follow the correct format (using underscores)
- Reference IDs are consistent across schemas
- Chunk reference IDs properly relate to their parent frames
- Embedding vectors have the correct dimensions

## Table Structure

### Embeddings Schema

#### multimodal_embeddings
- `id`: UUID (primary key)
- `reference_id`: Text (format: `folder_name_filename` for frames, `folder_name_filename_chunk_X` for chunks)
- `reference_type`: Text ('frame' or 'chunk')
- `embedding`: Vector(1024)
- `text_content`: Text
- `image_url`: Text
- `model_name`: Text
- `creation_time`: Timestamp

#### multimodal_embeddings_chunks
- `id`: UUID (primary key)
- `reference_id`: Text (format: `folder_name_filename_chunk_X`)
- `chunk_id`: Integer (references `metadata.frame_details_chunks.chunk_id`)
- `embedding_vector`: Vector(1024)
- `text_content`: Text
- `model_name`: Text
- `dimensions`: Integer
- `creation_time`: Timestamp

### Metadata Schema

#### frame_details_full
- `frame_id`: Serial (primary key)
- `reference_id`: Text (format: `folder_name_filename`)
- `frame_name`: Text
- `folder_name`: Text
- `google_drive_url`: Text
- `airtable_record_id`: Text
- `description`: Text
- `summary`: Text
- `frame_metadata`: JSONB
- `created_at`: Timestamp
- `updated_at`: Timestamp

#### frame_details_chunks
- `chunk_id`: Serial (primary key)
- `frame_id`: Integer (references `frame_details_full.frame_id`)
- `reference_id`: Text (format: `folder_name_filename_chunk_X`)
- `chunk_sequence_id`: Integer
- `chunk_text`: Text
- `metadata`: JSONB
- `created_at`: Timestamp
- `updated_at`: Timestamp

#### process_frames_chunks
- `id`: Serial (primary key)
- `frame_id`: Integer (references `frame_details_full.frame_id`)
- `chunk_id`: Integer (references `frame_details_chunks.chunk_id`)
- `airtable_record_id`: Text
- `processing_status`: Text
- `chunk_type`: Text
- `chunk_format`: Text
- `processing_metadata`: JSONB
- `processing_timestamp`: Timestamp

## Troubleshooting

If you encounter issues during migration or verification:

1. **Connection Issues**: Check your .env file and make sure your credentials are correct
2. **Missing Tables**: The migration script should create missing tables, but verify permissions
3. **Reference ID Format**: If some reference IDs are still using slashes, manually update them
4. **Vector Dimensions**: If vector dimensions are incorrect, check the `EMBEDDING_DIM` environment variable

## Backup Recommendation

It's recommended to take a database backup before running the migration script:

```bash
pg_dump -h aws-0-us-east-1.pooler.supabase.com -p 5432 -U your_username -d postgres -n embeddings -n metadata > embedding_metadata_backup.sql
``` 