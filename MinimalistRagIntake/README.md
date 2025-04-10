# MinimalistRagIntake

A lightweight system for processing screen recording frames, extracting metadata, and chunking text for RAG applications, with n8n integration capabilities.

## Overview

MinimalistRagIntake is designed to be a minimal yet efficient system for:

1. Receiving frame data via a REST API
2. Processing frame metadata and content 
3. Chunking text for optimal retrieval
4. Organizing frame and chunk data in a structured format
5. Sending the processed data to n8n webhooks for further processing (including embedding generation)

## Key Features

- **FastAPI REST API**: Exposes endpoints for frame data intake
- **Efficient Chunking**: Splits text content with configurable size and overlap
- **Webhook Integration**: Sends processed data to configurable webhook endpoints
- **Test/Production Modes**: Supports different webhook endpoints for testing and production
- **Structured Output**: Organizes data in a hierarchical structure for n8n processing
- **Image URLs Integration**: *(Coming Soon)* Integration with LightweightImageServer for providing image URLs alongside chunked text data

## System Architecture

### Components

1. **FastAPI Service (`main.py`)**: 
   - REST API for receiving frame data
   - Background processing of frame batches
   - Status monitoring endpoints

2. **Frame Processor (`process_json_files.py`)**:
   - Processes JSON files with frame metadata
   - Chunks text content for better RAG performance
   - Organizes data into a structured format
   - Sends data to webhook endpoints

3. **Utility Scripts**:
   - `run.sh`: Sets up environment and starts the API service
   - `stop.sh`: Gracefully stops the running service
   - `run_processor.sh`: Processes specific folders or files
   - `setup_chunker.sh`: Comprehensive setup script for TheChunker environment
   - `quick_setup.sh`: Simplified setup script for quick deployment
   - `run_processor_with_image_server.sh`: *(Coming Soon)* Processes frames and integrates with LightweightImageServer

### Data Flow

1. **Intake Flow**:
   - External system (n8n) sends frame data to the API
   - Data is saved as JSON files organized by folder
   - In-memory tracking of processed frames is maintained

2. **Processing Flow**:
   - The processor reads JSON files from specified folders
   - For each frame:
     - Extracts metadata and content
     - Chunks the text with proper overlap
     - Structures data with reference IDs for n8n processing

3. **Output Flow**:
   - Processed data is sent to a webhook (configurable for test/production)
   - Structured output includes frame metadata and chunked content
   - n8n can process the data further, including generating embeddings

### Upcoming Integration Flow (Coming Soon)

The upcoming integration with LightweightImageServer will enhance the system by:

1. **Image URL Generation**:
   - Automatically starting the image server when processing frames
   - Loading image files from corresponding frame folders
   - Generating accessible HTTP URLs for all frame images

2. **Enhanced Output Structure**:
   - Adding image URLs to the frame data structure
   - Providing direct links to view the original screenshots
   - Creating a more comprehensive data package for downstream processing

3. **Combined Webhook Delivery**:
   - Sending a single webhook with both text chunks and image URLs
   - Optimizing the entire pipeline for efficiency
   - Providing a complete data set to n8n workflows

## Output Structure

```json
{
  "folder_name": "example_folder",
  "processed_at": "2023-04-09T14:30:45.123456",
  "test_mode": false,
  "frames": [
    {
      "id": "example_folder_frame001",
      "folder_name": "example_folder",
      "file_name": "frame001.jpg",
      "frame_number": "frame001",
      "airtable_record_id": "rec123456",
      "metadata": { ... },
      "content": "...",
      "chunks": [
        {
          "id": "example_folder_frame001_chunk_0",
          "chunk_index": 0,
          "text": "..."
        },
        ...
      ],
      "processed_at": "2023-04-09T14:30:45.123456",
      "test_mode": false
    },
    ...
  ],
  "stats": {
    "total_files": 10,
    "processed": 9,
    "errors": 1
  }
}
```

## n8n Integration

This system is designed to work with n8n workflows:

1. n8n can send frame data to the API for processing
2. Processed data (with chunks) is sent back to n8n via webhooks
3. n8n can then generate embeddings and store the data in appropriate databases

## Getting Started

### Installation

There are two methods to set up the environment:

#### Method 1: Using the Comprehensive Setup Script

This method provides detailed feedback and creates a fully configured environment:

```bash
cd MinimalistRagIntake
chmod +x setup_chunker.sh
./setup_chunker.sh
```

#### Method 2: Using the Quick Setup Script

For a more straightforward setup:

```bash
cd MinimalistRagIntake
chmod +x quick_setup.sh
./quick_setup.sh
```

### Configuration

Edit the `.env` file to configure:
- API host and port
- Data and log directories
- Webhook URLs
- Chunking parameters

### Running the Service

1. Activate the virtual environment:
   ```bash
   source TheChunker/bin/activate
   ```

2. Start the API service:
   ```bash
   ./run.sh
   ```

3. Process frames:
   ```bash
   ./run_processor.sh <folder_name>          # Process in production mode
   ./run_processor.sh <folder_name> test     # Process in test mode
   ./run_processor.sh <folder_name> <file>   # Process a specific file
   ```

4. Stop the service:
   ```bash
   ./stop.sh
   ```

5. Deactivate the virtual environment when done:
   ```bash
   deactivate
   ```

## API Endpoints

- `POST /api/frames/batch`: Receive a batch of frames for processing
- `GET /api/status`: Get the current status of the API
- `GET /api/frames/{folder_path}/{file_name}`: Check if a specific frame has been processed 

## Dependencies

The following dependencies are required and will be installed by the setup scripts:

- fastapi==0.95.1
- uvicorn==0.22.0
- pydantic==1.10.7
- python-dotenv==1.0.0
- requests==2.30.0
- python-multipart==0.0.6 (for handling form data)
- aiofiles==23.1.0 (for asynchronous file operations)
- pillow==9.5.0 (for image processing capabilities) 