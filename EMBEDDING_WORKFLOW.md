# Database Advanced Tokenizer - Embedding Workflow

This document outlines the workflow for processing frames (images), extracting chunks, generating embeddings, and ensuring consistent reference IDs across both metadata and embeddings schemas.

## Architecture Overview

The system uses a hybrid approach to store and retrieve data:

1. **Content Schema**: Stores the raw frame and chunk data
2. **Metadata Schema**: Stores metadata about frames and chunks with reference IDs
3. **Embeddings Schema**: Stores vector embeddings with matching reference IDs

## Reference ID Format

To maintain consistency and proper linking between schemas, we use standardized reference ID formats:

- **Frames**: `folder_name/frame_name` (e.g., `images_batch1/frame001.jpg`)
- **Chunks**: `folder_name/frame_name/chunk_sequence_id` (e.g., `images_batch1/frame001.jpg/chunk_0`)

## Processing Workflow

The complete workflow for processing a frame and its chunks works as follows:

### 1. Frame Processing

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐
│  Process    │     │   Generate   │     │   Store in Tables   │
│   Image     │────►│  Embedding   │────►│  - content.frames   │
│             │     │             │     │  - metadata.frame_details_full │
└─────────────┘     └─────────────┘     │  - embeddings.multimodal_embeddings │
                                        └─────────────────────┘
```

### 2. Chunk Processing

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────────┐
│  Extract    │     │   Generate   │     │   Store in Tables   │
│   Chunks    │────►│  Embeddings  │────►│  - content.chunks   │
│             │     │             │     │  - metadata.frame_details_chunk │
└─────────────┘     └─────────────┘     │  - embeddings.multimodal_embeddings │
                                        └─────────────────────┘
```

### 3. Reference ID Synchronization

When data is stored, the system ensures consistent reference IDs:

1. The frame is stored in `content.frames` with its folder and file name
2. A reference ID is created in the format `folder_name/frame_name`
3. This reference ID is stored in both:
   - `metadata.frame_details_full.reference_id`
   - `embeddings.multimodal_embeddings.reference_id` (with reference_type='frame')

Similarly for chunks:

1. The chunk is stored in `content.chunks` with its frame ID and sequence ID
2. A reference ID is created in the format `folder_name/frame_name/chunk_sequence_id`
3. This reference ID is stored in both:
   - `metadata.frame_details_chunk.reference_id`
   - `embeddings.multimodal_embeddings.reference_id` (with reference_type='chunk')

## Database Schema Relationships

```
┌───────────────────┐     ┌─────────────────────────┐     ┌────────────────────────────┐
│  Content Schema   │     │    Metadata Schema      │     │    Embeddings Schema       │
│                   │     │                         │     │                            │
│  frames           │◄────┤  frame_details_full     │     │                            │
│  - id             │     │  - frame_id             │     │                            │
│  - frame_name     │     │  - reference_id ────────┼────►│  multimodal_embeddings     │
│  - folder_name    │     │  - description          │     │  - embedding_id            │
│                   │     │  - summary              │     │  - reference_id            │
│  chunks           │◄────┤  frame_details_chunk    │     │  - reference_type          │
│  - id             │     │  - chunk_id             │     │  - embedding               │
│  - frame_id       │     │  - reference_id ────────┼────►│  - model_name              │
│  - chunk_text     │     │  - chunk_sequence_id    │     │                            │
└───────────────────┘     └─────────────────────────┘     └────────────────────────────┘
```

## Embedding Storage

The system stores embeddings in two locations:

1. **Metadata Schema**:
   - `metadata.frame_embeddings`: Stores frame embeddings with reference to `content.frames`
   - `metadata.chunk_embeddings`: Stores chunk embeddings with reference to `content.chunks`

2. **Embeddings Schema**:
   - `embeddings.multimodal_embeddings`: Universal embedding storage with `reference_id` and `reference_type`

## Search Process

When searching using embeddings:

1. The query text is converted to an embedding
2. This embedding is compared against stored embeddings in the vector database
3. Matches are returned with their associated reference IDs
4. The reference IDs can be used to fetch detailed metadata from the metadata schema
5. Same reference IDs can be used to link to original content in the content schema

## CSV Export

The system also exports data to CSV files for local storage and backup:

1. **frames.csv**: Contains frame data with embeddings and reference IDs
2. **chunks.csv**: Contains chunk data with embeddings and reference IDs

## Implementation Steps

To ensure proper synchronization:

1. **Always use the PostgresVectorStore class** for storing frames, chunks, and embeddings
2. The class takes care of creating consistent reference IDs across schemas
3. Use the `update_reference_ids.py` script to fix any inconsistencies in existing data
4. Verify reference ID consistency using the `verify_reference_ids.py` script
5. Run the example workflow in `process_embedding_workflow.py` to test the entire process

## Error Handling

The system includes error handling and logging to:

1. Detect missing or inconsistent reference IDs
2. Report reference ID mismatches between schemas
3. Log detailed information about each processing step

## Common Issues

1. **Inconsistent reference IDs**: If schemas get out of sync, use `update_reference_ids.py`
2. **Missing folder names**: Folder names are required for proper reference ID creation
3. **Empty tables**: Make sure to run the migration script if tables are empty or missing 