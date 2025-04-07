"""
Client for interacting with the Voyage AI multimodal embedding model.
Handles initialization and embedding generation for mixed text/image inputs.
"""

import os
import logging
from typing import List, Union, Dict, Any, Optional, Tuple
from io import BytesIO

import voyageai
from PIL import Image # Required for multimodal input

from src.config.settings import VOYAGE_API_KEY, EMBEDDING_MODEL_NAME, EMBEDDING_DIM

logger = logging.getLogger(__name__)

# Initialize Voyage AI Client
embedding_client: Optional[voyageai.Client] = None
if VOYAGE_API_KEY:
    try:
        voyageai.api_key = VOYAGE_API_KEY
        embedding_client = voyageai.Client()
        logger.info(f"Voyage AI client initialized successfully for model {EMBEDDING_MODEL_NAME}.")
    except ImportError:
        logger.error("Voyage AI library not installed. Please install it: pip install voyageai")
        embedding_client = None
    except Exception as e:
        logger.error(f"Error initializing Voyage AI client: {e}", exc_info=True)
        embedding_client = None
else:
    logger.error("VOYAGE_API_KEY not set. Voyage AI embedding client cannot be initialized.")
    embedding_client = None

def _prepare_single_multimodal_input(text_chunks: List[str], image_data: Optional[bytes] = None) -> Optional[List[Union[str, Image.Image]]]:
    """Prepares a single input sequence for the multimodal_embed function."""
    input_sequence = []
    pil_image = None

    # Try to load image data if provided
    if image_data:
        try:
            pil_image = Image.open(BytesIO(image_data))
            # Optional: Add image preprocessing/resizing here if needed
            # logger.debug(f"Image loaded successfully: format={pil_image.format}, size={pil_image.size}")
        except Exception as img_err:
            logger.error(f"Failed to load image from bytes: {img_err}", exc_info=True)
            # Decide if we should proceed without the image or fail
            pil_image = None # Proceed without image if loading fails
    
    # Construct the input sequence: [image, chunk1, chunk2, ...]
    # Or potentially interleave based on future strategy, but start simple.
    if pil_image:
        input_sequence.append(pil_image)
    
    input_sequence.extend(text_chunks)
    
    if not input_sequence: # Don't send empty inputs
        logger.warning("Prepared multimodal input sequence is empty.")
        return None
        
    return input_sequence

def get_embeddings(inputs: List[Tuple[List[str], Optional[bytes]]]) -> Optional[List[List[float]]]:
    """
    Generates multimodal embeddings for a batch of inputs.

    Args:
        inputs: A list of tuples. Each tuple contains:
                - A list of text chunks associated with the item.
                - Optional image data in bytes for the item.

    Returns:
        A list of embeddings (each a list of floats), or None if an error occurs.
    """
    if not embedding_client:
        logger.error("Voyage AI embedding client not initialized.")
        return None
    if not inputs:
        return []

    prepared_inputs = []
    for text_chunks, image_bytes in inputs:
        single_input = _prepare_single_multimodal_input(text_chunks, image_bytes)
        if single_input: # Only add if preparation was successful
             prepared_inputs.append(single_input)
        else:
             logger.warning("Skipping an item in batch due to input preparation failure.")
             # We need to handle the fact that the output length might not match input length
             # For now, we proceed but this could cause issues if caller expects 1:1 mapping

    if not prepared_inputs:
        logger.error("No valid inputs prepared for batch embedding.")
        return None

    try:
        model_to_use = EMBEDDING_MODEL_NAME
        input_type = "document" # Assuming inputs are documents for retrieval
        
        logger.debug(f"Requesting multimodal batch embeddings for {len(prepared_inputs)} items using model {model_to_use}")
        
        # Call the multimodal_embed function
        result = embedding_client.multimodal_embed(inputs=prepared_inputs, model=model_to_use, input_type=input_type)
        
        if result and result.embeddings:
            num_embeddings = len(result.embeddings)
            logger.debug(f"Received {num_embeddings} embeddings. Total tokens: {result.total_tokens}")
            
            if num_embeddings != len(prepared_inputs):
                 logger.warning(f"Mismatch between number of prepared inputs ({len(prepared_inputs)}) and received embeddings ({num_embeddings}). This might indicate partial failure or API issues.")
            
            # Optional: Dimension check on the first embedding
            if result.embeddings and len(result.embeddings[0]) != EMBEDDING_DIM:
                 logger.warning(f"Warning: Actual embedding dimension ({len(result.embeddings[0])}) differs from configured EMBEDDING_DIM ({EMBEDDING_DIM}). Check model name and config.")
            
            # TODO: Need a strategy to map results back to original inputs if some failed preparation
            # For now, returning the list as is. Caller must be aware of potential length mismatch.
            return result.embeddings
        else:
             logger.error("Voyage AI returned empty or invalid batch multimodal embedding result.")
             return None
             
    except Exception as e:
        logger.error(f"Error generating Voyage AI multimodal batch embeddings: {e}", exc_info=True)
        return None

def get_embedding_dimension() -> int:
    """Returns the configured embedding dimension."""
    return EMBEDDING_DIM

# Note: get_embedding(text, image_data) for single items is removed 
# as the batch function `get_embeddings` handles the primary use case 
# efficiently by accepting a list containing potentially just one item. 