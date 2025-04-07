#!/usr/bin/env python3
"""
Module for handling webhook interactions with n8n or other webhook endpoints.
Provides functionality to send payloads to webhooks with retry capability.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional
import aiohttp
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
WEBHOOK_TEST_URL = os.environ.get('WEBHOOK_TEST_URL')

class WebhookConnector:
    """Class for handling interactions with webhooks."""
    
    def __init__(self, 
                 webhook_url: Optional[str] = None, 
                 test_webhook_url: Optional[str] = None,
                 max_retries: int = 3,
                 retry_delay: float = 1.0):
        """
        Initialize the webhook connector.
        
        Args:
            webhook_url: Production webhook URL (defaults to env var WEBHOOK_URL)
            test_webhook_url: Test webhook URL (defaults to env var WEBHOOK_TEST_URL)
            max_retries: Maximum number of retries on failure
            retry_delay: Delay between retries in seconds
        """
        self.webhook_url = webhook_url or WEBHOOK_URL
        self.test_webhook_url = test_webhook_url or WEBHOOK_TEST_URL
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        if not self.webhook_url and not self.test_webhook_url:
            logger.warning("No webhook URLs configured. Set WEBHOOK_URL or WEBHOOK_TEST_URL environment variables.")
    
    async def send_payload(self, 
                          payload: Dict[str, Any], 
                          use_test_webhook: bool = True,
                          headers: Optional[Dict[str, str]] = None) -> bool:
        """
        Send payload to webhook with retry capability.
        
        Args:
            payload: The payload to send to the webhook
            use_test_webhook: Whether to use the test webhook URL
            headers: Additional headers to include in the request
            
        Returns:
            True if successful, False otherwise
        """
        webhook_url = self.test_webhook_url if use_test_webhook else self.webhook_url
        
        if not webhook_url:
            logger.error("No webhook URL configured for the specified mode")
            return False
        
        logger.info(f"Sending payload to webhook URL: {webhook_url}")
        
        # Set default headers
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        else:
            headers.setdefault('Content-Type', 'application/json')
        
        # Try to send payload with retries
        retries = 0
        while retries <= self.max_retries:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(webhook_url, json=payload, headers=headers) as response:
                        if response.status == 200:
                            response_text = await response.text()
                            logger.info(f"Webhook call successful. Response: {response_text}")
                            return True
                        else:
                            response_text = await response.text()
                            logger.error(f"Webhook call failed: HTTP {response.status}")
                            logger.error(f"Response: {response_text}")
                            
                            # Check if we should retry
                            if retries < self.max_retries:
                                retries += 1
                                logger.info(f"Retrying ({retries}/{self.max_retries})...")
                                await asyncio.sleep(self.retry_delay)
                            else:
                                logger.error("Max retries reached")
                                return False
            except Exception as e:
                logger.error(f"Error sending webhook: {e}")
                if retries < self.max_retries:
                    retries += 1
                    logger.info(f"Retrying ({retries}/{self.max_retries})...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("Max retries reached")
                    return False
        
        return False

# Convenience function for backward compatibility
async def send_webhook_payload(webhook_url: str, payload: Dict[str, Any], 
                              max_retries: int = 3, retry_delay: float = 1.0) -> bool:
    """
    Send payload to webhook with retry capability.
    
    This is a convenience function that creates a WebhookConnector instance
    and calls its send_payload method.
    
    Args:
        webhook_url: URL of the webhook
        payload: The payload to send
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
        
    Returns:
        True if successful, False otherwise
    """
    connector = WebhookConnector(webhook_url=webhook_url, max_retries=max_retries, retry_delay=retry_delay)
    return await connector.send_payload(payload, use_test_webhook=False) 