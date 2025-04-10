# MinimalistRagIntake

A minimalist system for processing screen recordings, extracting text content, and generating image URLs for Retrieval Augmented Generation (RAG) applications.

## Overview

MinimalistRagIntake processes screen recording frames to:
1. Extract text content using OCR
2. Chunk text for more efficient retrieval
3. Generate image URLs for frame images
4. Combine text chunks and image URLs into a unified dataset
5. Send processed data via webhooks

## Components

### 1. Text Chunker

The text chunker processes JSON files containing OCR data from screen recording frames:
- Extracts meaningful text from OCR data
- Chunks text into manageable segments
- Organizes chunks with metadata
- Sends processed data via webhook

### 2. Image Server Integration

Integrated with LightweightImageServer to:
- Host frame images via HTTP
- Generate accessible URLs for each frame
- Combine image URLs with text data

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jaywalked78/RagImageDatabaseProcessor.git
   cd RagImageDatabaseProcessor/MinimalistRagIntake
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Usage

### Basic Usage

Process a folder of screen recording frames:

```bash
./run_processor_with_image_server.sh folder_name [test]
```

Arguments:
- `folder_name`: Name of the folder containing frame images
- `test` (optional): Run in test mode (doesn't send to webhook)

### Advanced Usage

Process a specific JSON file:

```bash
./run_processor_with_image_server.sh folder_name path/to/file.json
```

### n8n Integration

For automated workflows with n8n, see [n8n_integration.md](./n8n_integration.md).

## Input/Output

### Input

- JSON files containing OCR data from screen recording frames
- Each file represents a single frame with:
  - Frame metadata
  - Raw OCR text
  - Timestamp

### Output

1. **Text Processing Output**:
   - Chunked text data
   - Webhook payload with structured content
   - Metadata for each chunk

2. **Image Server Output**:
   - JSON file with image URLs
   - Format: `folder_name_YYYYMMDD_HHMMSS.json` (timestamped to prevent overwrites)
   - Symlink: `folder_name_latest.json` for easy access

## Configuration

Edit `.env` file to configure:
- Webhook URL for sending processed data
- Base directory for frame images
- Test mode settings
- Image server connection details

## Scripts

- `run_processor_with_image_server.sh`: Main script for integrated processing
- `process_json_files_v4.py`: Text processing and chunking
- `run.sh`: Starts the API server for receiving processing requests

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a pull request

## License

This project is proprietary and not licensed for public use without explicit permission from the repository owner.

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for version history and updates. 