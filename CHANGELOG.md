# Changelog

All notable changes to this project will be documented in this file.

## [1.3.0] - 2025-04-08

### Added
- Sequential OCR processing to handle frames in numerical order
- Improved Airtable integration with proper OCR data verification
- Skip mechanism to avoid reprocessing frames that already have OCR data
- Frame-by-frame OCR and LLM processing with controlled Airtable updates
- Fixed Airtable batch update to respect 10-record API limit
- Enhanced folder-based processing to complete all frames in a folder before moving on
- Multiple run scripts for different processing scenarios:
  - `run_sequential_ocr.sh` for controlled sequential processing
  - `run_ocr_batch.sh` for batch OCR processing
  - `run_folder_reset.sh` for resetting Flagged fields

### Fixed
- Prevented Airtable from receiving false data when OCR fails
- Fixed batch size limitations to respect Airtable's 10-record update limit
- Improved frame sorting to ensure numerical order processing
- Added proper verification before updating Airtable records
- Enhanced error handling and logging throughout the OCR pipeline

## [1.2.0] - 2024-07-12

### Added
- OCR text extraction using Tesseract OCR for improved frame analysis
- Airtable integration with structured data updating
- Text categorization and sensitive content detection
- Google Gemini API integration for advanced text analysis
- Advanced content categorization into topics, content types, and entities
- Batch processing with rate limiting for Airtable API requests
- New command-line options for OCR and Airtable control
- Helper scripts for standalone OCR data processing and Airtable updates
- Improved documentation for OCR and Airtable setup

### Fixed
- Airtable API rate limiting to prevent quota issues
- Frame timestamp extraction for chronological processing
- Enhanced duplicate detection using content hashing

## [1.1.0] - 2023-11-12

### Added
- Support for voyage-multimodal-3 embedding model
- Improved rate limiting with configurable API intervals
- Key rotation functionality for API key management
- `scripts/process_all_frames.sh` for recursive processing of frame directories
- Detailed README with comprehensive usage instructions
- Example environment file (.env.example) for easier setup

### Fixed
- Import structure in main.py to properly use FrameProcessor class
- Directory creation for JSON payload storage

## [1.0.0] - 2023-11-11

### Added
- Initial release with frame processing capabilities
- Embedding generation with Voyage AI
- Local storage option for frame data
- PostgreSQL vector database integration
- Directory-based batch processing
- Webhook integration for downstream processing

### Fixed
- Resolved import issues after codebase reorganization
- Fixed ChunkEmbedder initialization with proper parameters
- Updated model name to match .env configuration (voyage-multimodal-3)
- Fixed session handling in embedder class 