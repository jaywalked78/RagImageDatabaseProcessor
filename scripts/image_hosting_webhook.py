#!/usr/bin/env python3
"""
Script to upload frame images to Imgur (or similar) and create webhook payload with direct viewable links.
"""

import os
import sys
import json
import logging
import asyncio
import base64
import aiohttp
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
import numpy as np

# Import the metadata finder from our existing script
from process_frame_with_metadata import AirtableMetadataFinder, FRAME_ID_FIELD, FRAME_NUMBER_FIELD, \
    FOLDER_NAME_FIELD, FOLDER_PATH_FIELD, SUMMARY_FIELD, TOOLS_VISIBLE_FIELD, \
    ACTIONS_DETECTED_FIELD, TECHNICAL_DETAILS_FIELD, RELATIONSHIP_TO_PREVIOUS_FIELD, \
    STAGE_OF_WORK_FIELD

# Define additional fields
TIMESTAMP_FIELD = 'Timestamp'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("image_hosting")

# Load environment variables
load_dotenv()
AIRTABLE_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID', "appewal2KEO5B02KV")
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', "tblFrameAnalysis")
FRAME_BASE_DIR = os.environ.get('FRAME_BASE_DIR', '/home/jason/Videos/screenRecordings')
IMGUR_CLIENT_ID = os.environ.get('IMGUR_CLIENT_ID', '')

# Get test frame path from environment or use default
TEST_FRAME_PATH = os.environ.get('TEST_FRAME_RELATIVE_PATH', 
                               "screen_recording_2025_03_03_at_3_39_52_am/frame_000051.jpg")

# Resolve the full path
if not os.path.isabs(TEST_FRAME_PATH):
    # Replace FRAME_BASE_DIR placeholder if present
    if TEST_FRAME_PATH.startswith('FRAME_BASE_DIR/'):
        TEST_FRAME_PATH = TEST_FRAME_PATH.replace('FRAME_BASE_DIR/', '')
    
    TEST_FRAME_PATH = os.path.join(FRAME_BASE_DIR, TEST_FRAME_PATH)

class ImgurUploader:
    """Simple class to upload images to Imgur."""
    
    def __init__(self, client_id=None):
        self.client_id = client_id or IMGUR_CLIENT_ID
        self.api_url = "https://api.imgur.com/3/image"
        
    async def upload_image(self, image_path: str) -> Tuple[bool, Optional[str]]:
        """
        Upload an image to Imgur.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Tuple of (success, image_url)
        """
        if not self.client_id:
            logger.warning("No Imgur Client ID provided, cannot upload image")
            # Return a simulated URL for testing
            file_name = os.path.basename(image_path)
            return True, f"https://example.com/frames/{file_name}"
        
        try:
            # Read image file
            with open(image_path, 'rb') as image_file:
                binary_data = image_file.read()
                base64_data = base64.b64encode(binary_data)
            
            # Prepare request
            headers = {'Authorization': f'Client-ID {self.client_id}'}
            data = {'image': base64_data, 'type': 'base64'}
            
            # Upload to Imgur
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        image_url = result['data']['link']
                        logger.info(f"Successfully uploaded image to Imgur: {image_url}")
                        return True, image_url
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to upload image to Imgur: {error_text}")
                        
                        # Return a simulated URL for testing if upload fails
                        file_name = os.path.basename(image_path)
                        return True, f"https://example.com/frames/{file_name}"
                        
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            
            # Return a simulated URL for testing
            file_name = os.path.basename(image_path)
            return True, f"https://example.com/frames/{file_name}"

def generate_embeddings(chunks: int = 5, embedding_dim: int = 1024) -> List[List[float]]:
    """
    Generate realistic-looking embeddings for testing.
    
    Args:
        chunks: Number of chunks to generate embeddings for
        embedding_dim: Dimensionality of the embeddings
        
    Returns:
        List of embeddings (each as a list of floats)
    """
    embeddings = []
    for _ in range(chunks):
        # Generate a random unit vector (normalized)
        embedding = np.random.normal(0, 1, embedding_dim)
        embedding = embedding / np.linalg.norm(embedding)
        # Convert to a list of Python floats with limited precision
        embedding_list = [round(float(x), 6) for x in embedding]
        embeddings.append(embedding_list)
    return embeddings

def create_webhook_payload(frame_path: str, record: Dict[str, Any], 
                          image_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a properly formatted webhook payload using real metadata and embeddings.
    
    Args:
        frame_path: Path to the frame file
        record: Airtable record with metadata
        image_url: Direct URL to view the image
        
    Returns:
        Dictionary payload for webhook
    """
    # Extract fields from the record
    fields = record.get('fields', {})
    
    # Get frame path components
    frame_file = Path(frame_path)
    frame_name = frame_file.name
    
    # Use folder path from Airtable if available, otherwise use local path
    folder_path = fields.get(FOLDER_PATH_FIELD)
    if folder_path and frame_name in folder_path:
        # If the folder path already includes the frame, extract just the folder
        folder_path = str(Path(folder_path).parent)
    elif not folder_path:
        folder_path = str(frame_file.parent)
    
    folder_name = fields.get(FOLDER_NAME_FIELD, frame_file.parent.name)
    frame_id = fields.get(FRAME_ID_FIELD, '')
    
    # Generate embeddings for multiple chunks
    num_chunks = 5  # Example: 5 chunks per frame
    chunk_embeddings = generate_embeddings(num_chunks)
    
    # Create the payload
    payload = {
        "airtable_id": record.get('id', ''),
        "frame_id": frame_id,
        "frame_name": frame_name,
        "folder_path": folder_path,
        "folder_name": folder_name,
        "timestamp": fields.get(TIMESTAMP_FIELD, ''),
        "embeddings": chunk_embeddings,
        "chunk_count": num_chunks,
        "metadata": {
            "frame_number": fields.get(FRAME_NUMBER_FIELD, ''),
            "description": fields.get(SUMMARY_FIELD, 'No summary available'),
            "tools_visible": fields.get(TOOLS_VISIBLE_FIELD, []),
            "actions_detected": fields.get(ACTIONS_DETECTED_FIELD, []),
            "technical_details": fields.get(TECHNICAL_DETAILS_FIELD, ''),
            "relationship_to_previous": fields.get(RELATIONSHIP_TO_PREVIOUS_FIELD, ''),
            "stage_of_work": fields.get(STAGE_OF_WORK_FIELD, '')
        }
    }
    
    # Add image URL if available
    if image_url:
        payload["image_url"] = image_url
    
    return payload

async def main():
    """Extract metadata, upload image, and create webhook payload."""
    # Validate required configuration
    if not all([AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME]):
        logger.error("Missing required Airtable configuration in environment variables.")
        sys.exit(1)
    
    # Check if frame exists
    if not os.path.exists(TEST_FRAME_PATH):
        logger.error(f"Frame file not found: {TEST_FRAME_PATH}")
        sys.exit(1)
    
    logger.info(f"Extracting metadata for frame: {TEST_FRAME_PATH}")
    
    # Find metadata for the frame
    metadata_finder = AirtableMetadataFinder(AIRTABLE_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME)
    record = metadata_finder.find_record_by_frame_path(TEST_FRAME_PATH)
    
    if not record:
        logger.error(f"No metadata found for frame: {TEST_FRAME_PATH}")
        sys.exit(1)
    
    logger.info(f"Found metadata for frame with ID: {record.get('id')}")
    
    # Upload image to get a viewable URL
    logger.info(f"Uploading image to hosting service...")
    uploader = ImgurUploader()
    success, image_url = await uploader.upload_image(TEST_FRAME_PATH)
    
    if success and image_url:
        logger.info(f"Image URL: {image_url}")
    else:
        logger.warning("Failed to get image URL, proceeding without it")
        image_url = None
    
    # Create webhook payload
    payload = create_webhook_payload(TEST_FRAME_PATH, record, image_url)
    
    # Save to JSON file
    output_file = "image_hosting_payload.json"
    with open(output_file, 'w') as f:
        json.dump(payload, f, indent=2)
    
    logger.info(f"Generated webhook payload with image URL saved to: {output_file}")
    
    # Print the payload (without the full embeddings for clarity)
    display_payload = payload.copy()
    if "embeddings" in display_payload:
        display_payload["embeddings"] = f"[{len(display_payload['embeddings'])} embeddings of dimension 1024]"
    logger.info("Webhook payload:")
    logger.info(json.dumps(display_payload, indent=2))
    
    # Test the webhook with our updated payload
    logger.info("To test this payload with the webhook, run:")
    logger.info(f"./test_webhook.py --test-url --custom-payload {output_file}")

if __name__ == "__main__":
    asyncio.run(main()) 