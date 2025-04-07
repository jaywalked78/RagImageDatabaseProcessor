"""
Frame description utility that uses OpenAI to generate textual descriptions of frames.

This module enhances frame metadata with:
1. Generated textual descriptions
2. Classification tags
3. Structured metadata
"""
import os
import json
import logging
import asyncio
import base64
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

import aiohttp
import dotenv
from PIL import Image

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class FrameDescriptionGenerator:
    """
    Generate textual descriptions and enhanced metadata for frames using OpenAI.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the frame description generator.
        
        Args:
            api_key: OpenAI API key (default: from env var OPENAI_API_KEY)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API key not provided. Description generation will be unavailable.")
            
        self.api_base = "https://api.openai.com/v1"
        self.session = None
        
        logger.info("Initialized FrameDescriptionGenerator")
    
    async def _ensure_session(self):
        """Ensure an aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            })
        return self.session
    
    async def generate_description(self, 
                                image_path: str, 
                                existing_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a textual description of an image and enhance metadata.
        
        Args:
            image_path: Path to the image file
            existing_metadata: Optional existing metadata to enhance
            
        Returns:
            Dictionary with enhanced metadata including description and tags
        """
        if not self.api_key:
            logger.warning("Cannot generate description: OpenAI API key not configured")
            return existing_metadata or {}
        
        try:
            # Load the image
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return existing_metadata or {}
            
            # Create base metadata structure if not provided
            metadata = existing_metadata or {}
            
            # Extract basic info if not in metadata
            if "frame_name" not in metadata:
                metadata["frame_name"] = os.path.basename(image_path)
            if "folder_name" not in metadata:
                metadata["folder_name"] = os.path.basename(os.path.dirname(image_path))
            
            # Encode image as base64
            encoded_image = await self._encode_image(image_path)
            if not encoded_image:
                return metadata
            
            # Generate description
            description_result = await self._generate_image_description(encoded_image, metadata)
            if not description_result:
                return metadata
            
            # Merge description result with existing metadata
            enhanced_metadata = {**metadata, **description_result}
            
            # Add timestamp if not present
            if "timestamp" not in enhanced_metadata and "creation_time" in metadata:
                enhanced_metadata["timestamp"] = metadata["creation_time"]
            
            # Ensure we have tags
            if "tags" not in enhanced_metadata:
                enhanced_metadata["tags"] = []
            
            # Ensure we have classification_tags
            if "classification_tags" not in enhanced_metadata:
                enhanced_metadata["classification_tags"] = []
            
            logger.info(f"Generated description and enhanced metadata for {image_path}")
            return enhanced_metadata
            
        except Exception as e:
            logger.error(f"Error generating description for {image_path}: {e}")
            return existing_metadata or {}
    
    async def _encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode an image as base64.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64-encoded image or None on error
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            return None
    
    async def _generate_image_description(self, 
                                       encoded_image: str, 
                                       existing_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate a description of an image using OpenAI's API.
        
        Args:
            encoded_image: Base64-encoded image
            existing_metadata: Existing metadata
            
        Returns:
            Dictionary with description and enhanced metadata
        """
        if not self.api_key:
            return None
        
        session = await self._ensure_session()
        
        prompt = self._create_description_prompt(existing_metadata)
        
        # Create API payload
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant that analyzes images and provides detailed descriptions and metadata."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 600
        }
        
        try:
            async with session.post(f"{self.api_base}/chat/completions", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if "choices" in result and result["choices"]:
                        content = result["choices"][0]["message"]["content"]
                        return self._parse_description_response(content)
                    else:
                        logger.error(f"Unexpected response format from OpenAI: {result}")
                else:
                    error_text = await response.text()
                    logger.error(f"OpenAI API error: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
        
        return None
    
    def _create_description_prompt(self, metadata: Dict[str, Any]) -> str:
        """
        Create a prompt for generating a description.
        
        Args:
            metadata: Existing metadata
            
        Returns:
            Prompt string
        """
        prompt = (
            "Analyze this image and provide:\n"
            "1. A detailed description of what's visible in the image (frame_summary)\n"
            "2. A list of descriptive tags (tags)\n"
            "3. A list of classification categories this image belongs to (classification_tags)\n\n"
        )
        
        # Add context from existing metadata
        if metadata:
            prompt += "Here's some context about this image:\n"
            for key, value in metadata.items():
                if key in ["frame_name", "folder_name", "timestamp", "creation_time"]:
                    prompt += f"- {key}: {value}\n"
        
        prompt += (
            "\nOutput ONLY valid JSON containing:\n"
            "- frame_summary: detailed description\n"
            "- tags: array of descriptive tags\n"
            "- classification_tags: array of classification categories\n"
        )
        
        return prompt
    
    def _parse_description_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse the response from OpenAI's API.
        
        Args:
            response_text: Text response from OpenAI
            
        Returns:
            Dictionary with parsed description and tags
        """
        # Default response if parsing fails
        default_response = {
            "frame_summary": "Description not available",
            "tags": [],
            "classification_tags": []
        }
        
        # Try to extract JSON from the response
        try:
            # Find JSON in the response (it might be embedded in markdown code blocks)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}')
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end+1]
                parsed = json.loads(json_text)
                
                # Validate required fields
                if "frame_summary" in parsed:
                    return parsed
                else:
                    # Try to extract description from text if JSON doesn't have required fields
                    return self._extract_description_from_text(response_text)
            else:
                # No JSON found, try to extract description from text
                return self._extract_description_from_text(response_text)
                
        except Exception as e:
            logger.error(f"Error parsing description response: {e}")
            logger.debug(f"Response text: {response_text}")
            
            # Try to extract description from text as fallback
            return self._extract_description_from_text(response_text)
    
    def _extract_description_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract description and tags from plain text.
        
        Args:
            text: Plain text response from OpenAI
            
        Returns:
            Dictionary with extracted description and tags
        """
        result = {
            "frame_summary": "",
            "tags": [],
            "classification_tags": []
        }
        
        lines = text.strip().split('\n')
        
        # Extract description
        description_lines = []
        in_description = False
        
        # Extract tags
        tags = []
        classification_tags = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Check for description
            if "description" in line.lower() or "summary" in line.lower() or "frame_summary" in line.lower():
                in_description = True
                # Extract any text after the colon
                if ':' in line:
                    description_part = line.split(':', 1)[1].strip()
                    if description_part:
                        description_lines.append(description_part)
                continue
                
            # Check for tags section
            if "tags" in line.lower() and "classification" not in line.lower():
                in_description = False
                # Extract tags after the colon
                if ':' in line:
                    tags_part = line.split(':', 1)[1].strip()
                    if tags_part:
                        # Split by commas or other separators
                        extracted_tags = [tag.strip() for tag in tags_part.split(',')]
                        tags.extend([tag for tag in extracted_tags if tag])
                continue
                
            # Check for classification tags
            if "classification" in line.lower() and "tags" in line.lower():
                in_description = False
                # Extract classification tags after the colon
                if ':' in line:
                    tags_part = line.split(':', 1)[1].strip()
                    if tags_part:
                        # Split by commas or other separators
                        extracted_tags = [tag.strip() for tag in tags_part.split(',')]
                        classification_tags.extend([tag for tag in extracted_tags if tag])
                continue
                
            # Add to description if we're in the description section
            if in_description:
                description_lines.append(line)
        
        # Combine description lines
        if description_lines:
            result["frame_summary"] = ' '.join(description_lines)
        else:
            # If no description section found, use the first few lines as description
            result["frame_summary"] = ' '.join(lines[:3])
        
        # Add tags if found
        if tags:
            result["tags"] = tags
            
        # Add classification tags if found
        if classification_tags:
            result["classification_tags"] = classification_tags
        
        return result
    
    async def close(self):
        """Close the session."""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Closed frame description generator session")
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