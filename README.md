# DatabaseAdvancedTokenizer

Advanced tools for processing, tokenizing, and analyzing screen recordings and image frames for ML/AI applications.

## Overview

This repository contains multiple specialized tools for processing screen recordings and image frames, extracting data, and preparing it for machine learning applications. The modular architecture allows for flexible integration with n8n and other automation platforms.

## Key Components

### MinimalistRagIntake

A lightweight system for processing screen recording frames, extracting metadata, and chunking text for RAG (Retrieval Augmented Generation) applications.

**Key Features**:
- Efficient text chunking for optimal retrieval
- Webhook integration for n8n workflows
- Semantic and token-based chunking options
- Hierarchical data structure optimized for RAG systems

[Go to MinimalistRagIntake →](MinimalistRagIntake/)

### LightweightImageServer

A high-performance, lightweight image server for hosting local images with HTTP URLs, perfect for integration with multimodal AI models.

**Key Features**:
- Blazing-fast image loading with parallel processing
- RESTful API for directory management
- Auto-unload timeout for efficient resource management
- Batch processing and real-time progress tracking

[Go to LightweightImageServer →](LightweightImageServer/)

## Upcoming Integration

A key upcoming feature is the integration between MinimalistRagIntake and LightweightImageServer, which will:

1. Process frames for text content and metadata
2. Automatically host the corresponding images via HTTP
3. Combine both text chunks and image URLs in a single webhook delivery
4. Provide a complete data package for downstream processing

This integration will enable more powerful multimodal AI applications by providing both text content and visual data from screen recordings in a unified, structured format.

## Getting Started

Each component has its own setup and configuration instructions. Please refer to the respective README files for detailed information:

- [MinimalistRagIntake Setup](MinimalistRagIntake/README.md#getting-started)
- [LightweightImageServer Setup](LightweightImageServer/README.md#quick-start)

## n8n Integration

Both components are designed to work seamlessly with n8n workflows:

1. n8n triggers the processing of frame data
2. Processed data (text chunks and image URLs) is sent back to n8n via webhooks
3. n8n can then generate embeddings, store data, and trigger further automations

## License

MIT

# Database Advanced Tokenizer

A comprehensive system for processing, analyzing, and storing OCR data from screen recordings with advanced sensitive information detection and LLM processing.

## OCR and Airtable Integration

This project now includes advanced OCR capabilities and Airtable integration:

### OCR Processing Features
- **Sequential Processing**: Process frames in numerical order within each folder
- **Sensitive Content Detection**: Automatically flag frames containing sensitive information
- **Frame-by-Frame Processing**: Complete OCR and LLM analysis for each frame
- **Skip Mechanism**: Avoid reprocessing frames that already have OCR data
- **Multiple Run Scripts**:
  - `run_sequential_ocr.sh`: Process one frame at a time, one folder at a time
  - `run_ocr_batch.sh`: Process frames in batches with parallelization options
  - `run_folder_reset.sh`: Reset flagged fields for specific folders or all folders
  - `simple_process_frames.js`: Process existing OCR data for flagging sensitive content

### Batch Processing Improvements (v1.3.0)
- **Folder-Based Processing**: Target specific folders or process entire collections
- **Parallel Processing**: Option to process multiple frames simultaneously
- **Rate Limiting Protection**: Intelligent delays to prevent Airtable API rate limits
- **Selective Flag Updates**: Option to preserve sensitive flags while updating others
- **Detailed Logging**: Track progress with timestamped console output

### Parallel Processing Architecture (v1.3.1)
- **Multi-Worker Support**: Process different segments of folders simultaneously
- **Alphabetical Segmentation**: Divide folders alphabetically for parallel processing
- **Bidirectional Processing**: Option to process folders in forward or reverse alphabetical order
- **Path Isolation**: Each worker uses isolated temporary directories
- **Robust Error Handling**: Fallback mechanisms for API failures and parsing errors
- **New Scripts**:
  - `process_all_frames_simple.sh`: Reliable single-worker processing (fallback solution)
  - `run_parallel_segments.sh`: Manages multiple workers processing different folder segments
  - `run_segment_worker.sh`: Processes a segment of folders with a dedicated worker

### Technical Lessons Learned
- **Path Management**: Consistent absolute paths prevent cross-script conflicts
- **Process Isolation**: Workers need dedicated directories to prevent race conditions
- **Error Recovery**: Robust parsing with regex fallbacks when JSON parsing fails
- **Logging Strategy**: Detailed, timestamped logs are critical for debugging distributed processes
- **Simplicity First**: Build reliable single-process solutions before scaling to parallel processing

### Airtable Integration
- Records are updated only after successful OCR and LLM processing
- Respects Airtable's 10-record batch update limit
- Stores OCR text and sensitive content flags
- Provides detailed logging of all processing steps
- Supports controlled updates to avoid false data
- **Field Mapping**:
  - `OCRData`: Cleaned and structured text extracted from frame images
  - `Flagged`: Indicates whether sensitive content was detected (Yes/No with sensitivity percentage)
  - `SensitivityConcerns`: Detailed explanation of detected sensitive information and why it's flagged
- Environment variables control field names (`AIRTABLE_OCR_DATA_FIELD`, `AIRTABLE_FLAGGED_FIELD`, `AIRTABLE_SENSITIVITY_CONCERNS_FIELD`)

### Getting Started with OCR

To process frames sequentially (recommended):
```bash
./run_sequential_ocr.sh
```

To process frames in a specific folder:
```bash
./run_sequential_ocr.sh --folder=/path/to/folder
```

To process frames in batches:
```bash
./run_ocr_batch.sh
```

To process all frames with a simple, reliable approach:
```bash
./process_all_frames_simple.sh
```

To process frames with multiple workers in parallel:
```bash
./run_parallel_segments.sh
```

To reset flagged fields for all folders:
```bash
./run_folder_reset.sh
```

To reset flagged fields for a specific folder:
```bash
./run_folder_reset.sh -f "folder_name"
```

To process existing OCR data for flagging:
```bash
./run_simple.sh
```

## Project Overview

This project provides tools for:

1. **Migration**: Transferring data from source tables to a normalized schema structure
2. **Verification**: Checking database structure and data integrity
3. **Sensitive Information Detection**: Identifying and redacting sensitive data like API keys, passwords, and payment information
4. **LLM Processing**: Analyzing OCR data to generate descriptions and summaries while respecting sensitive data

## Database Schema

The system uses three main schemas:

### Content Schema
- `frames`: Stores information about individual frames from screen recordings
  - Primary key: `frame_id`
  - Contains: timestamps, frame numbers, image URLs, and file metadata

### Metadata Schema
- `frame_details_full`: Stores full frame details including OCR text and LLM-generated descriptions
  - Primary key: `frame_id` (references `content.frames.frame_id`)
  - Contains: descriptions, summaries, OCR data, and technical details
  - **OCR Integration Fields**:
    - `ocr_data`: Stores cleaned OCR text extracted from frames
    - `flagged`: Boolean indicating whether sensitive content was detected
    - `sensitivity_concerns`: Detailed explanation of sensitivity issues detected
- `frame_details_chunks`: Stores chunks from frames with specific analyses
  - Primary key: `frame_id` (references `content.frames.frame_id`)
  - Has `chunk_id` to link with embeddings
  - **OCR Integration Fields**:
    - `ocr_data`: Stores cleaned OCR text from specific chunks
    - `flagged`: Boolean indicating whether this chunk contains sensitive content
    - `sensitivity_concerns`: Detailed explanation of sensitivity issues in this chunk
- `process_frames_chunks`: Tracks processing status of chunks
  - Contains references to `frame_id` and `chunk_id`
  - Logs processing status, timestamps, and metadata

### Embeddings Schema
- `multimodal_embeddings`: Source table with original embeddings
- `multimodal_embeddings_chunks`: Stores embeddings for chunks with reference to `chunk_id`
  - Primary key: `embedding_id`
  - Contains vector embeddings and reference data

## Key Scripts

### Data Migration
- `migrate_embedding_tables.py`: Migrates data from source tables to normalized schema structure
  - Creates entries in `content.frames` table
  - Populates metadata tables with frame and chunk data
  - Creates relationships between tables

### Data Verification
- `verify_embedding_tables.py`: Validates database structure and reference consistency
- `verify_production_data.py`: Checks actual data in tables, relationships, and counts
- `check_processed_frames.py`: Examines LLM-processed data and sensitive information detection

### Sensitive Information Detection
- `sensitive_info_detector.py`: Detects and redacts sensitive information in OCR data
  - Identifies API keys, passwords, environment variables, and payment card numbers
  - Provides risk assessments and sanitized text for LLM processing
  - Uses regex patterns and validation algorithms to reduce false positives

### LLM Processing
- `llm_ocr_processor.py`: Processes OCR data with LLM to generate descriptions and summaries
  - Detects sensitive information before LLM processing
  - Sanitizes text to protect sensitive data
  - Updates database with LLM-generated content and technical metadata

## Workflow

1. **Data Migration**:
   ```bash
   python migrate_embedding_tables.py
   ```
   Migrates data from source tables to the normalized schema structure, creating entries in `content.frames` and populating metadata tables.

2. **Verification**:
   ```bash
   python verify_embedding_tables.py
   python verify_production_data.py
   ```
   Validates database structure, reference consistency, and data integrity.

3. **LLM Processing**:
   ```bash
   python llm_ocr_processor.py --type both --limit 10
   ```
   Processes frames and chunks with LLM to generate descriptions and summaries, while detecting and redacting sensitive information.

4. **Check Results**:
   ```bash
   python check_processed_frames.py
   ```
   Examines LLM-processed data and sensitive information detection results.

## Sensitive Information Detection

The system detects multiple types of sensitive information:

1. **API Keys**: Long alphanumeric strings that might represent credentials
2. **Passwords**: Password fields in config or .env files
3. **Environment Variables**: Configuration with sensitive values
4. **Payment Card Numbers**: Credit/debit card numbers (validated with Luhn algorithm)

When sensitive information is detected:
- The content is redacted before sending to LLM
- Risk levels are assigned (low, medium, high) based on sensitivity
- The LLM is instructed to avoid referencing or repeating sensitive data
- Metadata records the detection for security auditing

## Future Enhancements

Possible enhancements for the system:

1. **Real-time Processing**: Enable streaming processing of frames as they're captured
2. **Enhanced Security Measures**: Add encryption for sensitive metadata
3. **User Interface**: Create a dashboard for monitoring sensitive information detection
4. **Custom LLM Prompts**: Develop domain-specific prompts for specialized analysis
5. **Expanded Detection**: Add more patterns for sensitive information detection

## Requirements

- Python 3.8+
- PostgreSQL database (Supabase)
- Environment variables set in `.env` file (database credentials)
- Required Python packages:
  - asyncpg
  - python-dotenv
  - requests

## Setup

1. Clone the repository
2. Create a `.env` file with database credentials:
   ```
   SUPABASE_DB_HOST=your-db-host
   SUPABASE_DB_PORT=5432
   SUPABASE_DB_NAME=postgres
   SUPABASE_DB_USER=your-username
   SUPABASE_DB_PASSWORD=your-password
   LLM_API_ENDPOINT=your-llm-api-endpoint  # Optional, uses mock responses if not set
   LLM_API_KEY=your-llm-api-key            # Optional, uses mock responses if not set
   ```
3. Install required packages:
   ```bash
   pip install asyncpg python-dotenv requests
   ```

# RAG Image Database Processor

A system for processing and embedding images along with their metadata for retrieval augmented generation (RAG) applications.

## Overview

This project processes video frames (images) extracted from screen recordings, analyzing them with computer vision and embedding the results into vector databases for retrieval. The system supports both local storage and PostgreSQL vector database storage.

## Features

- Process single frames or entire directories of images
- Extract text and visual information from frames using computer vision
- Generate text embeddings suitable for vector database storage
- Store results locally or in PostgreSQL (with pgvector extension)
- Support for key rotation to manage API rate limits
- Webhook integration for triggering downstream processes
- Duplicate frame detection to prevent reprocessing
- Database structure verification tools

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/jaywalked78/RagImageDatabaseProcessor.git
   cd RagImageDatabaseProcessor
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys and configuration:
   ```
   # API Keys
   VOYAGE_API_KEY=your_voyage_api_key
   OPENAI_API_KEY=your_openai_api_key
   
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   
   # Webhook Configuration
   WEBHOOK_URL=your_webhook_url
   ```

## Usage

### Basic Frame Processing

Process a single frame:
```
python main.py --input path/to/frame.jpg
```

Process all frames in a directory:
```
python main.py --input path/to/directory --pattern "*.jpg"
```

### Batch Processing

To process all frames in a base directory and all subdirectories:
```
./scripts/process_all_frames.sh
```

Options:
```
--limit N            : Process only N frames per directory (default: 0 for all)
--chunk-size N       : Size of text chunks (default: 500)
--chunk-overlap N    : Overlap between chunks (default: 50)
--max-chunks N       : Maximum chunks per frame (default: 10)
--storage-dir DIR    : Directory to store results (default: all_frame_embeddings)
--dry-run            : Print what would be processed without actually processing
--force              : Force reprocessing of already processed frames
--help               : Display this help message
```

### Advanced Options

Process frames sequentially rather than in batch:
```
python main.py --input path/to/directory --pattern "*.jpg" --sequential
```

Store results only locally (no database or webhook):
```
python main.py --input path/to/directory --pattern "*.jpg" --local-only
```

Specify a custom storage directory:
```
python main.py --input path/to/directory --pattern "*.jpg" --local-storage-dir "my_embeddings"
```

### PostgreSQL Integration

To use PostgreSQL for vector storage, ensure you've configured your .env file with database credentials and run without the `--local-only` flag:

```
python main.py --input path/to/directory --pattern "*.jpg"
```

### Data Verification Tools

The project includes several utilities to verify data integrity:

#### Check Database Structure

This script verifies that data is being correctly stored in the PostgreSQL database:

```
./scripts/check_database.py
```

Options:
```
--frame PATH         : Check if a specific frame exists in the database
--output FILE        : Save database structure report to JSON file
```

#### Check for Duplicate Processing

This script verifies that frames aren't being processed multiple times:

```
./scripts/check_duplicates.py --storage-dir all_frame_embeddings --check-db
```

Options:
```
--storage-dir DIR    : Directory containing processed frames
--csv-file FILE      : Custom CSV log file to check
--detailed           : Show detailed information for each duplicate
--check-db           : Check database for duplicates
--output FILE        : Save results to JSON file
```

## OCR Processing and Airtable Integration

This section covers the frame OCR processing pipeline and Airtable integration capabilities of the DatabaseAdvancedTokenizer system.

## Processing Frames with OCR

The system provides tools to process frames with OCR, structure the extracted text data using Google's Gemini API, save the data to CSV files, and update Airtable with the processed information.

### Setup

1. **Environment Configuration**

   Copy the `.env.example` file to `.env` and fill in your configuration:

   ```bash
   cp .env.example .env
   # Edit .env with your credentials and preferences
   ```

   The following environment variables are essential for OCR processing and Airtable integration:

   ```
   # API Keys
   GOOGLE_API_KEY=your_google_api_key
   
   # Gemini API Key Rotation (for high-volume processing)
   GEMINI_API_KEY_1=your_gemini_api_key_1
   GEMINI_API_KEY_2=your_gemini_api_key_2
   GEMINI_API_KEY_3=your_gemini_api_key_3
   GEMINI_API_KEY_4=your_gemini_api_key_4
   GEMINI_API_KEY_5=your_gemini_api_key_5
   GEMINI_USE_KEY_ROTATION=true
   GEMINI_RATE_LIMIT=60
   GEMINI_COOLDOWN_PERIOD=60
   
   # Airtable Configuration
   AIRTABLE_API_KEY=your_airtable_api_key
   AIRTABLE_BASE_ID=your_airtable_base_id
   AIRTABLE_TABLE_NAME=your_table_name
   
   # Airtable Field Mappings
   OCR_DATA_FIELD=OCRData
   FLAGGED_FIELD=Flagged
   SYNC_TIMESTAMP_FIELD=LastSynced
   
   # Storage Configuration
   STORAGE_DIR=all_frame_embeddings
   ```

2. **OCR Data Directory**

   Make sure you have a directory containing OCR text files. The default is `ocr_results`.

### Processing Pipeline

The system provides multiple scripts for different processing needs:

#### 1. Complete Frame Processing Pipeline

This script processes frames through the entire pipeline:
1. Reads OCR text from files
2. Processes text using Google's Gemini API
3. Extracts structured data
4. Creates text chunks for search
5. Saves data to CSV files
6. Updates Airtable (if configured)

```bash
./scripts/process_and_update_airtable.sh [OPTIONS]
```

**Options:**
- `--storage-dir DIR`: Set storage directory (default: all_frame_embeddings)
- `--ocr-dir DIR`: Directory containing OCR data files
- `--frame-id ID`: Process a specific frame ID
- `--dry-run`: Run without updating Airtable or writing files
- `--use-gemini`: Use Google Gemini API for enhanced text analysis
- `--batch-size N`: Process N frames at a time (default: 10)
- `--max-workers N`: Use N concurrent workers (default: 4)
- `--flagged-only`: Only process frames with flagged content
- `--verbose`: Show detailed logging
- `--airtable-key KEY`: Set Airtable API key (overrides .env)
- `--base-id BASE_ID`: Set Airtable base ID (overrides .env)
- `--table-name TABLE`: Set Airtable table name (overrides .env)

#### 2. OCR Data Processing

Process OCR files and structure the data:

```bash
python scripts/ocr_data_processor.py --input-dir ocr_results --csv-file all_frame_embeddings/payloads/csv/processed_frames.csv --use-gemini
```

#### 3. Airtable Updates

Update Airtable with processed OCR data:

```bash
./scripts/update_airtable.sh --storage-dir all_frame_embeddings --use-gemini
```

### Output Files

The processing pipeline generates several output files:

1. **CSV Files** (in `STORAGE_DIR/payloads/csv/`):
   - `processed_frames.csv`: Contains processed frame data
   - `frame_chunks.csv`: Contains chunked text data
   - `ocr_structured_data.csv`: Contains structured OCR data

2. **JSON Files** (in `STORAGE_DIR/payloads/json/`):
   - `{frame_id}_structured.json`: Structured OCR data for each frame

3. **Text Chunks** (in `STORAGE_DIR/payloads/chunks/{frame_id}/`):
   - `chunk_{index}.txt`: Text chunks for each frame
   - `chunk_info.json`: Metadata about chunks

4. **Log Files** (in `STORAGE_DIR/logs/`):
   - `pipeline_{timestamp}.log`: Regular processing logs
   - `master_logs/master_log_{timestamp}.jsonl`: Detailed JSONL logs of processing steps

### Features

- **Gemini API Key Rotation**: Automatically rotates between multiple API keys to handle high-volume processing.
- **Sensitive Information Flagging**: Identifies frames containing API keys, credentials, or other sensitive information.
- **CSV Data Storage**: Stores processed data in CSV format for local database-like access.
- **Comprehensive Logging**: Detailed logging of all processing steps for debugging and analysis.
- **Airtable Integration**: Updates Airtable with processed OCR data.
- **Rate Limiting**: Respects API rate limits to avoid throttling.

### Airtable Schema

The system is designed to work with an Airtable base that has the following fields:

- `FrameID`: Unique identifier for each frame
- `OCRData`: JSON field to store structured OCR data
- `Flagged`: Checkbox to indicate frames with sensitive information
- `LastSynced`: Date/time field to track when the record was last updated

See `docs/airtable_schema.md` for more details on the Airtable schema.

## Project Structure

- `main.py`: Entry point for the application
- `src/`: Source code modules
  - `api/`: API integration components
  - `connectors/`: Database and external service connectors
  - `db/`: Database interaction modules
  - `embeddings/`: Embedding generation components
  - `models/`: Data models
  - `processors/`: Frame and metadata processors
  - `utils/`: Utility functions
- `scripts/`: Utility scripts
  - `process_all_frames.sh`: Recursively process frames with duplicate detection
  - `check_database.py`: Verify database structure and contents
  - `check_duplicates.py`: Detect duplicated frame processing
- `tests/`: Test files
- `payloads/`: Directory for storing payloads in JSON and CSV formats

## Development

### Running Tests

```
pytest tests/
```

### Adding New Features

1. Create a new branch for your feature
2. Implement your changes
3. Add tests
4. Submit a pull request

## License

This project is proprietary and not licensed for public use without explicit permission.

## Contact

For questions or support, contact the repository owner.

# API Key Detection and Airtable Integration

This project now includes enhanced functionality for detecting API keys and other sensitive information in OCR text and updating Airtable with the results.

## Features

- **Enhanced API Key Detection**: Automatically detect various API key patterns in OCR text, including:
  - Google API keys (starting with 'AIza')
  - AWS keys (starting with 'AKIA')
  - Stripe keys (starting with 'sk_test_' or 'pk_test_')
  - Generic API keys and tokens

- **Sensitive Content Flagging**: Automatically flag content containing:
  - API keys and credentials
  - Google Sheets with sensitive information
  - Contact information and other sensitive data

- **Airtable Integration**: Update Airtable records with:
  - Flagged status for sensitive content
  - Structured OCR data including topics, URLs, and tables
  - Detailed explanations of detected sensitive information

- **LLM-Enhanced Analysis**: Use Google's Gemini API to:
  - Categorize text content into topics and content types
  - Extract structured information from OCR text
  - Identify sensitive information with detailed explanations

## Setup

1. Copy the environment template:
   ```bash
   cp .env.airtable.example .env.airtable
   ```

2. Edit `.env.airtable` with your credentials:
   ```
   AIRTABLE_API_KEY="your_api_key"
   AIRTABLE_BASE_ID="your_base_id"
   AIRTABLE_TABLE_NAME="your_table_name"
   GEMINI_API_KEY="your_gemini_api_key"  # Optional, for enhanced analysis
   ```

3. Install dependencies:
   ```bash
   pip install pyairtable google-generativeai
   ```

## Usage

### Process OCR and Update Airtable in One Step

Use the all-in-one script:

```bash
./scripts/process_and_update_airtable.sh --use-gemini --ocr-dir ocr_results
```

Options:
- `--use-gemini`: Enable Gemini API for enhanced text analysis
- `--flagged-only`: Only update Airtable records for flagged frames
- `--dry-run`: Show what would be updated without making changes
- `--skip-ocr-processing`: Skip OCR processing and only update Airtable

### Step-by-Step Processing

1. Process OCR data:
   ```bash
   python scripts/ocr_data_processor.py --input-dir ocr_results --csv-file processed_frames.csv --use-gemini
   ```

2. Update Airtable:
   ```bash
   python scripts/csv_to_airtable.py --csv-file processed_frames.csv --ocr-dir ocr_results --base-id YOUR_BASE_ID --table-name YOUR_TABLE --api-key YOUR_API_KEY
   ```

## Rate Limiting

All Airtable API calls include rate limiting to prevent hitting API quotas:
- Default: 250ms between requests (approximately 4 requests per second)
- Adjustable via the `AIRTABLE_RATE_LIMIT_SLEEP` environment variable

# OCRProcessorAndUpsertToAirtable Subprogram

This subprogram focuses solely on OCR processing and Airtable metadata updates, without embedding generation.

### Features

- Processes frames chronologically from oldest to newest based on folder name
- Divides processing into batches of 10 frames for efficient processing
- Uses Gemini AI to filter OCR results and identify meaningful text
- Detects sensitive content in frames
- Updates Airtable records with OCR data and sensitivity flags
- Logs detailed processing information

### Usage

#### Running the OCR Processor

```bash
# Process all folders
./process_all_folders.sh

# Run directly with Python
python ocr_processor.py --base-dir /path/to/folders --batch-size 10
```

#### Command-line Options

```
--base-dir        Base directory containing screen recording folders
                  Default: Value from FRAME_BASE_DIR env variable or /home/jason/Videos/screenRecordings
--pattern         Glob pattern for image files
                  Default: *.jpg
--limit-folders   Maximum number of folders to process
                  Default: All folders
--batch-size      Number of frames to process in each batch
                  Default: 10
```

### Processing Flow

1. Folders are processed chronologically based on folder name (screen_recording_YYYY_MM_DD_*)
2. For each folder:
   - All matching frames are identified and sorted
   - Frames are divided into batches of 10
   - Each batch is processed through OCR
   - OCR results are filtered through Gemini AI to extract meaningful text
   - Airtable records are updated with filtered OCR data and sensitivity flags
3. Processing results are logged and summarized in JSON reports

### Requirements

- Python 3.8+
- Pillow for image processing
- google.generativeai for Gemini API
- dotenv for environment variables
- Airtable API token configured in .env file
- Gemini API key configured in .env file

### Environment Variables

The following environment variables should be set in your .env file:

```
AIRTABLE_PERSONAL_ACCESS_TOKEN=your_airtable_token
AIRTABLE_BASE_ID=your_airtable_base_id
AIRTABLE_TABLE_NAME=tblFrameAnalysis
GEMINI_API_KEY=your_gemini_api_key
FRAME_BASE_DIR=/path/to/screen/recordings
```

### Project Structure

```
.
├── ocr_processor.py           # Main OCR processing script
├── process_all_folders.sh     # Shell script to process all folders
├── src/
│   ├── connectors/
│   │   └── airtable.py        # Airtable connection utilities
│   └── processors/
│       └── frame_processor.py # Frame OCR processing utilities
├── logs/
│   └── ocr/                   # OCR processing logs
└── output/
    └── reports/               # Processing reports and results
```
