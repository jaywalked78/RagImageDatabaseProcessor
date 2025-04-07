#!/usr/bin/env python3
"""
Webhook integration module for sending frame data to n8n or other webhook services.
"""

import os
import json
import logging
import time
import random
from typing import Dict, List, Any, Optional, Union
import aiohttp
import asyncio

import dotenv

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class WebhookSender:
    """
    Client for sending frame data and embeddings to webhook services.
    """
    
    def __init__(self, 
                webhook_url: Optional[str] = None,
                webhook_url_test: Optional[str] = None,
                max_retries: int = 3):
        """
        Initialize the webhook sender.
        
        Args:
            webhook_url: Production webhook URL (default: from env var WEBHOOK_URL)
            webhook_url_test: Test webhook URL (default: from env var WEBHOOK_URL_TEST)
            max_retries: Maximum number of retries for failed requests
        """
        # Initialize webhook URLs
        self.webhook_url = webhook_url or os.getenv("WEBHOOK_URL")
        self.webhook_url_test = webhook_url_test or os.getenv("WEBHOOK_URL_TEST")
        self.max_retries = max_retries
        
        # Create session for reuse
        self.session = None
        
        # Log configuration
        if self.webhook_url:
            logger.info(f"Webhook URL configured: {self.webhook_url[:20]}...")
        if self.webhook_url_test:
            logger.info(f"Test webhook URL configured: {self.webhook_url_test[:20]}...")
        
        if not self.webhook_url and not self.webhook_url_test:
            logger.warning("No webhook URLs configured. Set WEBHOOK_URL or WEBHOOK_URL_TEST environment variables.")
    
    def get_active_webhook_url(self, use_test: bool = False) -> Optional[str]:
        """
        Get the active webhook URL based on configuration.
        
        Args:
            use_test: Whether to use the test webhook URL
            
        Returns:
            Active webhook URL or None if not configured
        """
        if use_test and self.webhook_url_test:
            return self.webhook_url_test
        elif self.webhook_url:
            return self.webhook_url
        else:
            return None
    
    async def _ensure_session(self):
        """Ensure an aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers={
                "Content-Type": "application/json"
            })
        return self.session
    
    async def send_frame_data(self,
                            frame_name: str,
                            folder_path: str,
                            folder_name: str,
                            metadata: Dict[str, Any] = None,
                            google_drive_url: Optional[str] = None,
                            airtable_record_id: Optional[str] = None,
                            use_test: bool = False) -> bool:
        """
        Send frame data to webhook.
        
        Args:
            frame_name: Name of the frame
            folder_path: Path to the folder containing the frame
            folder_name: Name of the folder containing the frame
            metadata: Dictionary of metadata for the frame
            google_drive_url: Optional Google Drive URL for the frame
            airtable_record_id: Optional Airtable record ID
            use_test: Whether to use the test webhook URL
            
        Returns:
            Boolean indicating success
        """
        webhook_url = self.get_active_webhook_url(use_test)
        if not webhook_url:
            logger.error("No webhook URL configured for frame data")
            return False
        
        # Format the folder path
        formatted_folder_path = self._format_folder_path(folder_path)
        
        # Prepare payload
        payload = {
            "frame_name": frame_name,
            "folder_path": formatted_folder_path,
            "folder_name": folder_name,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        # Add optional fields
        if google_drive_url:
            payload["google_drive_url"] = google_drive_url
        if airtable_record_id:
            payload["airtable_record_id"] = airtable_record_id
        
        # Send the payload
        return await self._send_with_retries(webhook_url, payload)
    
    async def send_embedding_data(self,
                               embedding_id: str,
                               reference_id: str,
                               text_content: str,
                               embedding: List[float],
                               model_name: str,
                               metadata: Optional[Dict[str, Any]] = None,
                               use_test: bool = False) -> bool:
        """
        Send embedding data to webhook.
        
        Args:
            embedding_id: ID of the embedding
            reference_id: ID of the referenced object (e.g., frame name)
            text_content: Text content of the embedding
            embedding: Embedding vector
            model_name: Name of the embedding model
            metadata: Optional metadata for the embedding
            use_test: Whether to use the test webhook URL
            
        Returns:
            Boolean indicating success
        """
        webhook_url = self.get_active_webhook_url(use_test)
        if not webhook_url:
            logger.error("No webhook URL configured for embedding data")
            return False
        
        # Prepare payload
        payload = {
            "embedding_id": embedding_id,
            "reference_id": reference_id,
            "text_content": text_content,
            "model_name": model_name,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        # Don't include the full embedding in the webhook payload
        # Instead, include dimension and a few sample values
        if embedding:
            payload["embedding_dimension"] = len(embedding)
            payload["embedding_sample"] = embedding[:5]
        
        # Send the payload
        return await self._send_with_retries(webhook_url, payload)
    
    async def _send_with_retries(self, url: str, payload: Dict[str, Any]) -> bool:
        """
        Send data to webhook with retries and exponential backoff.
        
        Args:
            url: Webhook URL
            payload: Data payload to send
            
        Returns:
            Boolean indicating success
        """
        session = await self._ensure_session()
        
        for attempt in range(self.max_retries):
            try:
                async with session.post(url, json=payload) as response:
                    if response.status in [200, 201, 202]:
                        logger.info(f"Successfully sent data to webhook")
                        return True
                    else:
                        response_text = await response.text()
                        error = f"HTTP {response.status}: {response_text}"
                        logger.warning(f"Webhook error: {error}")
                        
                        if attempt < self.max_retries - 1:
                            # Exponential backoff with jitter
                            wait_time = (2 ** attempt) + random.random()
                            logger.info(f"Retrying in {wait_time:.2f}s")
                            await asyncio.sleep(wait_time)
            
            except Exception as e:
                logger.error(f"Error sending to webhook: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff with jitter
                    wait_time = (2 ** attempt) + random.random()
                    logger.info(f"Retrying in {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
        
        return False
    
    def _format_folder_path(self, folder_path: str) -> str:
        """
        Format folder path for better readability.
        
        Args:
            folder_path: Original folder path
            
        Returns:
            Formatted folder path
        """
        if not folder_path:
            return ""
        
        # Make the path relative if it contains /home/
        if "/home/" in folder_path:
            parts = folder_path.split("/home/")
            if len(parts) > 1:
                user_path = parts[1].split("/")
                if len(user_path) > 1:
                    # Remove username from path for privacy/simplicity
                    return "/".join(user_path[1:])
        
        return folder_path
    
    async def close(self):
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Closed webhook sender session")
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