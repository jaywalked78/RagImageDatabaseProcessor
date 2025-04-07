#!/usr/bin/env python3
"""
Webhook test script for n8n integration.

This script helps test the webhook functionality by sending test data to an n8n webhook,
which can then be used to store data in Airtable.
"""

import os
import sys
import json
import asyncio
import logging
import argparse
from datetime import datetime
from typing import Dict, Any, Optional, List

import aiohttp
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("webhook_test")

async def send_webhook_payload(webhook_url: str, payload: Dict[str, Any], retries: int = 3) -> bool:
    """
    Send a payload to the webhook URL.
    
    Args:
        webhook_url: The webhook URL to send data to
        payload: The payload to send
        retries: Number of retry attempts
    
    Returns:
        Boolean indicating success
    """
    if not webhook_url:
        logger.error("No webhook URL provided")
        return False
    
    logger.info(f"Sending payload to webhook URL: {webhook_url}")
    logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
    
    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            try:
                async with session.post(webhook_url, json=payload, timeout=30) as response:
                    if response.status in [200, 201, 202]:
                        response_text = await response.text()
                        logger.info(f"Webhook call successful: HTTP {response.status}")
                        logger.debug(f"Response: {response_text}")
                        return True
                    else:
                        response_text = await response.text()
                        logger.error(f"Webhook call failed: HTTP {response.status}")
                        logger.error(f"Response: {response_text}")
                        
                        if attempt < retries - 1:
                            logger.info(f"Retrying ({attempt+1}/{retries})...")
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        else:
                            logger.error("Max retries reached")
                            return False
            
            except Exception as e:
                logger.error(f"Error sending webhook: {e}")
                
                if attempt < retries - 1:
                    logger.info(f"Retrying ({attempt+1}/{retries})...")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("Max retries reached")
                    return False
    
    return False

def generate_test_frame_data(frame_id: str = None) -> Dict[str, Any]:
    """
    Generate test frame data payload.
    
    Args:
        frame_id: Optional frame ID to use
    
    Returns:
        Dictionary with test frame data
    """
    # Generate a frame ID if not provided
    if not frame_id:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        frame_id = f"test_frame_{timestamp}"
    
    # Create a test payload
    payload = {
        "frame_name": frame_id,
        "folder_path": "/test/frames/sample",
        "folder_name": "sample",
        "timestamp": datetime.now().isoformat(),
        "google_drive_url": f"https://drive.google.com/file/d/{frame_id}/view",
        "airtable_record_id": f"rec{frame_id.replace('_', '')}",
        "metadata": {
            "description": "Test frame for webhook integration",
            "tags": ["test", "webhook", "sample"],
            "source": "webhook_test_script",
            "frame_type": "test",
            "resolution": "1920x1080",
            "format": "jpg",
            "size_kb": 1024
        }
    }
    
    return payload

def generate_test_embedding_data(frame_id: str = None) -> Dict[str, Any]:
    """
    Generate test embedding data payload.
    
    Args:
        frame_id: Optional frame ID to use
    
    Returns:
        Dictionary with test embedding data
    """
    # Generate a frame ID if not provided
    if not frame_id:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        frame_id = f"test_frame_{timestamp}"
    
    # Create a test payload
    embedding_id = f"emb_{frame_id}"
    
    payload = {
        "embedding_id": embedding_id,
        "reference_id": frame_id,
        "text_content": "This is a test embedding for frame metadata. It contains sample text.",
        "model_name": "voyage-large-2",
        "timestamp": datetime.now().isoformat(),
        "metadata": {
            "chunk_id": 1,
            "chunk_type": "metadata",
            "embedding_dimension": 1024,
            "embedding_sample": [0.1, 0.2, 0.3, 0.4, 0.5]  # First 5 values
        }
    }
    
    return payload

async def main():
    """Main function for the webhook test script."""
    parser = argparse.ArgumentParser(description="Test webhook integration with n8n")
    
    # Webhook options
    parser.add_argument("--url", help="Webhook URL (default: from WEBHOOK_URL env var)")
    parser.add_argument("--test-url", help="Test webhook URL (default: from WEBHOOK_URL_TEST env var)", 
                       action="store_true")
    
    # Payload options
    parser.add_argument("--type", choices=["frame", "embedding", "both"], default="frame",
                      help="Type of test data to send (default: frame)")
    parser.add_argument("--frame-id", help="Frame ID to use in the test payload")
    parser.add_argument("--custom-payload", help="Path to JSON file with custom payload")
    parser.add_argument("--batch", action="store_true",
                      help="Process custom payload as a batch (JSON array)")
    
    # Output options
    parser.add_argument("--print-payload", action="store_true", 
                      help="Print the payload being sent")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get webhook URL
    webhook_url = args.url
    if not webhook_url:
        if args.test_url:
            webhook_url = os.getenv("WEBHOOK_URL_TEST")
        else:
            webhook_url = os.getenv("WEBHOOK_URL")
    
    if not webhook_url:
        logger.error("No webhook URL specified. Use --url or set WEBHOOK_URL environment variable.")
        sys.exit(1)
    
    # Load custom payload if specified
    custom_payloads = []
    if args.custom_payload:
        try:
            with open(args.custom_payload, 'r') as file:
                data = json.load(file)
                logger.info(f"Loaded custom payload from {args.custom_payload}")
                
                # Check if the data is a list/array for batch processing
                if isinstance(data, list):
                    custom_payloads = data
                    logger.info(f"Found {len(custom_payloads)} items in batch payload")
                else:
                    custom_payloads = [data]
        except Exception as e:
            logger.error(f"Error loading custom payload: {e}")
            sys.exit(1)
    
    # Process payloads
    payloads = []
    
    if custom_payloads:
        # Use custom payload(s)
        payloads = custom_payloads
    else:
        # Generate payloads based on type
        if args.type in ["frame", "both"]:
            frame_payload = generate_test_frame_data(args.frame_id)
            payloads.append(frame_payload)
        
        if args.type in ["embedding", "both"]:
            embedding_payload = generate_test_embedding_data(args.frame_id)
            payloads.append(embedding_payload)
    
    # Print payloads if requested
    if args.print_payload:
        logger.info("Generated payloads:")
        for i, payload in enumerate(payloads):
            logger.info(f"Payload {i+1}:")
            logger.info(json.dumps(payload, indent=2))
    
    # Send payloads
    for i, payload in enumerate(payloads):
        logger.info(f"Sending payload {i+1}/{len(payloads)}...")
        success = await send_webhook_payload(webhook_url, payload)
        
        if success:
            logger.info(f"Successfully sent payload {i+1}")
        else:
            logger.error(f"Failed to send payload {i+1}")
            sys.exit(1)
    
    logger.info(f"Successfully sent {len(payloads)} payload(s) to webhook")

if __name__ == "__main__":
    asyncio.run(main()) 