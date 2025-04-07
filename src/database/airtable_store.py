#!/usr/bin/env python3
"""
Module for storing embeddings in Airtable.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional

import numpy as np
from pyairtable import Api
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', 'tblFrameAnalysis')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
WEBHOOK_TEST_URL = os.environ.get('WEBHOOK_TEST_URL')

# Configure logging
logger = logging.getLogger(__name__)

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
            
            # Add full vector to the vectors array
            embedding_data["vectors"].append(embedding_vector)
            
        # Convert to JSON string
        try:
            return json.dumps(embedding_data)
        except Exception as e:
            logger.error(f"Error converting embedding data to JSON: {e}")
            return "{}"
    
    async def _send_to_webhook(self, airtable_id, embeddings_json, chunk_count, frame_path):
        """Send embeddings to a webhook instead of directly updating Airtable."""
        try:
            # Import the webhook module
            from src.connectors.webhook import WebhookConnector
            
            # Create webhook payload
            frame_name = os.path.basename(frame_path)
            folder_path = os.path.dirname(frame_path)
            folder_name = os.path.basename(folder_path)
            
            webhook_payload = {
                "airtable_id": airtable_id,
                "frame_name": frame_name,
                "folder_path": folder_path,
                "folder_name": folder_name,
                "chunk_count": chunk_count,
                "embeddings": embeddings_json,
                "webhook_source": "test" if WEBHOOK_TEST_URL else "production",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # Send to webhook
            webhook_connector = WebhookConnector(WEBHOOK_URL, WEBHOOK_TEST_URL)
            success = await webhook_connector.send_payload(webhook_payload, use_test=True)
            
            if success:
                logger.info(f"Successfully sent embeddings to webhook for frame {frame_name}")
                return True
            else:
                logger.error(f"Failed to send embeddings to webhook for frame {frame_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending to webhook: {e}")
            return False 