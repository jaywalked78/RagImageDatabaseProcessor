# Changelog

## Version 2.0.0 (2024-03-01)

### Major Enhancements
- Added automatic timestamping to output filenames to prevent overwrites
- Added Central Standard Time (CST) timezone support for timestamps
- Improved n8n integration with enhanced script execution
- Refactored directory handling in all scripts for better path resolution
- Added symlink creation to latest output files for easier access

### Script Improvements
- `run_processor_with_image_server.sh`: 
  - Added timestamp-based filename generation
  - Fixed directory handling with proper pushd/popd usage
  - Added comprehensive logging with color-coded output
  - Improved image server startup and detection logic
  - Added error handling for failed image loading
  - Renamed output files to include timestamps
  - Created symlinks to latest output files

### n8n Integration
- Created dedicated n8n workflow documentation
- Added support for dynamic variable passing from n8n
- Improved execution flow for webhook integration
- Added consistent logging for n8n-triggered processes

### Bug Fixes
- Fixed issues with relative vs. absolute paths in scripts
- Fixed file overwriting issues by adding timestamps to filenames
- Resolved image server connection handling issues
- Fixed environment variable inheritance problems

## Version 1.0.0 (2024-02-20)

### Initial Release
- Basic processing pipeline for screen recordings
- Text extraction and chunking
- Image server for hosting frame images
- Initial webhook integration
- Basic n8n compatibility

All notable changes to the MinimalistRagIntake project will be documented in this file.

## [1.1.0] - 2025-04-10

### Added
- Integration with LightweightImageServer for image URL generation
- New `run_processor_with_image_server.sh` script for coordinated processing
- n8n workflow template for combining text chunks and image URLs
- Detailed documentation for n8n integration
- Support for automatically starting the image server if not running
- Parallel processing of text content and image URLs

### Enhanced
- Better path resolution for finding image folders
- Color-coded terminal output for better readability
- Improved error handling for when image server is unavailable
- Clear separation of concerns between text and image processing

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