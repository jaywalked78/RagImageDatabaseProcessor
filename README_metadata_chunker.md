# Metadata Chunking for RAG Pipeline

This implementation provides a flexible and efficient system for processing frame metadata from Airtable into semantic chunks suitable for RAG (Retrieval-Augmented Generation) applications. It follows the requirements specified in the RAG Pipeline Implementation Plan.

## Key Components

### 1. MetadataChunker

`metadata_chunker.py` contains the core `MetadataChunker` class that handles:

- Converting structured metadata into a text representation
- Chunking the text semantically using LangChain's RecursiveCharacterTextSplitter
- Maintaining source information and sequence IDs for each chunk
- Preserving the full metadata as context for each chunk

### 2. Airtable Integration

`test_metadata_chunking.py` demonstrates how to:

- Connect to Airtable and find frame metadata
- Match frames based on frame number and folder name
- Process the metadata through the chunker

### 3. Batch Processing

`test_batch_processing.py` provides batch processing capabilities:

- Process multiple frames in sequence
- Track success/failure rates
- Generate statistics about the chunking process

## Usage

### Basic Usage

```python
# Initialize the chunker
chunker = MetadataChunker(chunk_size=500, chunk_overlap=50)

# Process metadata into chunks
chunks = chunker.process_metadata(metadata, record_id, frame_path)

# Each chunk contains:
# - chunk_text: The text content of the chunk
# - chunk_sequence_id: Order within the original document
# - metadata: Full metadata for context
# - source: Information about where this chunk came from
```

### Running the Test Scripts

Process a single frame:

```bash
python test_metadata_chunking.py /path/to/frame.jpg [--chunk-size 500] [--chunk-overlap 50]
```

Process multiple frames:

```bash
python test_batch_processing.py /path/to/frames/directory [--limit 10] [--chunk-size 500] [--chunk-overlap 50]
```

## Integration with RAG Pipeline

In the full RAG pipeline implementation, these chunks would be:

1. Embedded using the voyageai multimodal embedding model
2. Stored in Supabase with their embeddings
3. Retrieved via hybrid search (semantic + keyword)
4. Used for context assembly and LLM generation

## Customization

The chunking parameters can be adjusted:

- **chunk_size**: Target size for each chunk (default: 500 characters)
- **chunk_overlap**: Overlap between consecutive chunks (default: 50 characters)

## Technical Details

- Uses LangChain's RecursiveCharacterTextSplitter for semantic chunking
- Falls back to a simple paragraph-based chunker if LangChain is not available
- Handles structured metadata with fields like Summary, ToolsVisible, ActionsDetected, etc.
- Preserves the full context in each chunk for accurate retrieval 