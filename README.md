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

The system now includes OCR (Optical Character Recognition) capabilities to extract text from frames, along with advanced data processing and Airtable integration.

### OCR Features

- **Text Extraction**: Uses Tesseract OCR to extract text content from frames
- **Content Categorization**: Parses and categorizes extracted text into structured data
- **Sensitive Content Detection**: Identifies and flags frames containing potential API keys, credentials, or sensitive information
- **Enhanced Analysis**: Optional integration with Google's Gemini API for more advanced content understanding

### Airtable Integration

The system can automatically update Airtable with processed OCR data:

1. Each frame's extracted text is categorized and stored in the `OCRData` column
2. Sensitive content (like Google Sheets with API keys) is flagged in the `Flagged` column
3. Additional metadata like word count, character count, and content types are also recorded

### Setup

1. Install required dependencies:
   ```bash
   pip install pytesseract pillow pyairtable google-generativeai
   ```

2. Install Tesseract OCR:
   ```bash
   sudo apt-get install -y tesseract-ocr
   ```

3. Configure Airtable integration:
   - Copy `.env.airtable.example` to `.env.airtable`
   - Add your Airtable credentials (Base ID, Table Name, API Key)
   - Optionally add Google Gemini API key for enhanced text analysis

### Usage

Process frames with OCR and update Airtable:

```bash
./scripts/process_all_frames.sh --storage-dir all_frame_embeddings --enable-ocr
```

Advanced processing with Gemini API:

```bash
source scripts/load_env.sh  # Load credentials from .env.airtable
./scripts/process_all_frames.sh --storage-dir all_frame_embeddings --enable-ocr
```

Process OCR data separately (without frame processing):

```bash
python scripts/ocr_data_processor.py --input-dir "ocr_results" --update-airtable --base-id "YOUR_BASE_ID" --table-name "YOUR_TABLE" --api-key "YOUR_API_KEY" --use-gemini --gemini-api-key "YOUR_GEMINI_KEY"
```

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
