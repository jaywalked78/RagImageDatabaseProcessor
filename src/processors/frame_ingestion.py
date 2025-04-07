"""
Frame ingestion module for handling the complete ingestion pipeline.

This module orchestrates:
1. Finding and loading frame data
2. Extracting and structuring metadata
3. Creating semantic chunks
4. Generating embeddings for both whole frames and chunks
5. Storing in PostgreSQL
"""
import os
import sys
import asyncio
import logging
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
import glob

import dotenv
from PIL import Image

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import custom modules
from src.utils.chunking import create_structured_chunks, create_semantic_chunks
from src.embeddings.chunk_embedder import ChunkEmbedder
from src.database.postgres_vector_store import PostgresVectorStore
from src.api.webhook import WebhookSender

class FrameIngestionPipeline:
    """
    Pipeline for ingesting frames, extracting metadata, generating embeddings, and storing in database.
    
    Implements a hybrid approach with both whole-frame and chunk-level embeddings.
    """
    
    def __init__(self, 
                base_dir: Optional[str] = None,
                voyage_api_key: Optional[str] = None,
                embedding_model: str = "voyage-large-2",
                use_semantic_chunking: bool = True,
                use_postgres: bool = True,
                use_webhook: bool = False,
                hybrid_mode: bool = True):
        """
        Initialize the frame ingestion pipeline.
        
        Args:
            base_dir: Base directory for frames (default: from env var FRAME_BASE_DIR)
            voyage_api_key: API key for Voyage embeddings (default: from env var VOYAGE_API_KEY)
            embedding_model: Model name for embeddings (default: voyage-large-2)
            use_semantic_chunking: Whether to use semantic chunking (default: True)
            use_postgres: Whether to store results in PostgreSQL (default: True)
            use_webhook: Whether to send results via webhook (default: False)
            hybrid_mode: Whether to use hybrid mode with both frame and chunk embeddings (default: True)
        """
        # Initialize base directory
        self.base_dir = base_dir or os.getenv("FRAME_BASE_DIR")
        if not self.base_dir:
            logger.warning("Frame base directory not specified. Using current directory.")
            self.base_dir = os.getcwd()
        
        # Initialize API keys
        self.voyage_api_key = voyage_api_key or os.getenv("VOYAGE_API_KEY")
        if not self.voyage_api_key:
            raise ValueError("Voyage API key is required")
        
        # Configuration
        self.embedding_model = embedding_model
        self.use_semantic_chunking = use_semantic_chunking
        self.use_postgres = use_postgres
        self.use_webhook = use_webhook
        self.hybrid_mode = hybrid_mode
        
        # Initialize components
        self.embedder = ChunkEmbedder(api_key=self.voyage_api_key, model=embedding_model)
        
        # Initialize storage backends
        self.pg_store = None
        if self.use_postgres:
            try:
                self.pg_store = PostgresVectorStore()
            except Exception as e:
                logger.error(f"Failed to initialize PostgreSQL: {e}")
                self.use_postgres = False
        
        # Initialize webhook sender
        self.webhook_sender = None
        if self.use_webhook:
            try:
                self.webhook_sender = WebhookSender()
            except Exception as e:
                logger.error(f"Failed to initialize webhook sender: {e}")
                self.use_webhook = False
        
        logger.info(f"Initialized FrameIngestionPipeline with model: {embedding_model}")
        logger.info(f"Using semantic chunking: {use_semantic_chunking}")
        logger.info(f"Using hybrid mode: {hybrid_mode}")
        logger.info(f"Using PostgreSQL: {use_postgres}")
        logger.info(f"Using Webhook: {use_webhook}")
    
    async def process_frame(self, 
                          frame_path: str,
                          metadata: Optional[Dict[str, Any]] = None,
                          airtable_record_id: Optional[str] = None,
                          google_drive_url: Optional[str] = None,
                          chunk_size: int = 500,
                          chunk_overlap: int = 50,
                          max_chunks: Optional[int] = None,
                          semantic_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Process a single frame through the complete ingestion pipeline.
        
        Args:
            frame_path: Path to the frame image file
            metadata: Optional metadata for the frame (will be extracted if not provided)
            airtable_record_id: Optional Airtable record ID
            google_drive_url: Optional Google Drive URL for the frame
            chunk_size: Size of text chunks for embedding
            chunk_overlap: Overlap between chunks
            max_chunks: Maximum number of chunks to process
            semantic_threshold: Threshold for semantic chunking
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        result = {
            "frame_path": frame_path,
            "success": False,
            "chunks_processed": 0,
            "embeddings_created": 0,
            "errors": []
        }
        
        try:
            # Check if file exists
            if not os.path.exists(frame_path):
                raise FileNotFoundError(f"Frame file not found: {frame_path}")
            
            # Extract frame name and folder
            frame_name = os.path.basename(frame_path)
            folder_path = os.path.dirname(frame_path)
            folder_name = os.path.basename(folder_path)
            
            logger.info(f"Processing frame: {frame_name} from {folder_name}")
            
            # Load image
            image = Image.open(frame_path)
            result["image_size"] = f"{image.width}x{image.height}"
            
            # Get metadata if not provided
            if not metadata:
                metadata = self._extract_metadata(frame_path, frame_name, folder_path)
            
            if not metadata:
                metadata = {"frame_name": frame_name, "folder_name": folder_name}
                logger.warning(f"No metadata found for {frame_name}, using basic metadata")
            
            # Add frame path and source info to metadata
            metadata["frame_path"] = frame_path
            metadata["source_frame_path"] = frame_path
            if airtable_record_id:
                metadata["source_airtable_id"] = airtable_record_id
            if google_drive_url:
                metadata["google_drive_url"] = google_drive_url
                
            # Generate structured metadata text representation 
            metadata_text = self._create_text_representation(metadata)
            
            # Generate chunks
            chunks = None
            if self.use_semantic_chunking:
                # Semantic chunking uses embeddings to cluster similar content
                chunks = await create_semantic_chunks(
                    metadata_text, 
                    embedder=self.embedder,
                    metadata=metadata,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    max_chunks=max_chunks,
                    similarity_threshold=semantic_threshold
                )
            else:
                # Regular chunking based on character count
                chunks = create_structured_chunks(
                    metadata_text, 
                    metadata=metadata,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    max_chunks=max_chunks
                )
            
            result["total_chunks"] = len(chunks)
            logger.info(f"Generated {len(chunks)} chunks from metadata")
            
            # Generate whole-frame embedding
            whole_frame_embedding = await self.embedder.embed_text(metadata_text)
            logger.info(f"Generated whole-frame embedding with dimension {len(whole_frame_embedding)}")
            
            # Generate embeddings for each chunk
            for chunk in chunks:
                chunk_text = chunk["text"]
                
                # Skip empty chunks
                if not chunk_text.strip():
                    continue
                
                # Generate embedding
                embedding = await self.embedder.embed_text(chunk_text)
                
                # Store embedding in chunk
                chunk["embedding"] = embedding
            
            result["embeddings_created"] = len(chunks) + 1  # Chunks + whole frame
            logger.info(f"Created {result['embeddings_created']} embeddings (1 frame + {len(chunks)} chunks)")
            
            # Store in PostgreSQL using the hybrid approach
            if self.use_postgres and self.pg_store:
                await self.pg_store.connect()  # Ensure connected
                
                if self.hybrid_mode:
                    # Use the combined process_frame_with_chunks method
                    pg_result = await self.pg_store.process_frame_with_chunks(
                        frame_name=frame_name,
                        folder_path=folder_path,
                        folder_name=folder_name,
                        chunks=chunks,
                        frame_embedding=whole_frame_embedding,
                        model_name=self.embedding_model,
                        frame_timestamp=metadata.get("timestamp") or metadata.get("creation_time"),
                        google_drive_url=google_drive_url,
                        airtable_record_id=airtable_record_id,
                        metadata=metadata
                    )
                    
                    if pg_result:
                        logger.info(f"Successfully stored frame {frame_name} with {len(chunks)} chunks in PostgreSQL")
                    else:
                        logger.error(f"Failed to store frame {frame_name} with chunks in PostgreSQL")
                        result["errors"].append("PostgreSQL storage failed")
                else:
                    # Store frame and embeddings separately for backward compatibility
                    frame_id = await self.pg_store.store_frame(
                        frame_name=frame_name,
                        folder_path=folder_path,
                        folder_name=folder_name,
                        frame_timestamp=metadata.get("timestamp") or metadata.get("creation_time"),
                        google_drive_url=google_drive_url,
                        airtable_record_id=airtable_record_id,
                        metadata=metadata
                    )
                    
                    if frame_id:
                        # Store whole-frame embedding
                        frame_emb_success = await self.pg_store.store_frame_embedding(
                            frame_id=frame_id,
                            embedding=whole_frame_embedding,
                            model_name=self.embedding_model
                        )
                        
                        if frame_emb_success:
                            logger.info(f"Stored whole-frame embedding for {frame_name}")
                        else:
                            logger.error(f"Failed to store whole-frame embedding for {frame_name}")
                            result["errors"].append("Failed to store whole-frame embedding")
                        
                        # Store chunks and their embeddings
                        stored_chunks = 0
                        for chunk in chunks:
                            chunk_id = await self.pg_store.store_chunk(
                                frame_id=frame_id,
                                chunk_sequence_id=chunk['sequence_id'],
                                chunk_text=chunk['text']
                            )
                            
                            if chunk_id:
                                # Store chunk embedding
                                chunk_emb_success = await self.pg_store.store_chunk_embedding(
                                    chunk_id=chunk_id,
                                    embedding=chunk['embedding'],
                                    model_name=self.embedding_model
                                )
                                
                                if chunk_emb_success:
                                    stored_chunks += 1
                        
                        logger.info(f"Stored {stored_chunks}/{len(chunks)} chunk embeddings for {frame_name}")
                    else:
                        logger.error(f"Failed to store frame {frame_name} in PostgreSQL")
                        result["errors"].append("Failed to store frame in PostgreSQL")
            
            # Send to webhook
            if self.use_webhook and self.webhook_sender:
                webhook_sent = await self.webhook_sender.send_frame_data(
                    frame_name=frame_name,
                    folder_path=folder_path,
                    folder_name=folder_name,
                    metadata=metadata,
                    google_drive_url=google_drive_url,
                    airtable_record_id=airtable_record_id
                )
                
                if webhook_sent:
                    logger.info(f"Sent frame data to webhook")
                else:
                    logger.warning(f"Failed to send frame data to webhook")
                    result["errors"].append("Failed to send webhook")
            
            result["success"] = True
            result["processing_time"] = time.time() - start_time
            
        except Exception as e:
            logger.error(f"Error processing frame {frame_path}: {e}", exc_info=True)
            result["errors"].append(str(e))
            result["processing_time"] = time.time() - start_time
        
        return result
    
    def _extract_metadata(self, frame_path: str, frame_name: str, folder_path: str) -> Dict[str, Any]:
        """
        Extract metadata for a frame from filename, path, or attached metadata.
        
        Args:
            frame_path: Path to the frame file
            frame_name: Name of the frame file
            folder_path: Path to the folder containing the frame
            
        Returns:
            Dictionary of metadata
        """
        # Extract basic metadata
        metadata = {
            "frame_name": frame_name,
            "folder_name": os.path.basename(folder_path),
            "folder_path": folder_path,
            "creation_time": self._get_file_creation_time(frame_path)
        }
        
        # Try to extract more metadata from filename
        try:
            # Extract timestamp from filename if present
            # Example: frame_20220315_120000.jpg -> 2022-03-15 12:00:00
            if "_202" in frame_name:
                parts = frame_name.split("_")
                for part in parts:
                    if part.startswith("202") and len(part) >= 8:  # Year starts with 202x
                        date_part = part[:8]  # Extract YYYYMMDD
                        time_part = part[8:14] if len(part) >= 14 else "000000"  # Extract HHMMSS or default
                        
                        try:
                            # Format into ISO timestamp
                            timestamp = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                            if time_part:
                                timestamp += f" {time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
                                
                            metadata["timestamp"] = timestamp
                        except:
                            pass
        except Exception as e:
            logger.warning(f"Error extracting metadata from filename: {e}")
        
        # Try to extract keywords from folder name
        try:
            # Split folder name by underscores, dashes, or spaces
            folder_terms = []
            folder_name = os.path.basename(folder_path)
            for term in folder_name.replace("_", " ").replace("-", " ").split():
                # Skip numbers and very short terms
                if not term.isdigit() and len(term) > 2:
                    folder_terms.append(term.lower())
            
            if folder_terms:
                metadata["folder_keywords"] = folder_terms
        except Exception as e:
            logger.warning(f"Error extracting keywords from folder name: {e}")
        
        return metadata
    
    def _get_file_creation_time(self, file_path: str) -> str:
        """Get creation time of a file as ISO string."""
        try:
            stat = os.stat(file_path)
            # Try creation time first, fall back to modification time
            timestamp = stat.st_ctime if hasattr(stat, 'st_ctime') else stat.st_mtime
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        except Exception as e:
            logger.warning(f"Error getting file creation time: {e}")
            return ""
    
    def _create_text_representation(self, metadata: Dict[str, Any]) -> str:
        """
        Create a text representation from metadata for embedding.
        
        Args:
            metadata: Dictionary of metadata
            
        Returns:
            Formatted text representation
        """
        text_parts = []
        
        # Add frame name and path info
        if "frame_name" in metadata:
            text_parts.append(f"Frame: {metadata['frame_name']}")
        
        if "folder_name" in metadata:
            text_parts.append(f"Folder: {metadata['folder_name']}")
        
        # Add timestamp if available
        if "timestamp" in metadata:
            text_parts.append(f"Timestamp: {metadata['timestamp']}")
        elif "creation_time" in metadata:
            text_parts.append(f"Creation Time: {metadata['creation_time']}")
        
        # Add keywords if available
        if "folder_keywords" in metadata:
            text_parts.append(f"Keywords: {', '.join(metadata['folder_keywords'])}")
        
        # Add other metadata keys but skip technical/internal fields
        skip_keys = ["frame_name", "folder_name", "folder_path", "timestamp", "creation_time", 
                     "folder_keywords", "frame_path", "source_frame_path", "source_airtable_id", 
                     "google_drive_url"]
        
        for key, value in metadata.items():
            if key in skip_keys:
                continue
                
            # Format the value based on type
            if isinstance(value, dict):
                formatted_value = json.dumps(value, indent=2)
            elif isinstance(value, list):
                if all(isinstance(item, str) for item in value):
                    formatted_value = ", ".join(value)
                else:
                    formatted_value = json.dumps(value)
            else:
                formatted_value = str(value)
                
            text_parts.append(f"{key.replace('_', ' ').title()}: {formatted_value}")
        
        return "\n".join(text_parts)
    
    async def process_directory(self, 
                               directory: str,
                               pattern: str = "*.jpg",
                               limit: Optional[int] = None,
                               sequential: bool = False,
                               **kwargs) -> Dict[str, Any]:
        """
        Process all frames in a directory matching a pattern.
        
        Args:
            directory: Directory path to process
            pattern: Glob pattern for matching files
            limit: Maximum number of files to process
            sequential: Whether to process files sequentially
            **kwargs: Additional arguments to pass to process_frame
            
        Returns:
            Dictionary with processing results
        """
        # Find matching files
        file_pattern = os.path.join(directory, pattern)
        files = sorted(glob.glob(file_pattern))
        
        if not files:
            logger.warning(f"No files found matching pattern {file_pattern}")
            return {"success": False, "error": "No files found"}
        
        logger.info(f"Found {len(files)} files matching pattern '{pattern}' in {directory}")
        
        # Apply limit if specified
        if limit and len(files) > limit:
            logger.info(f"Limiting to {limit} files (out of {len(files)})")
            files = files[:limit]
        
        results = {
            "total_files": len(files),
            "processed_files": 0,
            "successful_files": 0,
            "failed_files": 0,
            "total_chunks": 0,
            "total_embeddings": 0
        }
        
        if sequential:
            # Process files sequentially
            for file_path in files:
                try:
                    result = await self.process_frame(file_path, **kwargs)
                    
                    results["processed_files"] += 1
                    if result.get("success", False):
                        results["successful_files"] += 1
                        results["total_chunks"] += result.get("total_chunks", 0)
                        results["total_embeddings"] += result.get("embeddings_created", 0)
                    else:
                        results["failed_files"] += 1
                        
                    logger.info(f"Processed {results['processed_files']}/{results['total_files']} files")
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    results["failed_files"] += 1
                    results["processed_files"] += 1
        else:
            # Process files in parallel
            tasks = []
            for file_path in files:
                task = self.process_frame(file_path, **kwargs)
                tasks.append(task)
                
            # Wait for all tasks to complete
            frame_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in frame_results:
                results["processed_files"] += 1
                
                if isinstance(result, Exception):
                    logger.error(f"Error in parallel processing: {result}")
                    results["failed_files"] += 1
                else:
                    if result.get("success", False):
                        results["successful_files"] += 1
                        results["total_chunks"] += result.get("total_chunks", 0)
                        results["total_embeddings"] += result.get("embeddings_created", 0)
                    else:
                        results["failed_files"] += 1
        
        logger.info(f"Processing complete: {results['successful_files']} successful, "
                  f"{results['failed_files']} failed out of {results['total_files']} files")
        logger.info(f"Total chunks processed: {results['total_chunks']}, "
                  f"total embeddings created: {results['total_embeddings']}")
        
        return results
    
    def close(self):
        """Close connections to backends."""
        if self.pg_store:
            self.pg_store.close()
        if hasattr(self.embedder, 'close') and callable(self.embedder.close):
            asyncio.create_task(self.embedder.close())

async def main():
    """Main entry point for running the ingestion pipeline directly."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Frame Ingestion Pipeline")
    
    # Input options
    input_group = parser.add_argument_group("Input Options")
    input_group.add_argument("--input", required=True, help="Input file or directory path")
    input_group.add_argument("--pattern", default="*.jpg", help="Glob pattern for image files (default: *.jpg)")
    input_group.add_argument("--limit", type=int, help="Maximum number of files to process")
    
    # Chunking options
    chunking_group = parser.add_argument_group("Chunking Options")
    chunking_group.add_argument("--chunk-size", type=int, default=500, help="Size of text chunks (default: 500)")
    chunking_group.add_argument("--chunk-overlap", type=int, default=50, help="Overlap between chunks (default: 50)")
    chunking_group.add_argument("--max-chunks", type=int, help="Maximum number of chunks per frame")
    chunking_group.add_argument("--no-semantic", action="store_true", help="Disable semantic chunking")
    
    # Storage options
    storage_group = parser.add_argument_group("Storage Options")
    storage_group.add_argument("--no-postgres", action="store_true", help="Disable PostgreSQL storage")
    storage_group.add_argument("--webhook", action="store_true", help="Enable webhook notifications")
    storage_group.add_argument("--no-hybrid", action="store_true", help="Disable hybrid mode (frame + chunks)")
    
    # Processing options
    process_group = parser.add_argument_group("Processing Options")
    process_group.add_argument("--sequential", action="store_true", help="Process files sequentially (default: parallel)")
    
    args = parser.parse_args()
    
    # Validate input path
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input path does not exist: {input_path}")
        sys.exit(1)
    
    # Initialize the pipeline
    pipeline = FrameIngestionPipeline(
        use_semantic_chunking=not args.no_semantic,
        use_postgres=not args.no_postgres,
        use_webhook=args.webhook,
        hybrid_mode=not args.no_hybrid
    )
    
    try:
        if input_path.is_dir():
            # Process directory
            results = await pipeline.process_directory(
                directory=str(input_path),
                pattern=args.pattern,
                limit=args.limit,
                sequential=args.sequential,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap,
                max_chunks=args.max_chunks
            )
        else:
            # Process single file
            result = await pipeline.process_frame(
                frame_path=str(input_path),
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap,
                max_chunks=args.max_chunks
            )
            
            if result.get("success", False):
                print(f"Successfully processed {input_path}")
                print(f"Total chunks: {result.get('total_chunks', 0)}")
                print(f"Embeddings created: {result.get('embeddings_created', 0)}")
                print(f"Processing time: {result.get('processing_time', 0):.2f}s")
            else:
                print(f"Failed to process {input_path}")
                print(f"Errors: {result.get('errors', [])}")
                
    finally:
        # Clean up
        pipeline.close()

if __name__ == "__main__":
    asyncio.run(main()) 