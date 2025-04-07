#!/usr/bin/env python3
"""
Module for embedding frame chunks using Voyage AI models.
Handles batching, rate limiting, and API key rotation.
"""

import os
import logging
import asyncio
import json
from typing import List, Dict, Any, Optional, Union
import numpy as np
from PIL import Image
from dotenv import load_dotenv
import voyageai

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
VOYAGE_API_KEY = os.environ.get('VOYAGE_API_KEY')

# Multiple Voyage API keys for rotation
VOYAGE_API_KEYS = [
    os.environ.get('VOYAGE_API_KEY_V1', os.environ.get('VOYAGE_API_KEY')),
    os.environ.get('VOYAGE_API_KEY_V2'),
    os.environ.get('VOYAGE_API_KEY_V3'),
    os.environ.get('VOYAGE_API_KEY_V4'),
    os.environ.get('VOYAGE_API_KEY_V5')
]
# Filter out None values
VOYAGE_API_KEYS = [key for key in VOYAGE_API_KEYS if key]

# Voyage API rate limits
VOYAGE_RPM = 2000  # 2000 requests per minute per key
VOYAGE_WAIT_TIME = 0.03  # 0.03 seconds between requests (60/2000)
VOYAGE_ROTATION_WAIT_TIME = 0.03  # Same wait time when using key rotation

def estimate_tokens_from_chars(text: str) -> int:
    """Quickly estimate token count from character count.
    
    According to Voyage documentation, tokens are roughly 5 characters on average.
    This is a fast preliminary estimate before using the actual tokenizer.
    
    Args:
        text: Text to estimate tokens for
        
    Returns:
        Estimated number of tokens
    """
    return len(text) // 5 + 1  # Add 1 to account for tokenization overhead

class ChunkEmbedder:
    """Class to create embeddings for metadata chunks with frame images."""
    
    def __init__(self, voyage_api_key=None, embedding_model="voyage-multimodal-3", use_key_rotation=True):
        """Initialize with Voyage AI API key and model name."""
        self.primary_api_key = voyage_api_key or VOYAGE_API_KEY
        self.model_name = embedding_model
        self.use_key_rotation = use_key_rotation
        
        # Key rotation setup
        self.api_keys = VOYAGE_API_KEYS if use_key_rotation else [self.primary_api_key]
        self.current_key_index = 0
        self.last_api_calls = {key: 0 for key in self.api_keys}
        self.min_api_interval = VOYAGE_ROTATION_WAIT_TIME if use_key_rotation else VOYAGE_WAIT_TIME
        
        # Initialize VoyageAI client for the first key
        self.voyage_clients = {}
        self._initialize_current_client()
        
        logger.info(f"Initialized ChunkEmbedder with model: {embedding_model}")
        if use_key_rotation:
            logger.info(f"Using API key rotation with {len(self.api_keys)} keys")
            logger.info(f"Effective throughput: 1 request every {self.min_api_interval}s")
        else:
            logger.info(f"Using single API key with rate limit of {VOYAGE_RPM} requests per minute (1 request every {self.min_api_interval}s)")
    
    def _initialize_current_client(self):
        """Initialize the voyage client for the current API key if not already initialized."""
        current_key = self.api_keys[self.current_key_index]
        if current_key not in self.voyage_clients:
            # Initialize a new client for this key
            client = voyageai.Client()
            client.api_key = current_key
            self.voyage_clients[current_key] = client
    
    def _get_current_client(self):
        """Get the voyage client for the current API key."""
        current_key = self.api_keys[self.current_key_index]
        return self.voyage_clients[current_key]
    
    def _rotate_api_key(self):
        """Rotate to the next available API key."""
        if len(self.api_keys) > 1:
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            self._initialize_current_client()
    
    async def _rate_limit(self):
        """Apply rate limiting based on the last API call time."""
        current_key = self.api_keys[self.current_key_index]
        now = asyncio.get_event_loop().time()
        last_call = self.last_api_calls.get(current_key, 0)
        elapsed = now - last_call
        
        if elapsed < self.min_api_interval:
            await asyncio.sleep(self.min_api_interval - elapsed)
        
        self.last_api_calls[current_key] = asyncio.get_event_loop().time()
    
    async def create_embedding(self, text: str, image: Optional[Image.Image] = None) -> Optional[np.ndarray]:
        """
        Create an embedding for text and optional image.
        
        Args:
            text: Text to embed
            image: Optional PIL image to embed with the text
            
        Returns:
            Embedding vector as numpy array, or None if embedding fails
        """
        # Apply rate limiting
        await self._rate_limit()
        
        try:
            client = self._get_current_client()
            
            # Handle multimodal vs text-only embedding
            if image is not None:
                embedding = client.embed(
                    model=self.model_name,
                    text=text,
                    image=image,
                ).embeddings[0]
            else:
                embedding = client.embed(
                    model=self.model_name,
                    text=text,
                ).embeddings[0]
            
            return np.array(embedding)
        
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            # Rotate API key if there was an error (could be rate limit or auth issue)
            self._rotate_api_key()
            return None
    
    async def embed_chunk(self, chunk: Dict[str, Any], image: Optional[Image.Image] = None) -> Dict[str, Any]:
        """
        Create an embedding for a single chunk.
        
        Args:
            chunk: Dictionary containing chunk text and metadata
            image: Optional PIL image to associate with the chunk
            
        Returns:
            Dictionary with chunk data and embedding
        """
        chunk_text = chunk.get("chunk_text", "")
        chunk_id = chunk.get("chunk_sequence_id", 0)
        text_length = len(chunk_text)
        
        logger.info(f"Embedding chunk {chunk_id}/{chunk.get('total_chunks', '?')} (length: {text_length} chars)")
        
        embedding = await self.create_embedding(chunk_text, image)
        
        if embedding is not None:
            logger.info(f"  ✓ Embedding created: {embedding.shape[0]} dimensions")
            return {
                "chunk": chunk,
                "embedding": embedding,
                "embedding_dim": embedding.shape[0] if hasattr(embedding, "shape") else len(embedding)
            }
        else:
            logger.error(f"  ✗ Failed to create embedding")
            return {
                "chunk": chunk,
                "embedding": None,
                "error": "Failed to create embedding"
            }
    
    async def embed_chunks(self, chunks: List[Dict[str, Any]], image: Optional[Image.Image] = None) -> List[Dict[str, Any]]:
        """
        Create embeddings for multiple chunks.
        
        Args:
            chunks: List of chunk dictionaries
            image: Optional PIL image to associate with all chunks
            
        Returns:
            List of dictionaries with chunk data and embeddings
        """
        # Add total_chunks to each chunk for logging
        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            chunk["total_chunks"] = total_chunks
        
        # Process chunks sequentially (could be made parallel if needed)
        embedded_chunks = []
        for chunk in chunks:
            result = await self.embed_chunk(chunk, image)
            if result.get("embedding") is not None:
                embedded_chunks.append(result)
        
        return embedded_chunks
    
    def create_embedding_sync(self, text: str, image: Optional[Image.Image] = None) -> Optional[np.ndarray]:
        """
        Synchronous version of create_embedding.
        
        Args:
            text: Text to embed
            image: Optional PIL image to embed with the text
            
        Returns:
            Embedding vector as numpy array, or None if embedding fails
        """
        try:
            client = self._get_current_client()
            
            # Handle multimodal vs text-only embedding
            if image is not None:
                embedding = client.embed(
                    model=self.model_name,
                    text=text,
                    image=image,
                ).embeddings[0]
            else:
                embedding = client.embed(
                    model=self.model_name,
                    text=text,
                ).embeddings[0]
            
            return np.array(embedding)
        
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            # Can't rotate API key in sync mode effectively
            return None

class EmbeddingStore:
    """Base class for saving and retrieving embeddings."""
    
    async def save_embeddings(self, embedded_chunks: List[Dict[str, Any]], metadata: Dict[str, Any], **kwargs) -> bool:
        """
        Save embeddings to the store.
        
        Args:
            embedded_chunks: List of embedded chunks
            metadata: Additional metadata for the embeddings
            **kwargs: Additional arguments for the store
            
        Returns:
            True if saved successfully, False otherwise
        """
        raise NotImplementedError("Subclasses must implement save_embeddings")
    
    async def get_embeddings(self, ids: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve embeddings from the store.
        
        Args:
            ids: List of embedding IDs to retrieve
            **kwargs: Additional arguments for the store
            
        Returns:
            List of retrieved embeddings
        """
        raise NotImplementedError("Subclasses must implement get_embeddings")

# Simple in-memory embedding store for testing
class MemoryEmbeddingStore(EmbeddingStore):
    """Store embeddings in memory (for testing purposes)."""
    
    def __init__(self):
        """Initialize an empty embedding store."""
        self.embeddings = {}
    
    async def save_embeddings(self, embedded_chunks: List[Dict[str, Any]], metadata: Dict[str, Any], **kwargs) -> bool:
        """
        Save embeddings to memory.
        
        Args:
            embedded_chunks: List of embedded chunks
            metadata: Additional metadata for the embeddings
            **kwargs: Additional arguments for the store
            
        Returns:
            True if saved successfully
        """
        record_id = metadata.get("record_id", str(len(self.embeddings)))
        
        self.embeddings[record_id] = {
            "chunks": embedded_chunks,
            "metadata": metadata,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return True
    
    async def get_embeddings(self, ids: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Retrieve embeddings from memory.
        
        Args:
            ids: List of embedding IDs to retrieve
            **kwargs: Additional arguments for the store
            
        Returns:
            List of retrieved embeddings
        """
        return [self.embeddings.get(id_) for id_ in ids if id_ in self.embeddings] 