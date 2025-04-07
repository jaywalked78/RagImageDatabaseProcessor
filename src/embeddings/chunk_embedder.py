#!/usr/bin/env python3
"""
Chunk embedder module for generating embeddings using the Voyage API.
"""

import os
import logging
import time
import json
import asyncio
import random
from typing import List, Dict, Any, Optional, Tuple, Union

import numpy as np
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import aiohttp
from PIL import Image
import voyageai

import dotenv

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class ChunkEmbedder:
    """
    Client for generating text embeddings using Voyage API.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "voyage-multimodal-3", use_key_rotation: bool = False):
        """
        Initialize the Voyage embedding client.
        
        Args:
            api_key: Voyage API key (default: from env var VOYAGE_API_KEY)
            model: Model name for embeddings (default: voyage-multimodal-3)
            use_key_rotation: Whether to use API key rotation for rate limiting
        """
        self.api_key = api_key or os.getenv("VOYAGE_API_KEY")
        if not self.api_key:
            raise ValueError("Voyage API key is required")
            
        self.model = model
        self.api_base = "https://api.voyageai.com/v1"
        self.embedding_url = f"{self.api_base}/embeddings"
        
        # Create session for reuse
        self.session = None
        
        # Rate limiting settings
        self.min_api_interval = 0.2  # 5 requests per second max
        self.last_api_calls = {}  # Track last API call time for each key
        self.use_key_rotation = use_key_rotation  # Whether to use key rotation
        
        logger.info(f"Initialized ChunkEmbedder with model {model}")
    
    async def _ensure_session(self):
        """Ensure an aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            })
        return self.session
    
    async def embed_text(self, text: str, retry_count: int = 3) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            retry_count: Number of retries for API calls
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return []
        
        session = await self._ensure_session()
        
        # Payload for embedding API
        payload = {
            "model": self.model,
            "input": text,
        }
        
        error = None
        embedding = []
        
        # Try with retries
        for attempt in range(retry_count):
            try:
                async with session.post(self.embedding_url, json=payload) as response:
                    if response.status == 200:
                        # Parse the response
                        result = await response.json()
                        
                        if "data" in result and len(result["data"]) > 0:
                            # Extract the embedding from the response
                            embedding = result["data"][0]["embedding"]
                            logger.debug(f"Generated embedding with dimension {len(embedding)}")
                            return embedding
                        else:
                            error = f"Unexpected response format: {result}"
                    else:
                        response_text = await response.text()
                        error = f"API error: HTTP {response.status} - {response_text}"
                        
                        # Check if rate limited
                        if response.status == 429:
                            wait_time = min(2 ** attempt, 30)  # Exponential backoff, max 30 seconds
                            logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                            await asyncio.sleep(wait_time)
                        
            except Exception as e:
                error = f"Request error: {str(e)}"
            
            if embedding:
                break
                
            if attempt < retry_count - 1:
                wait_time = min(2 ** attempt, 10)  # Exponential backoff
                logger.warning(f"Retry {attempt+1}/{retry_count} after error: {error}. Waiting {wait_time}s")
                await asyncio.sleep(wait_time)
        
        if not embedding:
            logger.error(f"Failed to generate embedding after {retry_count} attempts: {error}")
            
        return embedding
    
    async def embed_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each API call
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Process in batches
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            # Process batch in parallel
            tasks = [self.embed_text(text) for text in batch]
            batch_embeddings = await asyncio.gather(*tasks)
            
            embeddings.extend(batch_embeddings)
            
            logger.info(f"Processed {len(embeddings)}/{len(texts)} embeddings")
        
        return embeddings
    
    async def close(self):
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Closed embedding client session")
            self.session = None
    
    def __del__(self):
        """Cleanup when object is deleted."""
        if self.session and not self.session.closed:
            logger.warning("Session not properly closed, closing in destructor")
            # Create a new event loop for cleanup if needed
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.session.close())
                else:
                    loop.run_until_complete(self.session.close())
            except Exception:
                pass  # Ignore errors in destructor

    def estimate_tokens_from_chars(self, text: str) -> int:
        """Estimate the number of tokens from character count.
        
        Simple tokenization estimate based on average character-to-token ratio.
        For English text, 1 token is approximately 4-5 characters.
        
        Args:
            text: Text to estimate token count for
            
        Returns:
            int: Estimated token count
        """
        if not text:
            return 0
        
        # Use a conservative estimate (4 characters per token)
        return len(text) // 4 + 1

    def estimate_tokens_from_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Estimate the number of tokens from a list of text chunks.
        
        Args:
            chunks: List of chunk dictionaries with 'chunk_text' key
            
        Returns:
            Estimated total number of tokens
        """
        if not chunks:
            return 0
        
        # Extract text from chunks
        texts = [chunk["chunk_text"] for chunk in chunks]
        
        # Count tokens using Voyage's tokenizer
        return self.count_tokens(texts)
    
    def estimate_tokens_quick(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Quickly estimate tokens from character counts (no API call).
        
        This uses the character-based estimation method (chars ÷ 4)
        described in Voyage documentation for a fast preliminary estimate.
        
        Args:
            chunks: List of chunk dictionaries with 'chunk_text' key
            
        Returns:
            Dictionary with estimation results
        """
        if not chunks:
            return {"total_tokens": 0, "chunk_count": 0, "avg_tokens": 0}
        
        # Get estimated token counts for each chunk based on character length
        token_estimates = [self.estimate_tokens_from_chars(chunk["chunk_text"]) for chunk in chunks]
        total_tokens = sum(token_estimates)
        
        return {
            "total_tokens_estimate": total_tokens,
            "chunk_count": len(chunks),
            "avg_tokens_per_chunk": total_tokens / len(chunks),
            "token_estimates": token_estimates
        }

    def tokenize_text(self, texts: List[str]) -> Optional[List[Any]]:
        """Tokenize a list of texts using the current model's tokenizer.
        
        Args:
            texts: List of text strings to tokenize
            
        Returns:
            List of tokenized encodings or None on error
        """
        client = self._get_current_client()
        if not client:
            logger.error("No valid Voyage API client available")
            return None
            
        try:
            return client.tokenize(texts, model=self.model)
        except Exception as e:
            logger.error(f"Error tokenizing texts: {e}")
            return None
    
    def count_tokens(self, texts: List[str]) -> int:
        """Count the number of tokens in a list of texts.
        
        Args:
            texts: List of text strings to count tokens for
            
        Returns:
            Total number of tokens
        """
        client = self._get_current_client()
        if not client:
            logger.error("No valid Voyage API client available")
            return 0
            
        try:
            return client.count_tokens(texts, model=self.model)
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            return 0
    
    def count_usage(self, inputs: List[List[Union[str, Image.Image]]]) -> Dict[str, int]:
        """Count usage (text tokens, image pixels, total tokens) for multimodal inputs.
        
        Args:
            inputs: List of text and image sequences
            
        Returns:
            Dictionary containing text_tokens, image_pixels, and total_tokens counts
        """
        client = self._get_current_client()
        if not client:
            logger.error("No valid Voyage API client available")
            return {"text_tokens": 0, "image_pixels": 0, "total_tokens": 0}
            
        try:
            return client.count_usage(inputs, model=self.model)
        except Exception as e:
            logger.error(f"Error counting usage: {e}")
            return {"text_tokens": 0, "image_pixels": 0, "total_tokens": 0}
    
    def _get_current_client(self):
        """Get the current VoyageAI client."""
        if not self.api_key:
            logger.error("No API key available. Please set VOYAGE_API_KEY environment variable.")
            return None
            
        return voyageai.Client(api_key=self.api_key)
    
    def _rotate_key(self):
        """Rotate to the next API key in the pool."""
        if not self.api_key:
            return
            
        logger.debug(f"Rotated to API key ...{self.api_key[-4:]}")
    
    async def enforce_rate_limit(self):
        """Enforce rate limiting by waiting if needed."""
        if not self.api_key:
            logger.error("No API key available. Please set VOYAGE_API_KEY environment variable.")
            return
            
        last_call_time = self.last_api_calls.get(self.api_key, 0)
        time_since_last_call = time.time() - last_call_time
        
        if time_since_last_call < self.min_api_interval:
            wait_time = self.min_api_interval - time_since_last_call
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s before next API call")
            await asyncio.sleep(wait_time)
        
        # Update last call time
        self.last_api_calls[self.api_key] = time.time()
    
    async def create_embedding(self, text, image=None):
        """Create embedding for text chunk with optional image."""
        max_retries = 3
        base_delay = 2  # seconds
        last_error = None
        
        # Try each key in rotation if we encounter rate limits
        for attempt in range(max_retries):
            try:
                # Always enforce rate limit before any API call
                await self.enforce_rate_limit()
                
                # Get the client for the current API key
                client = self._get_current_client()
                if not client:
                    raise ValueError("No valid Voyage API client available")
                    
                current_key = self.api_key
                logger.debug(f"Attempting API call with key ...{current_key[-4:]}")
                
                if image is not None:
                    # Multimodal embedding with both text and image
                    # Format input as a list containing text string and PIL image object
                    inputs = [
                        [text, image]
                    ]
                    
                    # Generate multimodal embedding
                    result = client.multimodal_embed(
                        inputs=inputs,
                        model=self.model
                    )
                    
                    embedding_type = "multimodal"
                else:
                    # Text-only embedding
                    result = client.text_embed(
                        model=self.model,
                        texts=[text]
                    )
                    
                    embedding_type = "text-only"
                
                # Extract embedding from the response
                if hasattr(result, 'embeddings') and result.embeddings:
                    embedding = result.embeddings[0]
                    logger.info(f"Successfully created {embedding_type} embedding ({len(embedding)} dimensions)")
                    return embedding
                else:
                    raise ValueError("No embedding returned from VoyageAI API")
                    
            except Exception as e:
                last_error = e
                logger.warning(f"API call failed (attempt {attempt+1}): {str(e)}")
                
                # Check if it's a rate limit issue
                if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                    if self.api_key:
                        # Rotate key and try again with minimal delay
                        self._rotate_key()
                        await asyncio.sleep(0.1)
                    else:
                        # Back off exponentially
                        wait_time = base_delay * (2 ** (attempt % max_retries))
                        logger.info(f"Rate limited. Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                else:
                    # For other errors, wait a bit before retry
                    wait_time = base_delay * (1.5 ** (attempt % max_retries))
                    logger.info(f"Error occurred. Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                    
                    # Rotate key if we have multiple keys
                    if self.api_key:
                        self._rotate_key()
        
        # If we exhaust all retries, raise the last error
        logger.error(f"Failed to create embedding after {max_retries} retries: {str(last_error)}")
        return None
    
    async def embed_chunks(self, chunks, image=None):
        """Create embeddings for multiple chunks with the same optional image."""
        embeddings = []
        
        for i, chunk in enumerate(chunks):
            chunk_text = chunk["chunk_text"]
            logger.info(f"Embedding chunk {i+1}/{len(chunks)} (length: {len(chunk_text)} chars)")
            
            try:
                embedding = await self.create_embedding(chunk_text, image)
                
                if embedding is not None:
                    # Create result with embedded chunk
                    result = {
                        "chunk": chunk,
                        "embedding": embedding,
                        "embedding_dim": len(embedding)
                    }
                    embeddings.append(result)
                    
                    logger.info(f"  ✓ Embedding created: {len(embedding)} dimensions")
                else:
                    logger.error(f"  ✗ Failed to embed chunk {i+1}")
            except Exception as e:
                logger.error(f"  ✗ Failed to embed chunk {i+1}: {str(e)}")
            
            # Note: No need to add delay here as enforce_rate_limit handles timing
        
        return embeddings
    
    def use_key_rotation(self):
        """Enable or disable key rotation."""
        self.use_key_rotation = True
    
    def no_key_rotation(self):
        """Disable key rotation."""
        self.use_key_rotation = False
    
    def min_api_interval(self):
        """Get the minimum API call interval."""
        return self.min_api_interval
    
    def last_api_calls(self):
        """Get the last API call times."""
        return self.last_api_calls
    
    def api_key(self):
        """Get the API key."""
        return self.api_key
    
    def model(self):
        """Get the embedding model."""
        return self.model
    
    def api_base(self):
        """Get the API base URL."""
        return self.api_base
    
    def session(self):
        """Get the requests session."""
        return self.session
    
    def _rotate_key(self):
        """Rotate to the next API key in the pool."""
        if not self.api_key:
            return
            
        logger.debug(f"Rotated to API key ...{self.api_key[-4:]}")
    
    async def enforce_rate_limit(self):
        """Enforce rate limiting by waiting if needed."""
        if not self.api_key:
            logger.error("No API key available. Please set VOYAGE_API_KEY environment variable.")
            return
            
        last_call_time = self.last_api_calls.get(self.api_key, 0)
        time_since_last_call = time.time() - last_call_time
        
        if time_since_last_call < self.min_api_interval:
            wait_time = self.min_api_interval - time_since_last_call
            logger.debug(f"Rate limiting: waiting {wait_time:.2f}s before next API call")
            await asyncio.sleep(wait_time)
        
        # Update last call time
        self.last_api_calls[self.api_key] = time.time()
    
    async def create_embedding(self, text, image=None):
        """Create embedding for text chunk with optional image."""
        max_retries = 3
        base_delay = 2  # seconds
        last_error = None
        
        # Try each key in rotation if we encounter rate limits
        for attempt in range(max_retries):
            try:
                # Always enforce rate limit before any API call
                await self.enforce_rate_limit()
                
                # Get the client for the current API key
                client = self._get_current_client()
                if not client:
                    raise ValueError("No valid Voyage API client available")
                    
                current_key = self.api_key
                logger.debug(f"Attempting API call with key ...{current_key[-4:]}")
                
                if image is not None:
                    # Multimodal embedding with both text and image
                    # Format input as a list containing text string and PIL image object
                    inputs = [
                        [text, image]
                    ]
                    
                    # Generate multimodal embedding
                    result = client.multimodal_embed(
                        inputs=inputs,
                        model=self.model
                    )
                    
                    embedding_type = "multimodal"
                else:
                    # Text-only embedding
                    result = client.text_embed(
                        model=self.model,
                        texts=[text]
                    )
                    
                    embedding_type = "text-only"
                
                # Extract embedding from the response
                if hasattr(result, 'embeddings') and result.embeddings:
                    embedding = result.embeddings[0]
                    logger.info(f"Successfully created {embedding_type} embedding ({len(embedding)} dimensions)")
                    return embedding
                else:
                    raise ValueError("No embedding returned from VoyageAI API")
                    
            except Exception as e:
                last_error = e
                logger.warning(f"API call failed (attempt {attempt+1}): {str(e)}")
                
                # Check if it's a rate limit issue
                if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                    if self.api_key:
                        # Rotate key and try again with minimal delay
                        self._rotate_key()
                        await asyncio.sleep(0.1)
                    else:
                        # Back off exponentially
                        wait_time = base_delay * (2 ** (attempt % max_retries))
                        logger.info(f"Rate limited. Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                else:
                    # For other errors, wait a bit before retry
                    wait_time = base_delay * (1.5 ** (attempt % max_retries))
                    logger.info(f"Error occurred. Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                    
                    # Rotate key if we have multiple keys
                    if self.api_key:
                        self._rotate_key()
        
        # If we exhaust all retries, raise the last error
        logger.error(f"Failed to create embedding after {max_retries} retries: {str(last_error)}")
        return None
    
    async def embed_chunks(self, chunks, image=None):
        """Create embeddings for multiple chunks with the same optional image."""
        embeddings = []
        
        for i, chunk in enumerate(chunks):
            chunk_text = chunk["chunk_text"]
            logger.info(f"Embedding chunk {i+1}/{len(chunks)} (length: {len(chunk_text)} chars)")
            
            try:
                embedding = await self.create_embedding(chunk_text, image)
                
                if embedding is not None:
                    # Create result with embedded chunk
                    result = {
                        "chunk": chunk,
                        "embedding": embedding,
                        "embedding_dim": len(embedding)
                    }
                    embeddings.append(result)
                    
                    logger.info(f"  ✓ Embedding created: {len(embedding)} dimensions")
                else:
                    logger.error(f"  ✗ Failed to embed chunk {i+1}")
            except Exception as e:
                logger.error(f"  ✗ Failed to embed chunk {i+1}: {str(e)}")
            
            # Note: No need to add delay here as enforce_rate_limit handles timing
        
        return embeddings
    
    def tokenize_text(self, texts: List[str]) -> Optional[List[Any]]:
        """Tokenize a list of texts using the current model's tokenizer.
        
        Args:
            texts: List of text strings to tokenize
            
        Returns:
            List of tokenized encodings or None on error
        """
        client = self._get_current_client()
        if not client:
            logger.error("No valid Voyage API client available")
            return None
            
        try:
            return client.tokenize(texts, model=self.model)
        except Exception as e:
            logger.error(f"Error tokenizing texts: {e}")
            return None
    
    def count_tokens(self, texts: List[str]) -> int:
        """Count the number of tokens in a list of texts.
        
        Args:
            texts: List of text strings to count tokens for
            
        Returns:
            Total number of tokens
        """
        client = self._get_current_client()
        if not client:
            logger.error("No valid Voyage API client available")
            return 0
            
        try:
            return client.count_tokens(texts, model=self.model)
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            return 0
    
    def count_usage(self, inputs: List[List[Union[str, Image.Image]]]) -> Dict[str, int]:
        """Count usage (text tokens, image pixels, total tokens) for multimodal inputs.
        
        Args:
            inputs: List of text and image sequences
            
        Returns:
            Dictionary containing text_tokens, image_pixels, and total_tokens counts
        """
        client = self._get_current_client()
        if not client:
            logger.error("No valid Voyage API client available")
            return {"text_tokens": 0, "image_pixels": 0, "total_tokens": 0}
            
        try:
            return client.count_usage(inputs, model=self.model)
        except Exception as e:
            logger.error(f"Error counting usage: {e}")
            return {"text_tokens": 0, "image_pixels": 0, "total_tokens": 0}
    
    def estimate_tokens_from_chars(self, text: str) -> int:
        """Estimate the number of tokens from character count.
        
        Simple tokenization estimate based on average character-to-token ratio.
        For English text, 1 token is approximately 4-5 characters.
        
        Args:
            text: Text to estimate token count for
            
        Returns:
            int: Estimated token count
        """
        if not text:
            return 0
        
        # Use a conservative estimate (4 characters per token)
        return len(text) // 4 + 1
    
    def estimate_tokens_from_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """Estimate the number of tokens from a list of text chunks.
        
        Args:
            chunks: List of chunk dictionaries with 'chunk_text' key
            
        Returns:
            Estimated total number of tokens
        """
        if not chunks:
            return 0
        
        # Extract text from chunks
        texts = [chunk["chunk_text"] for chunk in chunks]
        
        # Count tokens using Voyage's tokenizer
        return self.count_tokens(texts)
    
    def estimate_tokens_quick(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Quickly estimate tokens from character counts (no API call).
        
        This uses the character-based estimation method (chars ÷ 4)
        described in Voyage documentation for a fast preliminary estimate.
        
        Args:
            chunks: List of chunk dictionaries with 'chunk_text' key
            
        Returns:
            Dictionary with estimation results
        """
        if not chunks:
            return {"total_tokens": 0, "chunk_count": 0, "avg_tokens": 0}
        
        # Get estimated token counts for each chunk based on character length
        token_estimates = [self.estimate_tokens_from_chars(chunk["chunk_text"]) for chunk in chunks]
        total_tokens = sum(token_estimates)
        
        return {
            "total_tokens_estimate": total_tokens,
            "chunk_count": len(chunks),
            "avg_tokens_per_chunk": total_tokens / len(chunks),
            "token_estimates": token_estimates
        } 