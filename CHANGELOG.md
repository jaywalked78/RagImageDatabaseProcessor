# Changelog

All notable changes to the Database Advanced Tokenizer will be documented in this file.

## [1.3.0] - 2023-08-05

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

## [1.2.0] - 2023-07-15

### Added
- Initial OCR integration with Airtable
- Basic folder processing capabilities
- Sensitive information detection
- Frame-by-frame sequential processing

### Other
- First production-ready release with complete OCR pipeline 