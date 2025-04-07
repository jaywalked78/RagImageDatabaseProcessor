"""
Processes raw metadata and frame data to generate structured metadata and descriptions using Google Gemini.
"""

import os
import logging
import json
import base64
from typing import Dict, Any, Optional

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image # Keep PIL for potential image handling within this module
from io import BytesIO

from src.config.settings import LLM_MODEL_NAME, GOOGLE_API_KEY

logger = logging.getLogger(__name__)

# Configure Google Gemini Client
llm_client = None
gemini_model = None
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        # Initialize the specific model we intend to use
        gemini_model = genai.GenerativeModel(LLM_MODEL_NAME)
        logger.info(f"Google Gemini client configured successfully for model {LLM_MODEL_NAME}.")
        # TODO: Add a check here to see if the model supports vision input if possible via SDK
        
    except ImportError:
        logger.error("google-generativeai library not installed. Please install it: pip install google-generativeai")
    except Exception as e:
        logger.error(f"Error configuring Google Gemini client: {e}", exc_info=True)
        gemini_model = None
else:
    logger.warning("GOOGLE_API_KEY not set. Google Gemini client cannot be configured.")

def _prepare_gemini_multimodal_prompt(frame_data_bytes: bytes, raw_metadata: Dict[str, Any], airtable_id: str, frame_path_rel: str) -> list:
    """ Prepares the list of content parts for the Gemini API call. """
    
    # Convert raw metadata to a string format suitable for the prompt
    # Avoid excessive length, focus on key fields
    metadata_str = json.dumps(raw_metadata, indent=2, sort_keys=True, default=str)
    # Limit metadata length if necessary
    max_meta_len = 1000 
    if len(metadata_str) > max_meta_len:
        metadata_str = metadata_str[:max_meta_len] + "... (truncated)"

    # Prepare the prompt text
    prompt_text = f"""Analyze the provided frame image and its raw metadata.
Generate a concise text summary describing the visual content of the image.
Extract key objects or entities visible in the frame.
Analyze the raw metadata fields provided below.

Raw Metadata (from Airtable record {airtable_id}, path {frame_path_rel}):
```json
{metadata_str}
```

Based on both the visual content and raw metadata, structure the information into a JSON object.
Include the following keys in the JSON:
- frame_summary: Your generated textual description of the visual content.
- classification_tags: A list of relevant semantic tags (e.g., indoor, outdoor, meeting, presentation, code, diagram, person, vehicle, document, ui_screenshot).
- key_objects: A list of key objects/entities identified in the image.
- cleaned_metadata: A dictionary containing cleaned or extracted key fields from the raw metadata (e.g., a formatted timestamp, a specific tool name if identified, main subject).

Output ONLY the raw JSON object, without any markdown formatting (like ```json) surrounding it.
"""

    # Prepare image part
    image_part = None
    if frame_data_bytes:
        try:
            # Check image format and convert if necessary (Gemini prefers JPEG, PNG, WEBP, HEIC, HEIF)
            img = Image.open(BytesIO(frame_data_bytes))
            # Simple format check/conversion example
            if img.format not in ['JPEG', 'PNG', 'WEBP', 'HEIC', 'HEIF']:
                logger.warning(f"Image format {img.format} not directly supported by Gemini, attempting conversion to PNG.")
                output_buffer = BytesIO()
                img.save(output_buffer, format='PNG')
                frame_data_bytes = output_buffer.getvalue()
                mime_type = "image/png"
            else:
                 # Get appropriate mime type
                 mime_type = Image.MIME.get(img.format)
                 if not mime_type:
                     logger.warning(f"Could not determine MIME type for format {img.format}, defaulting to image/png")
                     mime_type = "image/png"
            
            image_part = {
                "mime_type": mime_type,
                "data": frame_data_bytes # Send raw bytes
            }
        except Exception as img_err:
            logger.error(f"Failed to prepare image for Gemini prompt: {img_err}", exc_info=True)
            image_part = None # Proceed without image if preparation fails

    # Construct the prompt list
    prompt_parts = [prompt_text]
    if image_part:
        prompt_parts.insert(0, image_part) # Prepend image data as per Gemini examples
        
    return prompt_parts

def generate_structured_metadata(frame_data_bytes: bytes, raw_metadata: Dict[str, Any], airtable_id: str, frame_path_rel: str) -> Dict[str, Any]:
    """
    Uses Google Gemini to analyze frame image bytes and raw metadata, returning structured JSON.

    Args:
        frame_data_bytes: The frame image data as bytes.
        raw_metadata: Metadata dictionary fetched from Airtable.
        airtable_id: The Airtable record ID.
        frame_path_rel: The relative path of the frame file.

    Returns:
        A dictionary containing structured metadata, including LLM-generated fields
        and source tracking information.
    """
    fallback_result = {
        "frame_summary": "LLM processing failed or not available.",
        "classification_tags": [],
        "key_objects": [],
        "cleaned_metadata": raw_metadata, # Passthrough raw metadata
        "source_airtable_id": airtable_id,
        "source_frame_path": frame_path_rel,
        "raw_airtable_metadata": raw_metadata 
    }
    
    if not gemini_model:
        logger.warning(f"Gemini model not available. Returning basic metadata structure for {airtable_id}.")
        return fallback_result
        
    try:
        prompt_parts = _prepare_gemini_multimodal_prompt(frame_data_bytes, raw_metadata, airtable_id, frame_path_rel)
        
        logger.debug(f"Sending request to Gemini model {LLM_MODEL_NAME} for Airtable ID: {airtable_id}")
        
        # Configure safety settings to be less restrictive if needed, otherwise use defaults
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Specify JSON output mode if available and desired (check SDK updates)
        # generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
        
        response = gemini_model.generate_content(
            prompt_parts, 
            safety_settings=safety_settings,
            # generation_config=generation_config # Add if using JSON mode
            stream=False
        )

        # Check for blocked content before accessing text
        if not response.candidates:
             logger.error(f"Gemini response blocked for Airtable ID {airtable_id}. Block reason: {response.prompt_feedback.block_reason}")
             # Add more detailed logging of feedback if needed
             # logger.error(f"Full prompt feedback: {response.prompt_feedback}")
             return fallback_result # Return fallback on blocked prompt

        if response.candidates[0].finish_reason != 1: # 1 == STOP
             logger.error(f"Gemini generation stopped for unexpected reason: {response.candidates[0].finish_reason} for {airtable_id}")
             # logger.error(f"Safety ratings: {response.candidates[0].safety_ratings}")
             return fallback_result # Return fallback if generation didn't complete normally

        response_text = response.text
        logger.debug(f"Raw Gemini response text for {airtable_id}: {response_text[:200]}...")
        
        # Attempt to parse the response text as JSON
        try:
            # Clean potential markdown fences if JSON mode wasn't used/available
            if response_text.strip().startswith("```json"):
                response_text = response_text.strip()[7:-3].strip()
            elif response_text.strip().startswith("```"):
                 response_text = response_text.strip()[3:-3].strip()
                 
            structured_metadata = json.loads(response_text)
            logger.info(f"Successfully generated and parsed structured metadata for Airtable ID: {airtable_id}")

            # Ensure source fields are present
            structured_metadata['source_airtable_id'] = airtable_id
            structured_metadata['source_frame_path'] = frame_path_rel
            # Add original raw metadata for reference
            structured_metadata['raw_airtable_metadata'] = raw_metadata 
            
            return structured_metadata
            
        except json.JSONDecodeError as json_err:
            logger.error(f"Failed to decode JSON response from Gemini for {airtable_id}: {json_err}")
            logger.error(f"LLM Response Text was: {response_text}")
            # Store the raw text in the summary if parsing fails?
            fallback_result["frame_summary"] = f"LLM JSON parsing failed. Raw response: {response_text[:500]}..."
            return fallback_result
        
    except Exception as e:
        logger.error(f"Gemini processing failed for Airtable ID {airtable_id}: {e}", exc_info=True)
        return fallback_result

def create_text_representation_for_embedding(metadata: Dict[str, Any]) -> str:
    """
    Creates a single text string from structured metadata suitable for embedding.
    Includes key fields identified as important for semantic meaning.

    Args:
        metadata: The structured metadata dictionary.

    Returns:
        A string concatenating important metadata fields.
    """
    # Select fields strategically for embedding (Ref #35, #40)
    text_parts = []
    text_parts.append(f"Frame Summary: {metadata.get('frame_summary', '')}")
    text_parts.append(f"Tags: {', '.join(metadata.get('classification_tags', []))}")
    text_parts.append(f"Key Objects: {', '.join(metadata.get('key_objects', []))}")
    
    # Add selected cleaned metadata fields (Example)
    cleaned = metadata.get('cleaned_metadata', {})
    if isinstance(cleaned, dict): # Ensure cleaned_metadata is a dict
        if 'title' in cleaned:
            text_parts.append(f"Title: {cleaned['title']}")
        if 'timestamp' in cleaned: # Assuming timestamp is cleaned/formatted
             text_parts.append(f"Timestamp: {cleaned['timestamp']}")
        # Add other relevant cleaned fields based on your LLM output
        if 'tool_name' in cleaned: 
             text_parts.append(f"Tool Identified: {cleaned['tool_name']}")
    elif isinstance(cleaned, str): # Handle case where LLM might return string
         text_parts.append(f"Cleaned Info: {cleaned}")

    # Filter out empty/None parts and join
    return "\n".join(filter(lambda x: x is not None and x.split(':', 1)[-1].strip(), text_parts)) 