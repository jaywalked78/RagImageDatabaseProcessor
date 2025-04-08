# Embedding System Updates

## Overview
This document outlines the recent updates to the embedding storage and processing system. These changes ensure that embedding vectors are properly stored in multiple tables with consistent reference IDs, making retrieval and matching more efficient.

## Key Changes

### 1. Consistent Reference ID Format
- All reference IDs now use underscores instead of slashes to maintain consistency: `folderName_filename`
- Frame reference IDs follow the format: `folderName_filename`
- Chunk reference IDs follow the format: `folderName_filename_chunk_chunkNumber`
- This format is maintained across all tables in both metadata and embeddings schemas

### 2. Added Multimodal Embeddings Chunks Table
- Created a new table `embeddings.multimodal_embeddings_chunks` specifically for chunk embeddings
- All chunk embeddings are now stored in both:
  - Original `embeddings.multimodal_embeddings` table (for backward compatibility)
  - New `embeddings.multimodal_embeddings_chunks` table (for optimized searches)
- Both tables maintain identical reference IDs for consistency

### 3. Enhanced ID Tracking
- Improved the export of ID mappings to CSV files
- Added `has_multimodal_embedding` and `multimodal_embedding_id` to chunk exports
- Added dimensions tracking to better handle different embedding models

### 4. Search Functionality
- Updated embedding search to work with both embedding tables
- Added table parameter to specify which embedding table to use:
  - `default` for regular embeddings table
  - `multimodal_chunks` for the new chunks-specific table

### 5. Processing Status Tracking
- Enhanced the `metadata.process_frames_chunks` table to store processing information
- Added detailed metadata to track the status of each chunk processing operation

## Database Table Structure

### Metadata Schema
- `metadata.frame_details_full`: Complete frame information with all metadata
- `metadata.frame_details`: Core frame details with reference IDs
- `metadata.chunk_details_full`: Complete chunk information with all metadata
- `metadata.chunk_details`: Core chunk details with reference IDs
- `metadata.process_frames_chunks`: Processing status and metadata for chunks

### Embeddings Schema
- `embeddings.multimodal_embeddings`: Original embeddings table for both frames and chunks
- `embeddings.multimodal_embeddings_chunks`: New table specifically for chunk embeddings

## Reference ID Examples

| Entity Type | Example Reference ID |
|-------------|----------------------|
| Frame | `test_batch_sample_frame_0.jpg` |
| Chunk | `test_batch_sample_frame_0.jpg_chunk_0` |

## CSV Export Format
The system now exports four CSV files:
- `frames.csv`: Complete frame data with metadata
- `frame_id_mapping.csv`: Mapping between frame IDs and reference IDs
- `chunks.csv`: Complete chunk data with metadata
- `chunk_id_mapping.csv`: Mapping between chunk IDs, reference IDs, and multimodal embedding IDs

## Next Steps
- Create database indexes on reference IDs to optimize search operations
- Add database migration script to convert existing reference IDs to new format
- Implement performance optimization for vector similarity search
- Add automatic cleanup of orphaned embeddings 