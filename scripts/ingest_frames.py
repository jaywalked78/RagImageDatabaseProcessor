#!/usr/bin/env python3
"""
Script to demonstrate and run the frame ingestion pipeline.

Usage:
    python ingest_frames.py --input /path/to/frames [options]
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ingest_frames")

# Import the ingestion pipeline
from src.processors.frame_ingestion import FrameIngestionPipeline
from src.database.schema_setup import main as setup_schema

async def main():
    """Main entry point for running the ingestion pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Frame Ingestion Pipeline Demo")
    
    # Setup action
    parser.add_argument('--setup-schema', action='store_true', help='Set up PostgreSQL database schema before ingestion')
    
    # Input options
    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument("--input", help="Input file or directory path")
    input_group.add_argument("--pattern", default="*.jpg", help="Glob pattern for image files (default: *.jpg)")
    input_group.add_argument("--limit", type=int, help="Maximum number of files to process")
    
    # Chunking options
    chunking_group = parser.add_argument_group("Chunking Options")
    chunking_group.add_argument("--chunk-size", type=int, default=500, help="Size of text chunks (default: 500)")
    chunking_group.add_argument("--chunk-overlap", type=int, default=50, help="Overlap between chunks (default: 50)")
    chunking_group.add_argument("--max-chunks", type=int, help="Maximum number of chunks per frame")
    chunking_group.add_argument("--no-semantic", action="store_true", help="Disable semantic chunking")
    chunking_group.add_argument("--similarity-threshold", type=float, default=0.7, 
                               help="Semantic similarity threshold (default: 0.7)")
    
    # Storage options
    storage_group = parser.add_argument_group("Storage Options")
    storage_group.add_argument("--no-postgres", action="store_true", help="Disable PostgreSQL storage")
    storage_group.add_argument("--webhook", action="store_true", help="Enable webhook notifications")
    storage_group.add_argument("--no-hybrid", action="store_true", 
                             help="Disable hybrid mode (frame + chunks) (default: use hybrid)")
    
    # Processing options
    process_group = parser.add_argument_group("Processing Options")
    process_group.add_argument("--sequential", action="store_true", help="Process files sequentially (default: parallel)")
    process_group.add_argument("--api-key", help="Voyage API key (default: from env var VOYAGE_API_KEY)")
    process_group.add_argument("--model", default="voyage-large-2", 
                              help="Embedding model to use (default: voyage-large-2)")
    
    args = parser.parse_args()
    
    # Run schema setup if requested
    if args.setup_schema:
        logger.info("Setting up PostgreSQL database schema...")
        # Run with sys.argv but skip our script name and --setup-schema arg
        setup_args = [arg for arg in sys.argv[1:] if arg != '--setup-schema']
        sys.argv = [sys.argv[0]] + setup_args
        setup_schema()
        logger.info("Schema setup completed")
    
    # Validate input path if provided
    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            logger.error(f"Input path does not exist: {input_path}")
            sys.exit(1)
        
        logger.info(f"Starting frame ingestion for: {input_path}")
        
        # Initialize the pipeline
        pipeline = FrameIngestionPipeline(
            voyage_api_key=args.api_key,
            embedding_model=args.model,
            use_semantic_chunking=not args.no_semantic,
            use_postgres=not args.no_postgres,
            use_webhook=args.webhook,
            hybrid_mode=not args.no_hybrid
        )
        
        try:
            # Process directory or single file
            if input_path.is_dir():
                logger.info(f"Processing directory: {input_path}")
                logger.info(f"File pattern: {args.pattern}")
                if args.limit:
                    logger.info(f"Processing up to {args.limit} files")
                
                results = await pipeline.process_directory(
                    directory=str(input_path),
                    pattern=args.pattern,
                    limit=args.limit,
                    sequential=args.sequential,
                    chunk_size=args.chunk_size,
                    chunk_overlap=args.chunk_overlap,
                    max_chunks=args.max_chunks,
                    semantic_threshold=args.similarity_threshold
                )
                
                # Print summary
                logger.info("=== Processing Summary ===")
                logger.info(f"Total files found: {results.get('total_files', 0)}")
                logger.info(f"Successfully processed: {results.get('successful_files', 0)}")
                logger.info(f"Failed to process: {results.get('failed_files', 0)}")
                logger.info(f"Total chunks created: {results.get('total_chunks', 0)}")
                logger.info(f"Total embeddings created: {results.get('total_embeddings', 0)}")
                
            else:
                # Process single file
                logger.info(f"Processing single file: {input_path}")
                
                result = await pipeline.process_frame(
                    frame_path=str(input_path),
                    chunk_size=args.chunk_size,
                    chunk_overlap=args.chunk_overlap,
                    max_chunks=args.max_chunks,
                    semantic_threshold=args.similarity_threshold
                )
                
                # Print result
                logger.info("=== Processing Result ===")
                if result.get("success", False):
                    logger.info(f"Successfully processed {input_path}")
                    logger.info(f"Image size: {result.get('image_size', 'unknown')}")
                    logger.info(f"Total chunks: {result.get('total_chunks', 0)}")
                    logger.info(f"Embeddings created: {result.get('embeddings_created', 0)}")
                    logger.info(f"Processing time: {result.get('processing_time', 0):.2f}s")
                    
                    if result.get("errors"):
                        logger.warning(f"Errors: {result.get('errors', [])}")
                else:
                    logger.error(f"Failed to process {input_path}")
                    logger.error(f"Errors: {result.get('errors', [])}")
                
        except Exception as e:
            logger.error(f"Error in ingestion process: {e}", exc_info=True)
            sys.exit(1)
            
        finally:
            # Clean up
            pipeline.close()
            logger.info("Frame ingestion completed")
    elif not args.setup_schema:
        # If neither --input nor --setup-schema is provided
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main()) 