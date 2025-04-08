#!/usr/bin/env python3
"""
Frame processor for creating embeddings from frames and storing them in various destinations.
"""

import os
import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
import requests
from PIL import Image
from dotenv import load_dotenv
import pytesseract

import numpy as np

# Import utilities
from src.utils.metadata_utils import process_metadata_text, find_image_url
from src.utils.chunking import create_structured_chunks

# Import embeddings
from src.embeddings.chunk_embedder import ChunkEmbedder

# Import database
from src.database.postgres_vector_store import PostgresVectorStore

# Import API
from src.api.webhook import WebhookSender

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("processor")
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class FrameProcessor:
    """
    Processor for handling frame processing, metadata extraction, and embedding generation.
    
    This class is responsible for:
    1. Loading frame data (image, metadata)
    2. Processing the frame into chunks
    3. Generating embeddings for chunks
    4. Storing results in PostgreSQL or sending via webhook
    """
    
    def __init__(self, 
                voyage_api_key: Optional[str] = None,
                embedding_model: str = "voyage-large-2",
                use_postgres: bool = True,
                use_webhook: bool = False,
                tesseract_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the frame processor.
        
        Args:
            voyage_api_key: API key for Voyage embeddings (defaults to env var VOYAGE_API_KEY)
            embedding_model: Model name for embeddings (default: voyage-large-2)
            use_postgres: Whether to store results in PostgreSQL
            use_webhook: Whether to send results via webhook
            tesseract_config: Optional configuration for Tesseract OCR
        """
        # Initialize API keys
        self.voyage_api_key = voyage_api_key or os.getenv("VOYAGE_API_KEY")
        if not self.voyage_api_key:
            raise ValueError("Voyage API key is required")
        
        # Initialize embedder
        self.embedder = ChunkEmbedder(api_key=self.voyage_api_key, model=embedding_model)
        
        # Configuration
        self.use_postgres = use_postgres
        self.use_webhook = use_webhook
        
        # Initialize storage backends
        self.pg_store = None
        if self.use_postgres:
            try:
                self.pg_store = PostgresVectorStore()
            except Exception as e:
                logger.error(f"Failed to initialize PostgreSQL: {e}")
                self.use_postgres = False
        
        # Initialize Tesseract OCR
        self.tesseract_config = tesseract_config or {
            'lang': 'eng',
            'config': '--psm 6'  # Assume a single uniform block of text
        }
        
        # Check if tesseract is installed and available
        try:
            pytesseract.get_tesseract_version()
            logger.info(f"Tesseract OCR initialized (version: {pytesseract.get_tesseract_version()})")
        except Exception as e:
            logger.error(f"Tesseract OCR is not available: {e}")
            logger.error("Please install Tesseract OCR and ensure it's in your PATH")
        
        logger.info(f"Initialized FrameProcessor with model: {embedding_model}")
        logger.info(f"Using PostgreSQL: {use_postgres}")
        logger.info(f"Using Webhook: {use_webhook}")

    async def process_frame(self, 
                          frame_path: str,
                          chunk_size: int = 500,
                          chunk_overlap: int = 50,
                          max_chunks: Optional[int] = None,
                          metadata: Optional[Dict[str, Any]] = None,
                          airtable_record_id: Optional[str] = None,
                          google_drive_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a single frame and generate embeddings.
        
        Args:
            frame_path: Path to the frame image file
            chunk_size: Size of text chunks for embedding
            chunk_overlap: Overlap between chunks
            max_chunks: Maximum number of chunks to process
            metadata: Optional metadata for the frame
            airtable_record_id: Optional Airtable record ID
            google_drive_url: Optional Google Drive URL for the frame
            
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
                metadata = self._get_metadata(frame_path, frame_name, folder_path)
            
            if not metadata:
                metadata = {"frame_name": frame_name, "folder_name": folder_name}
                logger.warning(f"No metadata found for {frame_name}, using basic metadata")
            
            # Add frame path and Google Drive URL to metadata
            metadata["frame_path"] = frame_path
            if google_drive_url:
                metadata["google_drive_url"] = google_drive_url
            if airtable_record_id:
                metadata["airtable_record_id"] = airtable_record_id
                
            # Create text from metadata
            metadata_text = self._metadata_to_text(metadata)
            
            # Generate chunks
            chunks = create_structured_chunks(
                metadata_text, 
                metadata=metadata,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                max_chunks=max_chunks
            )
            
            result["total_chunks"] = len(chunks)
            logger.info(f"Generated {len(chunks)} chunks from metadata")
            
            # Generate embeddings for each chunk
            embeddings = []
            for chunk in chunks:
                chunk_text = chunk["text"]
                
                # Skip empty chunks
                if not chunk_text.strip():
                    continue
                
                # Generate embedding
                embedding = await self.embedder.embed_text(chunk_text)
                
                # Store chunk with embedding
                embeddings.append({
                    "text": chunk_text,
                    "embedding": embedding,
                    "sequence_id": chunk["sequence_id"],
                    "metadata": chunk["metadata"]
                })
            
            result["embeddings_created"] = len(embeddings)
            logger.info(f"Created {len(embeddings)} embeddings")
            
            # Store embeddings in PostgreSQL
            if self.use_postgres and self.pg_store:
                for emb in embeddings:
                    await self._store_in_postgres(
                        embedding=emb["embedding"],
                        text=emb["text"],
                        frame_path=frame_path,
                        frame_name=frame_name,
                        folder_path=folder_path,
                        folder_name=folder_name,
                        metadata=metadata,
                        google_drive_url=google_drive_url
                    )
            
            # Send to webhook
            if self.use_webhook:
                await self._send_to_webhook(
                    frame_path=frame_path,
                    frame_name=frame_name,
                    folder_path=folder_path,
                    folder_name=folder_name,
                    embeddings=embeddings,
                    metadata=metadata,
                    google_drive_url=google_drive_url
                )
            
            result["success"] = True
            result["processing_time"] = time.time() - start_time
            
        except Exception as e:
            logger.error(f"Error processing frame {frame_path}: {e}", exc_info=True)
            result["errors"].append(str(e))
            result["processing_time"] = time.time() - start_time
        
        return result
    
    def _metadata_to_text(self, metadata: Dict[str, Any]) -> str:
        """Convert metadata dictionary to text format."""
        text_parts = []
        
        for key, value in metadata.items():
            # Skip internal keys
            if key.startswith("_") or key in ["frame_path", "google_drive_url", "airtable_record_id"]:
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
                
            text_parts.append(f"{key}: {formatted_value}")
        
        return "\n".join(text_parts)
    
    def _get_metadata(self, frame_path: str, frame_name: str, folder_path: str) -> Dict[str, Any]:
        """
        Extract metadata for a frame. This is a placeholder - 
        the actual implementation would depend on how metadata is stored.
        """
        # This is where you would implement your metadata retrieval logic
        # For example, looking up metadata from a database or a file
        
        # For now, return a simple placeholder
        return {
            "frame_name": frame_name,
            "folder_name": os.path.basename(folder_path)
        }
    
    async def _store_in_postgres(self, 
                              embedding: List[float],
                              text: str,
                              frame_path: str,
                              frame_name: str,
                              folder_path: str,
                              folder_name: str,
                              metadata: Dict[str, Any],
                              google_drive_url: Optional[str] = None) -> bool:
        """Store embedding in PostgreSQL vector store."""
        if not self.pg_store:
            return False
            
        try:
            # Generate a unique ID for the embedding
            import uuid
            embedding_id = str(uuid.uuid4())
            
            # Store the embedding
            await self.pg_store.store_embedding(
                embedding_id=embedding_id,
                reference_id=frame_name,
                reference_type="frame",
                text_content=text,
                image_url=google_drive_url or frame_path,
                embedding=embedding,
                model_name="voyage-large-2"
            )
            
            # Store the frame data
            await self.pg_store.store_content_frame(
                frame_name=frame_name,
                folder_path=folder_path,
                folder_name=folder_name,
                metadata=metadata,
                google_drive_url=google_drive_url
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to store in PostgreSQL: {e}")
            return False
    
    async def _send_to_webhook(self,
                            frame_path: str,
                            frame_name: str,
                            folder_path: str,
                            folder_name: str,
                            embeddings: List[Dict[str, Any]],
                            metadata: Dict[str, Any],
                            google_drive_url: Optional[str] = None) -> bool:
        """Send embeddings to webhook."""
        webhook_url = os.getenv("WEBHOOK_URL")
        if not webhook_url:
            logger.error("Webhook URL not configured")
            return False
            
        try:
            # Prepare the payload
            payload = {
                "frame_name": frame_name,
                "folder_path": folder_path,
                "folder_name": folder_name,
                "google_drive_url": google_drive_url,
                "metadata": metadata,
                "embeddings": [
                    {
                        "text": emb["text"],
                        "sequence_id": emb["sequence_id"],
                        "embedding_size": len(emb["embedding"])
                    } for emb in embeddings
                ]
            }
            
            # Send the request
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Webhook notification sent successfully for {frame_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
            return False
    
    def close(self):
        """Close any open connections."""
        if self.pg_store:
            self.pg_store.close()

    async def extract_text(self, image: Image.Image) -> str:
        """
        Extract text from an image using OCR.
        
        Args:
            image: PIL Image to process
            
        Returns:
            Extracted text as string
        """
        try:
            # Run Tesseract OCR in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None,
                lambda: pytesseract.image_to_string(
                    image,
                    lang=self.tesseract_config['lang'],
                    config=self.tesseract_config['config']
                )
            )
            
            # Clean the text
            text = text.strip()
            
            logger.info(f"Extracted {len(text)} characters of text")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text with OCR: {e}")
            return ""
    
    async def process_frame_ocr(self, frame_path: str) -> Dict[str, Any]:
        """
        Process a frame to extract OCR text.
        
        Args:
            frame_path: Path to the frame image
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Load the image
            img = Image.open(frame_path)
            logger.info(f"Loaded image: {frame_path} ({img.width}x{img.height})")
            
            # Extract text using OCR
            ocr_text = await self.extract_text(img)
            
            return {
                "frame_path": frame_path,
                "frame_name": os.path.basename(frame_path),
                "folder_name": os.path.basename(os.path.dirname(frame_path)),
                "ocr_text": ocr_text,
                "ocr_text_length": len(ocr_text),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error processing frame {frame_path}: {e}")
            return {
                "frame_path": frame_path,
                "frame_name": os.path.basename(frame_path) if frame_path else "",
                "success": False,
                "error": str(e)
            } 