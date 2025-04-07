"""
Test script for frame embedding using VoyageAI.
Loads a test frame and generates an embedding.
"""

import os
import sys
import logging
import asyncio
from PIL import Image
from pathlib import Path
from io import BytesIO
import voyageai
from dotenv import load_dotenv

# Load environment variables but don't rely on settings.py
load_dotenv()
VOYAGE_API_KEY = os.environ.get('VOYAGE_API_KEY')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_frame_embedding")

# Set test frame path directly
TEST_FRAME_PATH = "/home/jason/Videos/screenRecordings/screen_recording_2025_03_03_at_3_39_52_am/frame_000051.jpg"

# Initialize VoyageAI client
voyageai.api_key = VOYAGE_API_KEY
voyage_client = voyageai.Client()

async def generate_embedding(text=None, image=None):
    """Generate an embedding using VoyageAI."""
    try:
        if text and image:
            # Multimodal embedding
            byte_arr = BytesIO()
            image.save(byte_arr, format='JPEG')
            byte_arr = byte_arr.getvalue()
            
            response = voyage_client.embed(
                model="voyage-multimodal-3",
                texts=[text],
                images=[byte_arr]
            )
        elif text:
            # Text-only embedding
            response = voyage_client.embed(
                model="voyage-multimodal-3",
                texts=[text]
            )
        elif image:
            # Image-only embedding
            byte_arr = BytesIO()
            image.save(byte_arr, format='JPEG')
            byte_arr = byte_arr.getvalue()
            
            response = voyage_client.embed(
                model="voyage-multimodal-3",
                images=[byte_arr]
            )
        else:
            raise ValueError("Either text or image (or both) must be provided")
        
        # Extract the embedding
        if "embeddings" in response and len(response["embeddings"]) > 0:
            embedding = response["embeddings"][0]
            return embedding
        else:
            raise ValueError("No embedding returned from VoyageAI API")
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        raise

async def test_frame_embedding():
    """Test loading a frame and generating an embedding."""
    logger.info(f"Testing frame embedding for: {TEST_FRAME_PATH}")
    
    # Check if file exists
    frame_path = Path(TEST_FRAME_PATH)
    if not frame_path.exists():
        logger.error(f"Frame file not found: {TEST_FRAME_PATH}")
        return False
    
    try:
        # Load the image
        logger.info("Loading image...")
        img = Image.open(frame_path)
        
        # Display info
        logger.info(f"Frame loaded successfully!")
        logger.info(f"  Size: {img.size}")
        logger.info(f"  Format: {img.format}")
        logger.info(f"  Mode: {img.mode}")
        
        # Generate text description for the frame
        frame_text = f"Test frame from screen recording. Resolution: {img.size[0]}x{img.size[1]}"
        
        # Generate embedding
        logger.info("Generating embedding...")
        embedding = await generate_embedding(text=frame_text, image=img)
        
        # Show embedding info
        logger.info(f"Embedding generated successfully!")
        logger.info(f"  Embedding dimensions: {len(embedding)}")
        logger.info(f"  First 5 values: {embedding[:5]}")
        
        return True
    except Exception as e:
        logger.error(f"Error in test: {str(e)}")
        return False

if __name__ == "__main__":
    if not VOYAGE_API_KEY:
        logger.error("VOYAGE_API_KEY not set in environment variables.")
        sys.exit(1)
        
    success = asyncio.run(test_frame_embedding())
    if success:
        logger.info("✅ Test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Test failed")
        sys.exit(1) 