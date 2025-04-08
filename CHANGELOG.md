# Changelog

All notable changes to the Database Advanced Tokenizer will be documented in this file.

## [1.3.1] - 2025-08-08

### Added
- New `process_all_frames_simple.sh` script for efficient, reliable frame processing
- Multiple worker support with improved error handling and recovery
- Parallel processing capability with alphabetical folder segmentation

### Improved
- Hardcoded absolute paths to prevent environment variable conflicts
- Enhanced error handling in Airtable API response parsing
- Better logging with detailed error messages and progress tracking
- Fallback mechanisms for JSON parsing failures using regex

### Fixed
- Path handling issues between scripts that caused inconsistent behavior
- Temp directory conflicts that led to file not found errors
- Process isolation to prevent worker conflicts
- Issues with environment variable inheritance between scripts

### Technical Notes
- Path management remains a critical issue - hardcoded paths are more reliable than environment variables
- Worker processes need isolated environments with their own temp directories
- Cross-script communication works best with absolute paths for file references
- Fallback mechanisms are essential for API-dependent operations

## [1.3.0] - 2025-08-05

### Added
- Folder-based processing with ability to target specific folders
- New `run_ocr_batch.sh` script for processing frames in batches
- New `simple_process_frames.js` script for quick flagging of existing OCR data
- Selective flag updating with option to preserve sensitive flags
- Parallelization options for batch processing

### Improved
- Enhanced `run_folder_reset.sh` with command-line options
- Rate limiting protection with intelligent delays between API calls
- More detailed logging with timestamped console output
- Better error handling and recovery mechanisms

### Fixed
- Issues with Airtable API rate limiting
- Batch processing to respect Airtable's 10-record limit

## [1.2.0] - 2025-07-15

### Added
- Initial OCR integration with Airtable
- Basic folder processing capabilities
- Sensitive information detection
- Frame-by-frame sequential processing

### Other
- First production-ready release with complete OCR pipeline 