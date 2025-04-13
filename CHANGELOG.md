# Changelog

All notable changes to the Database Advanced Tokenizer will be documented in this file.

## [1.5.0] - 2025-04-13

### Added
- New `@TimeStampGenerator` module for timestamp generation across the system
- Integrated dynamic date and time generation for changelog updates
- Enhanced webhook payload system for both text chunks and image URLs

### Improved
- Extended timeout settings for image server to prevent connection issues
- Better ngrok integration for webhook handling
- Dynamic variable passing to scripts for improved flexibility

### Technical Notes
- Timestamp format standardized as "YYYY-MM-DD HH:MM:SS"
- Modular design of timestamp generator allows for easy integration with other components

## [1.4.0] - 2025-04-08

### Fixed: Sequential OCR Processing with Reverse Order

#### Issues Resolved
- Fixed dependency errors in the OCR processing pipeline
- Ensured proper execution of the reverse-order processing script

#### Implementation Details
- Environment Setup:
  - Created dedicated Python virtual environment (SecondaryVenv) to isolate dependencies
  - Activated with source SecondaryVenv/bin/activate
- Dependency Installation:
  - Installed Google Generative AI package: pip install google-generativeai
  - Installed Python dotenv package: pip install python-dotenv
  - Installed other required dependencies: Pillow, pytesseract, requests
- Script Configuration:
  - Ensured sequential_ocr_processor_Reverse.js references the correct Python script (process_frames_by_path_Reverse.py)
  - Verified API key configuration in environment variables
- Processing Workflow:
  - The system now processes folders in reverse chronological order (Z→A)
  - Each frame is processed sequentially with proper OCR and LLM analysis
  - Frame data is saved to output/ocr_results directory as JSON
  
This implementation maintains the same functionality as the original processing workflow but processes records in reverse order, providing more recent data first.

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