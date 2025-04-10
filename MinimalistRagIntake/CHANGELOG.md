# Changelog

All notable changes to the MinimalistRagIntake project will be documented in this file.

## [1.0.0] - 2025-04-10

### Added
- FastAPI REST API for frame data intake
- Semantic chunking for optimal text splitting with configurable size and overlap
- Webhook integration for test and production environments
- Environment variable configuration via .env file
- JSON file processing with structured output
- Token-based chunking option for more accurate text splitting
- Frame metadata extraction and organization
- Structured output format optimized for RAG systems
- Support for processing individual files and entire folders
- Comprehensive setup scripts for easy deployment
- Background processing of frame batches

### Features
- Configurable chunk size and overlap settings
- Test and production webhook endpoints
- Folder-based organization of frame data
- Unique ID generation for frames and chunks
- Structured metadata extraction
- Error tracking and statistics
- Support for processing individual files or entire folders
- Progress tracking and detailed logging

### Scripts
- `setup_chunker.sh`: Comprehensive environment setup
- `quick_setup.sh`: Simplified setup script
- `run.sh`: Start the API service
- `stop.sh`: Gracefully stop the running service
- `run_processor.sh`: Process folders or specific files
- `start-chunker-background.sh`: Run the chunker in background mode 