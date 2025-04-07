#!/usr/bin/env python3
"""
Test script for embedding metadata chunks with Voyage multimodal model.
This combines our metadata chunking with the Voyage embedding capabilities.

The script:
1. Loads a frame image
2. Finds its metadata in Airtable
3. Chunks the metadata
4. Creates embeddings for each chunk with the corresponding frame image.
5. Stores results in Airtable and Supabase vector database
"""

import os
import sys
import json
import hashlib
import logging
import argparse
import asyncio
import psycopg2
import uuid
from datetime import datetime
from PIL import Image
from io import BytesIO
from pathlib import Path
import numpy as np
import voyageai
from dotenv import load_dotenv
from pyairtable import Api
from typing import List, Dict, Union, Tuple, Optional, Any, Sequence
import random
import requests
import re

# Import our custom modules
from metadata_chunker import MetadataChunker
from test_metadata_chunking import AirtableMetadataFinder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("chunk_embedding")

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

# Load environment variables
load_dotenv()
VOYAGE_API_KEY = os.environ.get('VOYAGE_API_KEY')
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = "appewal2KEO5B02KV"
AIRTABLE_TABLE_NAME = "tblFrameAnalysis"

# n8n webhook URLs
N8N_TEST_WEBHOOK_URL = os.environ.get('WEBHOOK_TEST_URL')
N8N_PROD_WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
USE_TEST_WEBHOOK = os.environ.get('USE_TEST_WEBHOOK', 'true').lower() == 'true'

# Multiple Voyage API keys for rotation
VOYAGE_API_KEYS = [
    os.environ.get('VOYAGE_API_KEY_V1', 'pa-P9n1Yo1D98kWvEYUUFtswpai-iaRY7OAuRNeF1FEKCh'),
    os.environ.get('VOYAGE_API_KEY_V2', 'pa-j5BFEffJ2IyixVvrMZzqrqi8mJlzYqvsZ9GocPCtn_V'),
    os.environ.get('VOYAGE_API_KEY_V3', 'pa-UX91iG1Y6F7f7Lc9dPSqOxV_Zi0dZKk6Fidy_YYCPTJ'),
    os.environ.get('VOYAGE_API_KEY_V4', 'pa-oz5IO55q4415k4vetpLL3QqdzERTha1G8PQZuIKaWBp'),
    os.environ.get('VOYAGE_API_KEY_V5', 'pa-4PhLhoHMdIIB8LzNLD6mEOnjPINqccbHwZOe36WHXIa')
]

# Postgres/Supabase configuration
POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASS')
POSTGRES_DB = os.environ.get('POSTGRES_DB')

# Airtable field for storing embeddings
EMBEDDING_VECTORS_FIELD = "EmbeddingVectors"

# Cache settings
CACHE_DIR = os.environ.get('TEMP_DIR', '/tmp/database_tokenizer')
CACHE_FILE = os.path.join(CACHE_DIR, 'frame_processing_cache.json')

# Voyage API rate limits
VOYAGE_RPM = 2000  # 2000 requests per minute per key
VOYAGE_WAIT_TIME = 0.03  # 0.03 seconds between requests (60/2000)
VOYAGE_ROTATION_WAIT_TIME = 0.03  # Same wait time when using key rotation

class ProcessingCache:
    """Class to handle caching of processed frames to avoid reprocessing."""
    
    def __init__(self, cache_file=CACHE_FILE):
        """Initialize the cache with cache file path."""
        self.cache_file = cache_file
        self.cache_data = {}
        self._ensure_cache_dir()
        self._load_cache()
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists."""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
    
    def _load_cache(self):
        """Load the cache data from file if it exists."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache_data = json.load(f)
                logger.info(f"Loaded processing cache with {len(self.cache_data)} entries")
            except Exception as e:
                logger.warning(f"Failed to load cache file, starting with empty cache: {e}")
                self.cache_data = {}
        else:
            logger.info("No existing cache file found, starting with empty cache")
            self.cache_data = {}
    
    def _save_cache(self):
        """Save the cache data to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache_data, f)
            logger.info(f"Cache saved with {len(self.cache_data)} entries")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def get_metadata_hash(self, metadata):
        """Generate a hash from the metadata to detect changes."""
        # Convert metadata to a sorted JSON string for consistent hashing
        metadata_str = json.dumps(metadata, sort_keys=True)
        return hashlib.md5(metadata_str.encode('utf-8')).hexdigest()
    
    def is_processed(self, frame_path, metadata):
        """Check if frame has been processed with this metadata."""
        frame_id = os.path.basename(frame_path)
        metadata_hash = self.get_metadata_hash(metadata)
        
        if frame_id in self.cache_data:
            if self.cache_data[frame_id]['metadata_hash'] == metadata_hash:
                return True
        return False
    
    def mark_processed(self, frame_path, metadata, num_chunks, embedding_dim):
        """Mark a frame as processed with its metadata hash and processing details."""
        frame_id = os.path.basename(frame_path)
        metadata_hash = self.get_metadata_hash(metadata)
        
        self.cache_data[frame_id] = {
            'metadata_hash': metadata_hash,
            'last_processed': int(asyncio.get_event_loop().time()),
            'num_chunks': num_chunks,
            'embedding_dim': embedding_dim
        }
        self._save_cache()

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
            logger.debug(f"Initialized Voyage client for API key ending in ...{current_key[-4:]}")
    
    def _get_current_client(self):
        """Get the voyage client for the current API key."""
        current_key = self.api_keys[self.current_key_index]
        return self.voyage_clients[current_key]
    
    def _rotate_key(self):
        """Rotate to the next API key."""
        if not self.use_key_rotation or len(self.api_keys) <= 1:
            return False
        
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self._initialize_current_client()
        current_key = self.api_keys[self.current_key_index]
        logger.debug(f"Rotated to API key ending in ...{current_key[-4:]}")
        return True
    
    async def enforce_rate_limit(self):
        """Ensure we don't exceed Voyage's rate limits by adding delays between calls."""
        current_time = asyncio.get_event_loop().time()
        
        if not self.use_key_rotation or len(self.api_keys) <= 1:
            # Single key mode - enforce minimal wait time for the current key
            current_key = self.api_keys[self.current_key_index]
            elapsed = current_time - self.last_api_calls.get(current_key, 0)
            
            if elapsed < VOYAGE_WAIT_TIME:
                delay = VOYAGE_WAIT_TIME - elapsed
                # Only log if delay is significant
                if delay > 0.1:
                    logger.info(f"Rate limiting: Waiting {delay:.2f}s before next Voyage API call")
                await asyncio.sleep(delay)
            
            self.last_api_calls[current_key] = current_time
        else:
            # With higher limits, we can simplify key rotation logic
            # Just enforce minimal wait time and rotate keys for redundancy
            current_key = self.api_keys[self.current_key_index]
            elapsed = current_time - self.last_api_calls.get(current_key, 0)
            
            if elapsed < VOYAGE_WAIT_TIME:
                # If we need to wait, check if another key is ready
                ready_key_found = False
                
                for i in range(1, len(self.api_keys)):
                    # Check next keys in rotation
                    next_index = (self.current_key_index + i) % len(self.api_keys)
                    next_key = self.api_keys[next_index]
                    next_elapsed = current_time - self.last_api_calls.get(next_key, 0)
                    
                    if next_elapsed >= VOYAGE_WAIT_TIME:
                        # This key is ready, switch to it
                        self.current_key_index = next_index
                        self._initialize_current_client()
                        ready_key_found = True
                        break
                
                if not ready_key_found:
                    # No keys ready, wait for current key
                    delay = VOYAGE_WAIT_TIME - elapsed
                    # Only log if delay is significant
                    if delay > 0.1:
                        logger.debug(f"Rate limiting: Waiting {delay:.2f}s before next API call")
                    await asyncio.sleep(delay)
            
            # Rotate to next key after use for even distribution
            if random.random() < 0.2:  # 20% chance to rotate after each call for load balancing
                self._rotate_key()
            
            # Update the timestamp for the current key
            current_key = self.api_keys[self.current_key_index]
            self.last_api_calls[current_key] = asyncio.get_event_loop().time()
    
    async def create_embedding(self, text, image):
        """Create embedding for text chunk with image."""
        max_retries = 3
        base_delay = 2  # seconds
        last_error = None
        
        # Try each key in rotation if we encounter rate limits
        for attempt in range(max_retries * (len(self.api_keys) if self.use_key_rotation else 1)):
            try:
                # Always enforce rate limit before any API call
                await self.enforce_rate_limit()
                
                # Use multimodal_embed for interleaved text and image data
                # Format input as a list containing text string and PIL image object
                inputs = [
                    [text, image]
                ]
                
                # Get the client for the current API key
                client = self._get_current_client()
                current_key = self.api_keys[self.current_key_index]
                
                logger.debug(f"Attempting API call with key ...{current_key[-4:]}")
                
                # Generate multimodal embedding
                result = client.multimodal_embed(
                    inputs=inputs,
                    model=self.model_name
                )
                
                # Extract embedding from the response
                if hasattr(result, 'embeddings') and result.embeddings:
                    embedding = result.embeddings[0]
                    return embedding
                else:
                    raise ValueError("No embedding returned from VoyageAI API")
                
            except Exception as e:
                error_str = str(e)
                current_key = self.api_keys[self.current_key_index]
                last_error = e
                
                # Check if it's a rate limit error
                if "rate limit" in error_str.lower():
                    # Mark this key as recently used so it won't be selected again immediately
                    self.last_api_calls[current_key] = asyncio.get_event_loop().time()
                    
                    if self.use_key_rotation and len(self.api_keys) > 1:
                        # Try rotating to another key on the next attempt
                        logger.warning(f"Rate limit hit for key ...{current_key[-4:]}. Will try another key.")
                        # Force a longer wait for this key
                        self.last_api_calls[current_key] = asyncio.get_event_loop().time() + 5.0
                        # No need to sleep here as enforce_rate_limit will handle it
                    else:
                        # With a single key, we need exponential backoff
                        retry_delay = base_delay * (2 ** (attempt % max_retries))
                        logger.warning(f"Rate limit hit. Retrying in {retry_delay} seconds (attempt {(attempt % max_retries)+1}/{max_retries})...")
                        await asyncio.sleep(retry_delay)
                else:
                    # For non-rate-limit errors, don't retry
                    logger.error(f"Error generating embedding with key ...{current_key[-4:]}: {error_str}")
                    raise
        
        # If we've exhausted all retries
        if last_error:
            logger.error(f"Rate limit exceeded on all available keys after {max_retries * len(self.api_keys)} attempts")
            raise last_error
        else:
            raise RuntimeError("Failed to create embedding after all retry attempts")
    
    async def embed_chunks(self, chunks, image):
        """Create embeddings for multiple chunks with the same image."""
        embeddings = []
        
        for i, chunk in enumerate(chunks):
            chunk_text = chunk["chunk_text"]
            logger.info(f"Embedding chunk {i+1}/{len(chunks)} (length: {len(chunk_text)} chars)")
            
            try:
                embedding = await self.create_embedding(chunk_text, image)
                
                # Create result with embedded chunk
                result = {
                    "chunk": chunk,
                    "embedding": embedding,
                    "embedding_dim": len(embedding)
                }
                embeddings.append(result)
                
                logger.info(f"  ✓ Embedding created: {len(embedding)} dimensions")
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
        try:
            return client.tokenize(texts, model=self.model_name)
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
        try:
            return client.count_tokens(texts, model=self.model_name)
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
        try:
            return client.count_usage(inputs, model=self.model_name)
        except Exception as e:
            logger.error(f"Error counting usage: {e}")
            return {"text_tokens": 0, "image_pixels": 0, "total_tokens": 0}
    
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
        
        This uses the character-based estimation method (chars ÷ 5)
        described in Voyage documentation for a fast preliminary estimate.
        
        Args:
            chunks: List of chunk dictionaries with 'chunk_text' key
            
        Returns:
            Dictionary with estimation results
        """
        if not chunks:
            return {"total_tokens": 0, "chunk_count": 0, "avg_tokens": 0}
        
        # Get estimated token counts for each chunk based on character length
        token_estimates = [estimate_tokens_from_chars(chunk["chunk_text"]) for chunk in chunks]
        total_tokens = sum(token_estimates)
        
        return {
            "total_tokens_estimate": total_tokens,
            "chunk_count": len(chunks),
            "avg_tokens_per_chunk": total_tokens / len(chunks),
            "token_estimates": token_estimates
        }
    
    def analyze_chunk_token_distribution(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze token distribution across chunks to identify potential optimization areas.
        
        Args:
            chunks: List of chunk dictionaries with 'chunk_text' key
            
        Returns:
            Dictionary with token distribution statistics
        """
        if not chunks:
            return {"error": "No chunks to analyze"}
        
        # Extract text from chunks
        texts = [chunk["chunk_text"] for chunk in chunks]
        
        # Get individual token counts
        token_counts = []
        try:
            for text in texts:
                count = self.count_tokens([text])
                token_counts.append(count)
        except Exception as e:
            logger.error(f"Error analyzing token distribution: {e}")
            return {"error": str(e)}
        
        # Calculate statistics
        total_tokens = sum(token_counts)
        avg_tokens = float(total_tokens / len(token_counts) if token_counts else 0)
        max_tokens = int(max(token_counts) if token_counts else 0)
        min_tokens = int(min(token_counts) if token_counts else 0)
        std_dev = float(np.std(token_counts) if token_counts else 0)
        
        # Identify chunks that are significantly larger than average
        outliers = [int(i) for i, count in enumerate(token_counts) if count > avg_tokens * 1.5]
        
        # Convert all values to JSON serializable types
        result = {
            "total_tokens": int(total_tokens),
            "chunk_count": len(chunks),
            "avg_tokens_per_chunk": float(avg_tokens),
            "max_tokens": int(max_tokens),
            "min_tokens": int(min_tokens),
            "std_deviation": float(std_dev),
            "token_counts": [int(count) for count in token_counts],
            "outlier_chunks": outliers,
            "optimization_needed": bool(std_dev > (avg_tokens * 0.5))  # Suggests rebalancing if high deviation
        }
        
        return result
    
    def estimate_multimodal_usage(self, chunks: List[Dict[str, Any]], image: Image.Image) -> Dict[str, int]:
        """Estimate usage for chunks and image combined.
        
        Args:
            chunks: List of chunk dictionaries with 'chunk_text' key
            image: Image to process
            
        Returns:
            Dictionary containing text_tokens, image_pixels, and total_tokens counts
        """
        if not chunks:
            return {"text_tokens": 0, "image_pixels": 0, "total_tokens": 0}
            
        # Format inputs for count_usage
        inputs = [[chunk["chunk_text"], image] for chunk in chunks]
        
        return self.count_usage(inputs)

class AirtableEmbeddingStore:
    """Class to handle storing embeddings in Airtable."""
    
    def __init__(self, api_key=None, base_id=None, table_name=None, use_webhook=False):
        """Initialize with Airtable API credentials."""
        self.api_key = api_key or AIRTABLE_TOKEN
        self.base_id = base_id or AIRTABLE_BASE_ID
        self.table_name = table_name or AIRTABLE_TABLE_NAME
        self.last_api_call = 0
        self.min_delay = 0.2  # Minimum delay between API calls in seconds
        
        # For batch mode
        self.batch_mode = False
        self.batch_updates = {}  # Dictionary to store record_id -> embedding_data
        
        # For webhook mode
        self.use_webhook = use_webhook
        
    def enable_batch_mode(self):
        """Enable batch mode to collect updates instead of applying them immediately."""
        self.batch_mode = True
        self.batch_updates = {}
        logger.info("Batch mode enabled for Airtable updates")
        
    def disable_batch_mode(self):
        """Disable batch mode and return to immediate updates."""
        self.batch_mode = False
        logger.info("Batch mode disabled for Airtable updates")
        
    def get_batch_size(self):
        """Return the number of records queued for batch update."""
        return len(self.batch_updates)
        
    async def commit_batch_updates(self, chunk_size=10):
        """Commit all batched updates to Airtable.
        
        Args:
            chunk_size: Number of records to update in each batch
            
        Returns:
            Dict containing success_count and error_count
        """
        if not self.batch_mode:
            logger.warning("commit_batch_updates called but batch mode is not enabled")
            return {"success_count": 0, "error_count": 0}
            
        total_records = len(self.batch_updates)
        if total_records == 0:
            logger.info("No batched updates to commit")
            return {"success_count": 0, "error_count": 0}
            
        logger.info(f"Committing {total_records} batched updates to Airtable")
        
        # Initialize counters
        success_count = 0
        error_count = 0
        
        # Process in chunks to avoid overloading Airtable API
        record_ids = list(self.batch_updates.keys())
        
        for i in range(0, total_records, chunk_size):
            chunk = record_ids[i:i+chunk_size]
            logger.info(f"Processing batch {i//chunk_size + 1}/{(total_records + chunk_size - 1)//chunk_size} ({len(chunk)} records)")
            
            for record_id in chunk:
                embedding_data = self.batch_updates[record_id]
                try:
                    await self.enforce_rate_limit()
                    
                    # Connect to Airtable
                    api = Api(self.api_key)
                    self.table = api.table(self.base_id, self.table_name)
                    
                    # Prepare update fields
                    update_fields = {
                        "VectorEmbeddings": embedding_data["embeddings_json"],
                        "ChunkCount": embedding_data["chunk_count"]
                    }
                    
                    # Update the record
                    self.table.update(record_id, update_fields)
                    success_count += 1
                    
                    # Small delay between API calls within a chunk
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error updating Airtable record {record_id}: {e}")
            
            # Delay between chunks
            if i + chunk_size < total_records:
                logger.info(f"Waiting 1 second before processing next batch...")
                await asyncio.sleep(1)
                
        # Clear the batch updates dictionary after processing
        self.batch_updates = {}
        
        logger.info(f"Batch update complete: {success_count} successful, {error_count} failed")
        return {"success_count": success_count, "error_count": error_count}
    
    async def enforce_rate_limit(self):
        """Ensure we don't exceed Airtable's rate limits."""
        current_time = asyncio.get_event_loop().time()
        elapsed = current_time - self.last_api_call
        
        if elapsed < self.min_delay:
            delay = self.min_delay - elapsed
            await asyncio.sleep(delay)
            
        self.last_api_call = asyncio.get_event_loop().time()
    
    async def save_embeddings(self, record_id, embeddings, frame_path=None):
        """Save the embeddings to Airtable record. Include metadata about the embeddings."""
        # Create embeddings JSON
        embeddings_json = self._format_embeddings_json(embeddings)
        chunk_count = len(embeddings)
        
        if self.use_webhook and frame_path:
            return await self._send_to_webhook(record_id, embeddings_json, chunk_count, frame_path)
        
        if self.batch_mode:
            # In batch mode, store for later
            self.batch_updates[record_id] = {
                "embeddings_json": embeddings_json,
                "chunk_count": chunk_count
            }
            logger.debug(f"Queued embeddings for Airtable record {record_id} (batch mode)")
            return True
        
        try:
            await self.enforce_rate_limit()
            
            # Connect to Airtable
            api = Api(self.api_key)
            self.table = api.table(self.base_id, self.table_name)
            
            # Prepare update fields
            update_fields = {
                "VectorEmbeddings": embeddings_json,
                "ChunkCount": chunk_count
            }
            
            # Update the record
            self.table.update(record_id, update_fields)
            logger.info(f"Successfully saved embeddings to Airtable record {record_id}")
            return True
            
        except Exception as e:
            if "INVALID_MULTIPLE_CHOICE_OPTIONS" in str(e):
                # Handle the case where ChunkCount field is a number field
                logger.info("Adding ChunkCount field: " + str(chunk_count))
                try:
                    update_fields = {
                        "VectorEmbeddings": embeddings_json,
                        "ChunkCount": int(chunk_count)
                    }
                    self.table.update(record_id, update_fields)
                    logger.info(f"Successfully saved embeddings to Airtable record {record_id}")
                    return True
                except Exception as e2:
                    logger.error(f"Error saving embeddings to Airtable (retry): {e2}")
                    return False
            else:
                logger.error(f"Error saving embeddings to Airtable: {e}")
                return False
    
    def _format_embeddings_json(self, embeddings):
        """Format embedding vectors for storage in Airtable.
        
        Airtable has limitations on field size, so we:
        1. Convert numpy arrays to lists if needed
        2. Format as a JSON string
        3. Include metadata about the embeddings
        """
        # Create a dictionary with embedding metadata
        embedding_data = {
            "model": "voyage-multimodal-3",
            "dimension": len(embeddings[0]["embedding"]) if embeddings else 0,
            "count": len(embeddings),
            "created_at": int(asyncio.get_event_loop().time()),
            "chunks": [],
            "vectors": []  # Store all full embedding vectors separately
        }
        
        # Add each chunk's data
        for i, embed_chunk in enumerate(embeddings):
            # Convert numpy arrays to lists if needed
            embedding_vector = embed_chunk["embedding"]
            if isinstance(embedding_vector, np.ndarray):
                embedding_vector = embedding_vector.tolist()
                
            # Add chunk metadata
            chunk_data = {
                "sequence_id": embed_chunk["chunk"]["chunk_sequence_id"],
                "text_length": len(embed_chunk["chunk"]["chunk_text"]),
                "text_preview": embed_chunk["chunk"]["chunk_text"][:100] + "..." if len(embed_chunk["chunk"]["chunk_text"]) > 100 else embed_chunk["chunk"]["chunk_text"],
                "embedding_preview": embedding_vector[:5] + ["..."] + embedding_vector[-5:],
            }
            embedding_data["chunks"].append(chunk_data)
            
            # Add full vector to the vectors array, each wrapped in square brackets
            embedding_data["vectors"].append(embedding_vector)
        
        return json.dumps(embedding_data)
    
    async def _send_to_webhook(self, airtable_id, embeddings_json, chunk_count, frame_path):
        """Send frame data to n8n webhook instead of directly updating Airtable."""
        try:
            # Determine the webhook URL based on environment
            webhook_url = N8N_TEST_WEBHOOK_URL if USE_TEST_WEBHOOK else N8N_PROD_WEBHOOK_URL
            
            if not webhook_url:
                logger.error("No webhook URL configured. Set WEBHOOK_TEST_URL or WEBHOOK_URL in environment.")
                return False
                
            # Get frame name and folder information
            frame_name = os.path.basename(frame_path)
            folder_path = os.path.dirname(frame_path)
            folder_name = os.path.basename(folder_path)
            
            # Format the folder path for Airtable
            # Use relative path if it makes sense for your setup
            formatted_folder_path = folder_path
            if '/home/' in folder_path:
                # Try to make the path relative or more readable
                parts = folder_path.split('/')
                if len(parts) > 4:  # /home/username/...
                    formatted_folder_path = '/'.join(parts[3:])  # Skip /home/username
            
            # Get metadata for the frame if possible
            metadata = {}
            try:
                metadata_finder = AirtableMetadataFinder(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
                record = metadata_finder.find_record_by_frame_path(frame_path)
                if record and 'fields' in record:
                    metadata = record['fields']
            except Exception as metadata_error:
                logger.warning(f"Error retrieving metadata for webhook: {metadata_error}")
            
            # Prepare payload
            payload = {
                "airtable_id": airtable_id,
                "frame_name": frame_name,
                "folder_path": formatted_folder_path,
                "folder_name": folder_name,
                "chunk_count": chunk_count,
                "embeddings": embeddings_json,
                "metadata": metadata,
                "environment": "test" if USE_TEST_WEBHOOK else "production",
                "timestamp": datetime.now().isoformat()
            }
            
            # Send webhook request
            logger.info(f"Sending data to n8n webhook for frame {frame_name}...")
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Successfully sent data to n8n webhook for frame {frame_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending data to n8n webhook: {e}")
            return False

class PostgresVectorStore:
    """Class to handle storing embeddings and chunks in Postgres/Supabase vector database."""
    
    def __init__(self, host, port, user, password, dbname):
        """Initialize with PostgreSQL connection parameters."""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.conn = None
        
        # Verify we have all required credentials
        missing = []
        if not host: missing.append("POSTGRES_HOST")
        if not user: missing.append("POSTGRES_USER")
        if not password: missing.append("POSTGRES_PASSWORD")
        if not dbname: missing.append("POSTGRES_DB")
        
        if missing:
            missing_str = ", ".join(missing)
            logger.error(f"Missing PostgreSQL credentials: {missing_str}")
            raise ValueError(f"Missing PostgreSQL credentials: {missing_str}")
            
        logger.info(f"Initialized PostgresVectorStore for database {dbname}")
    
    async def connect(self):
        """Create a connection to the PostgreSQL database."""
        try:
            if self.conn is None or self.conn.closed:
                self.conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    dbname=self.dbname
                )
                logger.info("Successfully connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False
    
    async def ensure_schema(self):
        """Check that the required schemas and tables exist."""
        if not await self.connect():
            return False
            
        try:
            with self.conn.cursor() as cur:
                # Check if pgvector extension exists
                cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
                if cur.fetchone() is None:
                    logger.error("pgvector extension is not installed")
                    return False
                
                # Check all required schemas exist
                for schema in ['embeddings', 'content', 'metadata', 'relationships']:
                    cur.execute(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{schema}';")
                    if cur.fetchone() is None:
                        logger.error(f"{schema} schema does not exist")
                        return False
                    
                # Check if the multimodal_embeddings table exists
                cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'embeddings' AND table_name = 'multimodal_embeddings';
                """)
                if cur.fetchone() is None:
                    logger.error("embeddings.multimodal_embeddings table does not exist")
                    return False
                
                # Check content schema tables
                content_tables = ['frames', 'videos', 'sessions', 'frame_details']
                for table in content_tables:
                    cur.execute(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'content' AND table_name = '{table}';
                    """)
                    if cur.fetchone() is None:
                        logger.warning(f"content.{table} table does not exist")
                
                # Check metadata schema tables
                metadata_tables = ['frame_metadata', 'video_metadata', 'session_metadata']
                for table in metadata_tables:
                    cur.execute(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'metadata' AND table_name = '{table}';
                    """)
                    if cur.fetchone() is None:
                        logger.warning(f"metadata.{table} table does not exist")
                
                logger.info("Required PostgreSQL schemas and tables exist")
                return True
                
        except Exception as e:
            logger.error(f"Error checking PostgreSQL schema: {e}")
            return False
    
    async def store_content_frame(self, frame_path, airtable_record_id, metadata=None):
        """Store frame data in the content.frames table."""
        if not await self.connect():
            return False
            
        # Extract frame_id (filename) and folder info from path
        frame_id = os.path.basename(frame_path)
        folder_path = os.path.dirname(frame_path)
        folder_name = os.path.basename(folder_path)
        
        # Check if we have folderPath in the metadata from Airtable
        airtable_folder_path = None
        if metadata and isinstance(metadata, dict) and 'folderPath' in metadata:
            airtable_folder_path = metadata['folderPath']
            logger.info(f"Using folderPath from Airtable: {airtable_folder_path}")
        
        # Get frame number from filename
        frame_number = None
        try:
            # Assuming filename format like frame_000001.jpg
            frame_number_match = re.search(r'frame_(\d+)', frame_id)
            if frame_number_match:
                frame_number = int(frame_number_match.group(1))
        except Exception as e:
            logger.warning(f"Could not extract frame number from filename: {e}")
        
        try:
            with self.conn.cursor() as cur:
                # First, check the actual schema of the table
                cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'content' AND table_name = 'frames'
                ORDER BY ordinal_position;
                """)
                
                columns = [row[0] for row in cur.fetchall()]
                logger.debug(f"Available columns in content.frames: {columns}")
                
                # Check if frame already exists
                cur.execute("SELECT frame_id FROM content.frames WHERE file_name = %s", (frame_id,))
                frame_result = cur.fetchone()
                
                # Determine which fields to use based on schema
                has_file_path = 'file_path' in columns
                has_airtable_id = 'airtable_id' in columns
                has_folder_path = 'folder_path' in columns
                has_folder_name = 'folder_name' in columns
                has_frame_number = 'frame_number' in columns
                
                if frame_result:
                    # Frame exists, update it with available fields
                    frame_uuid = frame_result[0]
                    update_fields = []
                    update_values = []
                    
                    if has_folder_path:
                        update_fields.append("folder_path = %s")
                        update_values.append(folder_path)
                    
                    if has_folder_name:
                        update_fields.append("folder_name = %s")
                        update_values.append(folder_name)
                    
                    if has_airtable_id:
                        update_fields.append("airtable_id = %s")
                        update_values.append(airtable_record_id)
                    
                    if has_file_path and airtable_folder_path:
                        update_fields.append("file_path = %s")
                        update_values.append(airtable_folder_path)
                    
                    # Add last_updated timestamp if available
                    if 'last_updated' in columns:
                        update_fields.append("last_updated = NOW()")
                    
                    if update_fields:
                        # Construct and execute the update query
                        update_query = f"""
                        UPDATE content.frames 
                        SET {', '.join(update_fields)}
                        WHERE frame_id = %s
                        """
                        update_values.append(frame_uuid)
                        cur.execute(update_query, tuple(update_values))
                        logger.info(f"Updated existing frame in content.frames: {frame_uuid}")
                else:
                    # Frame doesn't exist, build insert query based on available columns
                    insert_fields = ['frame_id', 'file_name']
                    insert_values = [f"uuid_generate_v4()", f"%s"]
                    query_params = [frame_id]
                    
                    if has_file_path:
                        insert_fields.append('file_path')
                        insert_values.append('%s')
                        # Use Airtable folderPath if available, otherwise use local path
                        query_params.append(airtable_folder_path if airtable_folder_path else folder_path)
                    
                    if has_folder_path:
                        insert_fields.append('folder_path')
                        insert_values.append('%s')
                        query_params.append(folder_path)
                    
                    if has_folder_name:
                        insert_fields.append('folder_name')
                        insert_values.append('%s')
                        query_params.append(folder_name)
                    
                    if has_frame_number and frame_number is not None:
                        insert_fields.append('frame_number')
                        insert_values.append('%s')
                        query_params.append(frame_number)
                    
                    if has_airtable_id:
                        insert_fields.append('airtable_id')
                        insert_values.append('%s')
                        query_params.append(airtable_record_id)
                    
                    # Add timestamps
                    if 'created_at' in columns:
                        insert_fields.append('created_at')
                        insert_values.append('NOW()')
                    
                    if 'last_updated' in columns:
                        insert_fields.append('last_updated')
                        insert_values.append('NOW()')
                    
                    # Construct and execute the insert query
                    insert_query = f"""
                    INSERT INTO content.frames 
                    ({', '.join(insert_fields)})
                    VALUES ({', '.join(insert_values)})
                    RETURNING frame_id
                    """
                    
                    cur.execute(insert_query, tuple(query_params))
                    frame_uuid = cur.fetchone()[0]
                    logger.info(f"Inserted new frame in content.frames: {frame_uuid}")
                    
                    # If we have metadata and frame_details table exists, store additional details
                    if metadata and isinstance(metadata, dict):
                        try:
                            # Check if frame_details table exists
                            cur.execute("""
                            SELECT table_name 
                            FROM information_schema.tables 
                            WHERE table_schema = 'content' AND table_name = 'frame_details';
                            """)
                            
                            if cur.fetchone():
                                # Store basic frame details
                                details = {}
                                
                                # Extract metadata fields
                                if 'OCRText' in metadata:
                                    details['ocr_text'] = metadata['OCRText']
                                if 'Summary' in metadata:
                                    details['summary'] = metadata['Summary']
                                if 'Tags' in metadata and isinstance(metadata['Tags'], list):
                                    details['tags'] = metadata['Tags']
                                
                                # Add extra metadata
                                details['metadata_source'] = 'airtable'
                                details['airtable_record_id'] = airtable_record_id
                                
                                # Insert into frame_details
                                cur.execute("""
                                INSERT INTO content.frame_details
                                (frame_id, details, created_at)
                                VALUES (%s, %s, NOW())
                                """, (frame_uuid, json.dumps(details)))
                                logger.info(f"Added frame details for {frame_uuid}")
                        except Exception as detail_error:
                            logger.warning(f"Error storing frame details: {detail_error}")
                
                # Commit the transaction
                self.conn.commit()
                return frame_uuid
                
        except Exception as e:
            logger.error(f"Error storing frame in content schema: {e}")
            try:
                if self.conn and not self.conn.closed:
                    self.conn.rollback()
            except Exception as rollback_error:
                logger.error(f"Error rolling back transaction: {rollback_error}")
            return False

    async def store_chunks(self, frame_path, airtable_record_id, embedded_chunks, metadata=None):
        """Store embedded chunks in the PostgreSQL vector database using existing schema."""
        if not await self.connect() or not await self.ensure_schema():
            return False
            
        # Extract frame_id (filename) from path
        frame_id = os.path.basename(frame_path)
        
        try:
            # First, store the frame data in the content schema
            db_frame_id = await self.store_content_frame(frame_path, airtable_record_id, metadata)
            if not db_frame_id:
                # If storing in content schema failed, default to using filename
                db_frame_id = frame_id
                logger.warning(f"Using filename as frame ID: {db_frame_id}")
            
            # Start a transaction
            with self.conn.cursor() as cur:
                # First, delete any existing embeddings for this frame to avoid duplicates
                cur.execute(
                    "DELETE FROM embeddings.multimodal_embeddings WHERE reference_id = %s AND reference_type = 'frame'",
                    (db_frame_id,)
                )
                logger.info(f"Cleared {cur.rowcount} existing embeddings for frame {db_frame_id}")
                
                # Insert new embeddings
                inserted = 0
                for embed_result in embedded_chunks:
                    chunk = embed_result["chunk"]
                    embedding = embed_result["embedding"]
                    chunk_text = chunk["chunk_text"]
                    
                    # Convert numpy array to list if needed
                    if isinstance(embedding, np.ndarray):
                        embedding = embedding.tolist()
                    
                    # Format as PostgreSQL vector
                    vector_str = f"[{','.join(str(x) for x in embedding)}]"
                    
                    # Generate a unique ID for this chunk
                    chunk_id = f"{db_frame_id}_chunk_{chunk['chunk_sequence_id']}"
                    
                    # Insert the embedding
                    cur.execute("""
                    INSERT INTO embeddings.multimodal_embeddings
                    (embedding_id, reference_id, reference_type, text_content, image_url, embedding, model_name)
                    VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s::vector, %s)
                    """, (
                        db_frame_id,        # reference_id - frame ID
                        'frame',            # reference_type
                        chunk_text,         # text_content - the chunk text
                        frame_path,         # image_url - using frame path as URL for now
                        vector_str,         # embedding
                        "voyage-multimodal-3"  # model_name
                    ))
                    inserted += 1
                
                # Commit the transaction
                self.conn.commit()
                logger.info(f"Successfully stored {inserted} chunk embeddings in PostgreSQL vector database")
                return True
                
        except Exception as e:
            logger.error(f"Error storing chunks in PostgreSQL: {e}")
            try:
                if self.conn and not self.conn.closed:
                    self.conn.rollback()
                    logger.info("Transaction rolled back")
            except Exception as rollback_error:
                logger.error(f"Error rolling back transaction: {rollback_error}")
            return False
        finally:
            # Close the connection
            try:
                if self.conn and not self.conn.closed:
                    self.conn.close()
                    self.conn = None
            except Exception as close_error:
                logger.error(f"Error closing connection: {close_error}")

async def process_frame(frame_path, chunk_size=500, chunk_overlap=50, max_chunks=None, 
                 force_reprocess=False, save_to_airtable=True, save_to_postgres=True,
                 airtable_store=None, use_webhook=False):
    """Process frame: find metadata, chunk it, and create embeddings.
    
    Args:
        frame_path: Path to the frame image
        chunk_size: Size of text chunks
        chunk_overlap: Overlap between chunks
        max_chunks: Maximum number of chunks to process
        force_reprocess: Force reprocessing even if cached
        save_to_airtable: Save embeddings to Airtable
        save_to_postgres: Save embeddings to PostgreSQL
        airtable_store: Optional shared AirtableEmbeddingStore instance
        use_webhook: Use n8n webhook instead of direct Airtable updates
        
    Returns:
        bool: True if processing was successful
    """
    # Validate API keys
    if not VOYAGE_API_KEYS or len(VOYAGE_API_KEYS) == 0:
        logger.error("No Voyage API keys available. Set at least one API key.")
        return False
    if not AIRTABLE_TOKEN:
        logger.error("AIRTABLE_PERSONAL_ACCESS_TOKEN not set in environment variables.")
        return False
    
    # Check if file exists
    if not os.path.exists(frame_path):
        logger.error(f"Frame file not found: {frame_path}")
        return False
    
    try:
        # Initialize cache
        processing_cache = ProcessingCache()
        
        # Step 1: Load the frame image
        logger.info(f"Loading image: {frame_path}")
        img = Image.open(frame_path)
        logger.info(f"Frame loaded: {img.size}px {img.format}")
        
        # Step 2: Find metadata for the frame
        logger.info("Finding Airtable metadata...")
        metadata_finder = AirtableMetadataFinder(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
        record = metadata_finder.find_record_by_frame_path(frame_path)
        
        if not record:
            logger.error(f"No metadata found for frame: {frame_path}")
            return False
        
        # Extract fields from the record
        metadata = record.get('fields', {})
        airtable_id = record.get('id')
        logger.info(f"Found metadata for frame with ID: {airtable_id}")
        
        # Check if this frame with this metadata has already been processed
        if not force_reprocess and processing_cache.is_processed(frame_path, metadata):
            logger.info(f"Frame {os.path.basename(frame_path)} already processed with this metadata. Skipping.")
            logger.info("Use --force flag to reprocess anyway.")
            return True
        
        # Step 3: Initialize the metadata chunker
        logger.info(f"Initializing metadata chunker (chunk_size={chunk_size}, overlap={chunk_overlap})...")
        chunker = MetadataChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        
        # Step 4: Process metadata into chunks
        logger.info("Processing metadata into chunks...")
        chunks = chunker.process_metadata(metadata, airtable_id, frame_path)
        logger.info(f"Generated {len(chunks)} chunks")
        
        # Limit the number of chunks if specified
        if max_chunks is not None and max_chunks > 0:
            original_chunks = len(chunks)
            chunks = chunks[:max_chunks]
            logger.info(f"Limiting to first {max_chunks} chunks out of {original_chunks}")
        
        # Quick token estimation based on character counts (no API call)
        quick_token_estimate = estimate_tokens_from_chars("".join([chunk["chunk_text"] for chunk in chunks]))
        logger.info(f"Quick token estimate based on character count: ~{quick_token_estimate} tokens")
        
        # Step 5: Initialize the chunk embedder
        logger.info("Initializing chunk embedder...")
        embedder = ChunkEmbedder(use_key_rotation=True)
        
        # Analyze token distribution in chunks
        token_analysis = embedder.analyze_chunk_token_distribution(chunks)
        logger.info(f"Token distribution analysis: {json.dumps(token_analysis, indent=2)}")
        
        # Provide optimization recommendations if needed
        if token_analysis.get("optimization_needed", False):
            logger.warning("Chunk sizes vary significantly. Consider adjusting chunk_size and chunk_overlap parameters.")
            
            # Recommend smaller chunk size if max tokens is high
            if token_analysis.get("max_tokens", 0) > 512:  # Arbitrary threshold
                logger.warning(f"Consider reducing chunk_size (currently {chunk_size}) for more balanced chunks")
            
            # Highlight outlier chunks
            if token_analysis.get("outlier_chunks", []):
                outlier_indices = token_analysis.get("outlier_chunks", [])
                for idx in outlier_indices[:3]:  # Show first 3 outliers
                    logger.warning(f"Outlier chunk #{idx} has {token_analysis['token_counts'][idx]} tokens (significantly above average)")
        
        # Quick token estimation using character counts
        quick_estimates = embedder.estimate_tokens_quick(chunks)
        logger.info(f"Character-based token estimation: ~{quick_estimates['total_tokens_estimate']} total tokens")
        
        # Accurate token estimation using the actual tokenizer
        token_count = embedder.estimate_tokens_from_chunks(chunks)
        logger.info(f"Actual token count for text chunks: {token_count}")
        
        # If image is available, estimate multimodal usage
        if img:
            usage_estimate = embedder.estimate_multimodal_usage(chunks, img)
            logger.info(f"Estimated usage for multimodal processing: {usage_estimate}")
            logger.info(f"  - Text tokens: {usage_estimate['text_tokens']}")
            logger.info(f"  - Image pixels: {usage_estimate['image_pixels']}")
            logger.info(f"  - Total tokens: {usage_estimate['total_tokens']}")
        
        # Step 6: Create embeddings for all chunks
        logger.info("Creating embeddings for chunks...")
        embedded_chunks = await embedder.embed_chunks(chunks, img)
        
        # Step 7: Report results
        logger.info(f"Successfully embedded {len(embedded_chunks)} out of {len(chunks)} chunks")
        
        # Step 8: Print sample values from first embedding
        embedding_dim = 0
        if embedded_chunks:
            first_embed = embedded_chunks[0]
            logger.info(f"Sample embedding (first 5 values): {first_embed['embedding'][:5]}")
            embedding_dim = first_embed['embedding_dim']
            logger.info(f"Embedding dimensions: {embedding_dim}")
            
            # Step 9: Save embeddings to Airtable if requested
            if save_to_airtable and embedded_chunks:
                logger.info(f"Saving embeddings to Airtable record {airtable_id}...")
                
                # Use the provided store or create a new one
                if not airtable_store:
                    airtable_store = AirtableEmbeddingStore(use_webhook=use_webhook)
                
                # Save embeddings
                airtable_success = await airtable_store.save_embeddings(airtable_id, embedded_chunks, frame_path)
                
                if airtable_success:
                    logger.info("Embeddings successfully saved to Airtable")
                else:
                    logger.error("Failed to save embeddings to Airtable")
            
            # Step 10: Save embeddings to PostgreSQL vector database if requested
            if save_to_postgres and embedded_chunks and all([POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]):
                logger.info("Saving embeddings to PostgreSQL vector database...")
                postgres_store = PostgresVectorStore(
                    POSTGRES_HOST, 
                    POSTGRES_PORT, 
                    POSTGRES_USER, 
                    POSTGRES_PASSWORD, 
                    POSTGRES_DB
                )
                postgres_success = await postgres_store.store_chunks(frame_path, airtable_id, embedded_chunks, metadata)
                if postgres_success:
                    logger.info("Embeddings successfully saved to PostgreSQL vector database")
                else:
                    logger.warning("Failed to save embeddings to PostgreSQL vector database")
        
        # Step 11: Mark as processed in cache
        processing_cache.mark_processed(frame_path, metadata, len(chunks), embedding_dim)
        
        return True
    except Exception as e:
        logger.error(f"Error in processing pipeline: {e}")
        return False

async def tokenize_only(text, model="voyage-multimodal-3"):
    """Standalone function to tokenize text and display token information.
    
    This is useful for testing tokenization without doing a full embedding process.
    
    Args:
        text (str): Text to tokenize
        model (str): Model name to use for tokenization
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Initialize voyageai client
        if not any(VOYAGE_API_KEYS):
            logger.error("No Voyage API keys available")
            return False
        
        client = voyageai.Client()
        client.api_key = VOYAGE_API_KEYS[0]
        
        # Tokenize the text
        logger.info(f"Tokenizing text with model {model}...")
        
        # For demonstration, show both tokenization and token count
        tokenized = client.tokenize([text], model=model)
        token_count = client.count_tokens([text], model=model)
        
        # Print token information
        logger.info(f"Text: {text[:100]}..." if len(text) > 100 else f"Text: {text}")
        logger.info(f"Token count: {token_count}")
        
        # Print the first 20 tokens for demonstration
        if tokenized and len(tokenized) > 0:
            tokens = tokenized[0].tokens
            display_tokens = tokens[:20] if len(tokens) > 20 else tokens
            logger.info(f"First {len(display_tokens)} tokens: {display_tokens}")
            logger.info(f"Total tokens: {len(tokens)}")
            
            # Show approximate token to character ratio for estimation
            char_count = len(text)
            if token_count > 0:
                logger.info(f"Characters per token ratio: {char_count / token_count:.2f}")
            
            return True
        else:
            logger.error("Failed to get tokenization results")
            return False
            
    except Exception as e:
        logger.error(f"Error in tokenize_only: {e}")
        return False

async def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Test embedding metadata chunks with Voyage AI')
    parser.add_argument('frame_path', help='Path to the frame image file or text to tokenize if --tokenize-only is used')
    parser.add_argument('--chunk-size', type=int, default=500, help='Target size for text chunks')
    parser.add_argument('--chunk-overlap', type=int, default=50, help='Overlap between chunks')
    parser.add_argument('--max-chunks', type=int, default=None, help='Maximum number of chunks to process')
    parser.add_argument('--force', action='store_true', help='Force reprocessing even if already processed')
    parser.add_argument('--no-save', action='store_true', help='Skip saving embeddings to Airtable')
    parser.add_argument('--no-postgres', action='store_true', help='Skip saving embeddings to PostgreSQL vector database')
    parser.add_argument('--tokenize-only', action='store_true', help='Only tokenize text without creating embeddings')
    parser.add_argument('--model', default='voyage-multimodal-3', help='Model to use (only relevant with --tokenize-only)')
    parser.add_argument('--use-webhook', action='store_true', help='Use n8n webhook instead of direct Airtable updates')
    args = parser.parse_args()
    
    if args.tokenize_only:
        # In tokenize-only mode, treat the frame_path as text to tokenize
        success = await tokenize_only(args.frame_path, model=args.model)
        if success:
            logger.info("✅ Tokenization completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Tokenization failed.")
            sys.exit(1)
    else:
        # Normal processing mode
        success = await process_frame(
            args.frame_path, 
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            max_chunks=args.max_chunks,
            force_reprocess=args.force,
            save_to_airtable=not args.no_save,
            save_to_postgres=not args.no_postgres,
            use_webhook=args.use_webhook
        )
        
        if success:
            logger.info("✅ Frame processing and embedding completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Frame processing and embedding failed.")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 