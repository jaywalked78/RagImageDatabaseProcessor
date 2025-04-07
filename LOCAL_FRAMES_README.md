# Local Frames Processor

This solution provides an efficient way to process locally stored frames with embeddings, while minimizing API calls. It handles frames already stored in your local directory (`/home/jason/Videos/screenRecordings`), creates a local SQLite database for metadata, and processes frames with Voyage embeddings.

## Features

- **Process Existing Local Frames**: Works with your existing frame files in `/home/jason/Videos/screenRecordings`
- **Local SQLite Database**: Stores all metadata, chunks, and embeddings locally
- **Minimal API Calls**: Only calls Voyage API for creating embeddings, avoiding unnecessary Airtable calls
- **Google Drive URL Integration**: Links local frames to Google Drive URLs for database references
- **Batch Export**: Efficient batch export to PostgreSQL and webhooks
- **Parallel Processing**: Process multiple frames in parallel for faster throughput

## Setup

1. Make sure all required Python packages are installed:
   ```bash
   pip install numpy pillow dotenv requests
   ```

2. Set up environment variables for the database connection and API keys:
   ```bash
   # PostgreSQL connection
   export POSTGRES_HOST=your_host
   export POSTGRES_PORT=your_port
   export POSTGRES_USER=your_user
   export POSTGRES_PASSWORD=your_password
   export POSTGRES_DB=your_database
   
   # Voyage API keys
   export VOYAGE_API_KEY=your_key
   
   # Webhook URLs (optional)
   export WEBHOOK_URL=your_webhook_url
   export WEBHOOK_TEST_URL=your_test_webhook_url
   export USE_TEST_WEBHOOK=false
   
   # Frame base directory (optional, default is /home/jason/Videos/screenRecordings)
   export FRAME_BASE_DIR=/home/jason/Videos/screenRecordings
   ```

3. Make sure the script is executable:
   ```bash
   chmod +x process_local_frames.sh
   ```

## Usage

The easiest way to use this solution is with the provided shell script:

```bash
./process_local_frames.sh [OPTIONS]
```

### Full Process Example

To process all frames with a Google Drive folder reference:

```bash
./process_local_frames.sh --drive-folder-id YOUR_FOLDER_ID --parallel 10 --max-chunks 5
```

### Step-by-Step Processing

You can also process frames in steps:

1. First, load frames into the local database:
   ```bash
   ./process_local_frames.sh --load-only --drive-folder-id YOUR_FOLDER_ID
   ```

2. Then process them to create embeddings:
   ```bash
   ./process_local_frames.sh --process-only --parallel 10 --max-chunks 5
   ```

3. Finally, export the embeddings:
   ```bash
   ./process_local_frames.sh --export-only
   ```

### Available Options

- `--frames-dir DIR`: Directory containing frames (default: `/home/jason/Videos/screenRecordings`)
- `--pattern PATTERN`: Glob pattern to match frames (default: `**/*.jpg`)
- `--drive-folder-id ID`: Google Drive folder ID for URL references
- `--parallel N`: Number of frames to process in parallel (default: 5)
- `--max-chunks N`: Maximum number of chunks per frame (default: 10)
- `--chunk-size N`: Size of text chunks (default: 500)
- `--chunk-overlap N`: Overlap between chunks (default: 50)
- `--limit N`: Maximum number of frames to process
- `--db-path PATH`: Path to database file (default: `frames_local.db`)

## How It Works

1. **Frame Discovery**: The script scans your local directory for frame files.
2. **Local Database**: Frames and their metadata are stored in a SQLite database.
3. **Text Chunking**: Frame metadata is split into chunks for embedding.
4. **Embedding**: The script calls the Voyage API to create embeddings for each chunk.
5. **Batch Export**: Processed embeddings are exported to PostgreSQL and/or webhooks in batches.

## Database Schema

The local SQLite database contains the following tables:

- `folders`: Stores information about frame folders
- `frames`: Stores information about individual frames
- `metadata`: Stores metadata associated with frames
- `chunks`: Stores text chunks generated from metadata
- `embeddings`: Stores embeddings generated for chunks

## Benefits Over Previous Solution

- **No Download Step**: Uses frames that are already stored locally
- **Reduced API Calls**: No Airtable API calls required during processing
- **More Efficient Storage**: Stores everything in a local SQLite database
- **URL References**: Maintains Google Drive URL references for database integration
- **Faster Processing**: More efficient parallel processing of local files

## Troubleshooting

- **Missing Tables in PostgreSQL**: The processor will check for required tables in PostgreSQL and warn if they're missing
- **API Rate Limits**: The processor manages Voyage API keys and retries with exponential backoff
- **Missing Metadata**: If no metadata is found for a frame, it will use the frame name as basic metadata 