# RAG Image Database Processor

A comprehensive toolkit for processing screen recording frames, extracting metadata, creating embeddings, and storing in a vector database for RAG (Retrieval Augmented Generation) applications.

## Project Overview

This project provides a pipeline for:
1. Processing image frames from screen recordings
2. Extracting and structuring metadata
3. Chunking content for optimal retrieval
4. Creating vector embeddings using Voyage AI
5. Storing results in PostgreSQL (Supabase) vector database
6. Integrating with n8n workflows via webhooks

## Project Structure

```
RagImageDatabaseProcessor/
├── main.py                  # Main entry point
├── src/                     # Main source code
│   ├── api/                 # API integrations
│   ├── connectors/          # External service connections  
│   ├── database/            # Database interactions
│   ├── embeddings/          # Embedding-related code
│   ├── models/              # Data models
│   ├── processors/          # Data processing modules
│   └── utils/               # Utility functions
├── scripts/                 # Utility scripts
│   ├── process_frames.py    # Process frames from a directory
│   ├── export_embeddings.py # Export embeddings from database
│   └── download_frames.py   # Download frames from Google Drive
├── tests/                   # Test files
└── payloads/                # Webhook payload storage
    ├── json/                # JSON payload files
    └── csv/                 # CSV logs of operations
```

## Features

- **Frame Processing**: Process image frames with metadata extraction
- **Semantic Chunking**: Create semantic chunks for optimal retrieval
- **Vector Embeddings**: Generate embeddings using Voyage AI models
- **Vector Database**: Store and query embeddings in PostgreSQL/Supabase
- **n8n Integration**: Send data to n8n workflows via webhooks
- **Local Storage**: Option to store all data locally without external services
- **Batch Processing**: Process multiple frames sequentially or in parallel

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL database (or Supabase account)
- Voyage AI API key for embeddings
- Airtable account (optional)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/jaywalked78/RagImageDatabaseProcessor.git
   cd RagImageDatabaseProcessor
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Copy the example environment file:
   ```
   cp .env.example .env
   ```

5. Edit `.env` with your credentials and configuration

### Usage

#### Process a single frame:

```bash
python main.py --input /path/to/frame.jpg
```

#### Batch process frames from a directory:

```bash
python scripts/process_frames.py --input /path/to/directory --pattern "*.jpg" --limit 10
```

#### Export embeddings from the database:

```bash
python scripts/export_embeddings.py --output embeddings.json
```

#### Store data locally without sending to webhook:

```bash
python main.py --input /path/to/frame.jpg --local-only --local-storage-dir "data"
```

## Configuration

The application uses environment variables for configuration:

- `POSTGRES_HOST`: PostgreSQL host
- `POSTGRES_PORT`: PostgreSQL port
- `POSTGRES_USER`: PostgreSQL username
- `POSTGRES_PASS`: PostgreSQL password
- `POSTGRES_DB`: PostgreSQL database name
- `VOYAGE_API_KEY`: Voyage AI API key
- `AIRTABLE_PERSONAL_ACCESS_TOKEN`: Airtable PAT token
- `AIRTABLE_BASE_ID`: Airtable base ID
- `WEBHOOK_URL`: n8n webhook URL
- `FRAME_BASE_DIR`: Base directory for frames

## License

This project is licensed under the MIT License - see the LICENSE file for details. 