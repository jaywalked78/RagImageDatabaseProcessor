# Changelog

## [1.1.0] - 2025-04-07

### Added
- Extended support for the voyage-multimodal-3 embeddings model
- Improved rate limiting and API key rotation mechanisms
- Enhanced local storage options for processed frames

### Fixed
- Additional fixes for ChunkEmbedder initialization parameter handling
- Optimized embedding processing for better performance

## [1.0.0] - 2025-04-07

### Added
- Initial release of RagImageDatabaseProcessor
- Implemented frame processing pipeline with metadata chunking and embedding
- Added support for voyage-multimodal-3 model for text-image embeddings
- Created Airtable integration for metadata retrieval
- Added webhook connectivity for sending embedding data
- Implemented local storage mode for offline processing
- Added CSV logging for tracking processed frames
- Created command-line interface with multiple configuration options
- Added rate limiting and key rotation support for API calls

### Fixed
- Resolved import issues after codebase reorganization
- Fixed ChunkEmbedder initialization with proper parameters
- Updated model name to match .env configuration (voyage-multimodal-3)
- Fixed session handling in embedder class 