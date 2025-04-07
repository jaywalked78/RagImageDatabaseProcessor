# Project Reorganization Plan

## New Folder Structure

```
DatabaseAdvancedTokenizer/
├── src/                      # Main source code
│   ├── embeddings/           # Embedding-related code
│   ├── database/             # Database interactions
│   ├── utils/                # Utility functions
│   ├── api/                  # API integrations
│   └── processors/           # Frame processing code
├── scripts/                  # Utility scripts
└── tests/                    # Test files
```

## Files to Move

### src/embeddings/
- `embedding_store.py` (New file that will contain the embedding classes from test_chunk_embedding.py)
- `chunk_embedder.py` (New file that will extract the ChunkEmbedder class)

### src/database/
- `postgres_vector_store.py` (New file that will contain PostgreSQL vector store)
- `airtable_store.py` (New file that will contain Airtable-related classes)
- `local_database.py` (Move existing file)

### src/utils/
- `metadata_utils.py` (New file that will contain metadata processing functions)
- `chunking.py` (New file that will contain text chunking logic)
- `file_utils.py` (New file that will contain file handling functions)

### src/api/
- `google_drive.py` (New file that will contain Google Drive functions)
- `webhook.py` (New file that will contain webhook integration)
- `voyage_api.py` (New file that will contain Voyage API functions)

### src/processors/
- `frame_processor.py` (New file with core frame processing logic)
- `batch_processor.py` (New file with batch processing logic)
- `local_frames_processor.py` (Move existing file)

### scripts/
- `process_local_frames.sh` (Move existing file)
- `process_drive_folder.sh` (Move existing file)
- `batch_process.sh` (New utility script)

### tests/
- Organized test files based on functionality

## Implementation Plan

1. Create a proper Python package structure with `__init__.py` files
2. Extract reusable components from test files into proper modules
3. Update imports to use the new module structure
4. Write a simple test script to verify functionality of reorganized code
5. Update documentation to reflect new structure

## Migration Steps

1. First create the new module files with proper imports
2. Test functionality of each module individually
3. Gradually refactor test scripts to use the new module structure
4. Once everything is working, move old test files to a legacy folder

## File Mapping

| Current File | New Location/Files |
|--------------|-------------------|
| test_chunk_embedding.py | src/embeddings/chunk_embedder.py<br>src/database/postgres_vector_store.py<br>src/api/webhook.py |
| test_batch_chunk_embedding.py | src/processors/batch_processor.py |
| local_processor_local_frames.py | src/processors/local_frames_processor.py |
| local_database.py | src/database/local_database.py |
| google_drive_downloader.py | src/api/google_drive.py |
| test_frame_airtable_match.py | src/database/airtable_store.py |
| test_metadata_chunking.py | src/utils/metadata_utils.py<br>src/utils/chunking.py |

## Main Application Files

We'll also create proper application entry points:
- `process_frames.py` - Command-line tool for processing frames
- `export_embeddings.py` - Command-line tool for exporting embeddings
- `download_frames.py` - Command-line tool for downloading frames 