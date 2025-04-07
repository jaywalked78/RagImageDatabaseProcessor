# Changelog

All notable changes to this project will be documented in this file.

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