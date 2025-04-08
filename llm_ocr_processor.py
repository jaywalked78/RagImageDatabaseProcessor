#!/usr/bin/env python3
"""
LLM processor for OCR data with sensitive information detection.
Integrates with database to process frames and chunks.
"""

import os
import sys
import logging
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
import asyncpg
import requests

# Import the sensitive information detector
from sensitive_info_detector import process_frame_for_llm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("llm_processor")

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-us-east-1.pooler.supabase.com')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')

# LLM API details (replace with your actual LLM API endpoint)
LLM_API_ENDPOINT = os.getenv('LLM_API_ENDPOINT', 'https://api.example.com/v1/generate')
LLM_API_KEY = os.getenv('LLM_API_KEY')

# Verify environment variables
if not all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
    logger.error("Missing database connection parameters. Please check your .env file.")
    sys.exit(1)

if not LLM_API_KEY:
    logger.warning("LLM API key not set. Will use mock LLM responses.")

async def create_connection_pool():
    """Create a connection pool to the PostgreSQL database."""
    try:
        pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info(f"Successfully connected to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}")
        return pool
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
        sys.exit(1)

async def get_unprocessed_frames(pool, limit=5):
    """
    Retrieve frames that need LLM processing.
    
    Args:
        pool: Database connection pool
        limit: Maximum number of frames to retrieve
        
    Returns:
        List of frame data dictionaries
    """
    async with pool.acquire() as conn:
        # Get frames that have OCR data but no LLM-processed analysis
        frames = await conn.fetch("""
            SELECT f.frame_id, f.ocr_data, f.reference_id
            FROM metadata.frame_details_full f
            WHERE f.ocr_data IS NOT NULL
            AND (f.description IS NULL OR f.description = '' OR f.description LIKE 'Description for%')
            LIMIT $1
        """, limit)
        
        return [dict(frame) for frame in frames]

async def get_unprocessed_chunks(pool, limit=10):
    """
    Retrieve chunks that need LLM processing.
    
    Args:
        pool: Database connection pool
        limit: Maximum number of chunks to retrieve
        
    Returns:
        List of chunk data dictionaries
    """
    async with pool.acquire() as conn:
        # Get chunks that have OCR data but no LLM-processed analysis
        chunks = await conn.fetch("""
            SELECT c.frame_id, c.chunk_id, c.ocr_data, c.reference_id
            FROM metadata.frame_details_chunks c
            WHERE c.ocr_data IS NOT NULL
            AND (c.description IS NULL OR c.description = '' OR c.description LIKE 'Chunk for%')
            LIMIT $1
        """, limit)
        
        return [dict(chunk) for chunk in chunks]

def call_llm_api(text: str, prompt_type: str, metadata: Dict[str, Any] = None) -> str:
    """
    Call the LLM API with the provided text.
    
    Args:
        text: The text to send to the LLM
        prompt_type: Type of prompt ('frame_description', 'frame_summary', 'chunk_analysis')
        metadata: Additional metadata for the LLM
        
    Returns:
        The LLM response text
    """
    # If no API key, return a mock response
    if not LLM_API_KEY:
        return generate_mock_llm_response(text, prompt_type)
    
    # Prepare prompts based on prompt type
    if prompt_type == 'frame_description':
        prompt = """
        Analyze the following text extracted from a screen recording frame using OCR.
        Provide a concise description of what's happening in the frame, including:
        - What application/website is being used
        - What actions the user is taking
        - Any relevant UI elements visible
        - Technical context if apparent (coding, configuration, etc.)
        
        Provide the description in 3-5 sentences, focusing on the key elements.
        """
    elif prompt_type == 'frame_summary':
        prompt = """
        Summarize the key information from this screen recording frame.
        Focus on the most important elements that provide context about the user's task.
        Highlight any technical details, tools being used, or configuration settings visible.
        """
    elif prompt_type == 'chunk_analysis':
        prompt = """
        Analyze this chunk of OCR-extracted text from a screen recording.
        Identify key entities, actions, and technical components visible.
        If code or configuration is present, explain what it's doing.
        Provide a brief technical analysis that would help understand the content.
        """
    else:
        prompt = "Analyze the following text and provide a detailed description."
    
    # Check if sensitive information warning needs to be added
    if metadata and metadata.get("has_sensitive_information"):
        sensitivity_level = metadata.get("sensitive_info_summary", {}).get("alert_level", "low")
        types_detected = metadata.get("sensitive_info_summary", {}).get("types_detected", [])
        
        warning = f"\nNOTE: This content contains potentially sensitive information (level: {sensitivity_level}).\n"
        if types_detected:
            warning += f"Detected info types: {', '.join(types_detected)}.\n"
        warning += "Be careful not to include or reference any specific sensitive values in your response.\n"
        
        prompt = warning + prompt
    
    # Make the actual API call
    try:
        response = requests.post(
            LLM_API_ENDPOINT,
            headers={
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": prompt,
                "text": text,
                "max_tokens": 500,
                "temperature": 0.3
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("text", "")
        else:
            logger.error(f"LLM API error: {response.status_code} - {response.text}")
            return generate_mock_llm_response(text, prompt_type)
            
    except Exception as e:
        logger.error(f"Error calling LLM API: {str(e)}")
        return generate_mock_llm_response(text, prompt_type)

def generate_mock_llm_response(text: str, prompt_type: str) -> str:
    """
    Generate a mock LLM response for testing.
    
    Args:
        text: The input text
        prompt_type: Type of prompt
        
    Returns:
        A mock response
    """
    # Extract some keywords from the text for a somewhat relevant response
    words = text.split()
    keywords = [word for word in words if len(word) > 5][:5]
    keyword_str = ", ".join(keywords) if keywords else "no specific keywords"
    
    if prompt_type == 'frame_description':
        return f"This frame appears to show content related to {keyword_str}. The user seems to be interacting with a software interface or website. Several UI elements are visible, and the user may be configuring or reviewing settings related to these keywords."
    
    elif prompt_type == 'frame_summary':
        return f"Summary of frame content: Contains information about {keyword_str}. The frame shows a user interface with approximately {len(words)} elements of text visible. This appears to be part of a technical workflow involving configuration or data review."
    
    elif prompt_type == 'chunk_analysis':
        return f"Analysis of text chunk: This content focuses on {keyword_str}. The text contains configuration-like elements and possibly technical instructions. There are approximately {len(text)} characters of textual information that would need further interpretation in context."
    
    else:
        return f"Generic analysis of the provided text which contains references to {keyword_str}. Additional context would be required for a more specific analysis."

async def process_frame_with_llm(pool, frame_data: Dict[str, Any]):
    """
    Process a frame with LLM and update the database.
    
    Args:
        pool: Database connection pool
        frame_data: Dictionary with frame data
        
    Returns:
        Success status boolean and message
    """
    frame_id = frame_data['frame_id']
    ocr_text = frame_data['ocr_data']
    reference_id = frame_data['reference_id']
    
    logger.info(f"Processing frame {frame_id} with LLM")
    
    # Check for sensitive information
    sensitive_info_result = process_frame_for_llm(frame_id, ocr_text)
    
    # Use sanitized text if sensitive info was detected
    if sensitive_info_result["contains_sensitive_info"]:
        logger.warning(f"Sensitive information detected in frame {frame_id}")
        text_for_llm = sensitive_info_result["sanitized_text"]
    else:
        text_for_llm = ocr_text
    
    # Get LLM-generated description
    description = call_llm_api(
        text_for_llm, 
        'frame_description', 
        sensitive_info_result.get("llm_metadata")
    )
    
    # Get LLM-generated summary
    summary = call_llm_api(
        text_for_llm, 
        'frame_summary',
        sensitive_info_result.get("llm_metadata")
    )
    
    # Prepare additional metadata
    technical_details = {
        "processed_timestamp": datetime.now().isoformat(),
        "sensitive_info_detected": sensitive_info_result["contains_sensitive_info"],
        "sensitive_info_count": sensitive_info_result["sensitive_info_count"],
        "processing_version": "1.0.0"
    }
    
    # If sensitive info detected, add alert to technical details
    if sensitive_info_result["contains_sensitive_info"]:
        technical_details["sensitive_info_alert"] = sensitive_info_result["llm_metadata"]["sensitive_info_summary"]
    
    # Update database with LLM results
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE metadata.frame_details_full
                SET description = $1,
                    summary = $2,
                    technical_details = $3,
                    workflow_stage = 'llm_processed',
                    tags = ARRAY['llm_processed', 'ocr_analyzed']
                WHERE frame_id = $4
            """, description, summary, json.dumps(technical_details), frame_id)
            
            logger.info(f"Updated frame {frame_id} with LLM-processed data")
            return True, f"Successfully processed frame {frame_id}"
            
    except Exception as e:
        logger.error(f"Error updating frame {frame_id}: {str(e)}")
        return False, f"Error: {str(e)}"

async def process_chunk_with_llm(pool, chunk_data: Dict[str, Any]):
    """
    Process a chunk with LLM and update the database.
    
    Args:
        pool: Database connection pool
        chunk_data: Dictionary with chunk data
        
    Returns:
        Success status boolean and message
    """
    frame_id = chunk_data['frame_id']
    chunk_id = chunk_data['chunk_id']
    ocr_text = chunk_data['ocr_data']
    reference_id = chunk_data['reference_id']
    
    logger.info(f"Processing chunk {chunk_id} from frame {frame_id} with LLM")
    
    # Check for sensitive information
    sensitive_info_result = process_frame_for_llm(chunk_id, ocr_text)
    
    # Use sanitized text if sensitive info was detected
    if sensitive_info_result["contains_sensitive_info"]:
        logger.warning(f"Sensitive information detected in chunk {chunk_id}")
        text_for_llm = sensitive_info_result["sanitized_text"]
    else:
        text_for_llm = ocr_text
    
    # Get LLM-generated analysis for the chunk
    analysis = call_llm_api(
        text_for_llm, 
        'chunk_analysis',
        sensitive_info_result.get("llm_metadata")
    )
    
    # Prepare chunk description and technical details
    description = f"Analysis of chunk {chunk_id} from frame {frame_id}: {analysis[:100]}..."
    
    technical_details = {
        "processed_timestamp": datetime.now().isoformat(),
        "sensitive_info_detected": sensitive_info_result["contains_sensitive_info"],
        "sensitive_info_count": sensitive_info_result["sensitive_info_count"],
        "processing_version": "1.0.0",
        "parent_frame_id": frame_id
    }
    
    # If sensitive info detected, add alert to technical details
    if sensitive_info_result["contains_sensitive_info"]:
        technical_details["sensitive_info_alert"] = sensitive_info_result["llm_metadata"]["sensitive_info_summary"]
    
    # Update database with LLM results
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE metadata.frame_details_chunks
                SET description = $1,
                    summary = $2,
                    technical_details = $3,
                    workflow_stage = 'llm_processed',
                    tags = ARRAY['llm_processed', 'ocr_analyzed']
                WHERE chunk_id = $4
            """, description, analysis, json.dumps(technical_details), chunk_id)
            
            # Also update the process_frames_chunks table to reflect processing status
            await conn.execute("""
                UPDATE metadata.process_frames_chunks
                SET processing_status = 'completed',
                    processing_timestamp = NOW(),
                    processing_metadata = jsonb_set(
                        COALESCE(processing_metadata, '{}'::jsonb),
                        '{llm_processing}',
                        $1::jsonb
                    )
                WHERE chunk_id = $2
            """, json.dumps({"completed": True, "timestamp": datetime.now().isoformat()}), chunk_id)
            
            logger.info(f"Updated chunk {chunk_id} with LLM-processed data")
            return True, f"Successfully processed chunk {chunk_id}"
            
    except Exception as e:
        logger.error(f"Error updating chunk {chunk_id}: {str(e)}")
        return False, f"Error: {str(e)}"

async def main(process_type='both', limit=5):
    """
    Main processing function.
    
    Args:
        process_type: Type of processing ('frames', 'chunks', or 'both')
        limit: Maximum number of items to process
    """
    logger.info(f"Starting LLM processing of {'frames and chunks' if process_type == 'both' else process_type}")
    
    # Create connection pool
    pool = await create_connection_pool()
    
    try:
        # Process frames if requested
        if process_type in ['frames', 'both']:
            frames = await get_unprocessed_frames(pool, limit)
            logger.info(f"Found {len(frames)} unprocessed frames")
            
            for frame in frames:
                success, message = await process_frame_with_llm(pool, frame)
                if not success:
                    logger.error(message)
        
        # Process chunks if requested
        if process_type in ['chunks', 'both']:
            chunks = await get_unprocessed_chunks(pool, limit * 2)  # Process more chunks than frames
            logger.info(f"Found {len(chunks)} unprocessed chunks")
            
            for chunk in chunks:
                success, message = await process_chunk_with_llm(pool, chunk)
                if not success:
                    logger.error(message)
        
        logger.info("Processing complete")
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
    finally:
        # Close connection pool
        await pool.close()
        logger.info("PostgreSQL connection pool closed")

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Process OCR data with LLM")
    parser.add_argument('--type', choices=['frames', 'chunks', 'both'], default='both',
                      help='Type of items to process')
    parser.add_argument('--limit', type=int, default=5,
                      help='Maximum number of items to process')
    
    args = parser.parse_args()
    
    # Run the main function with provided arguments
    asyncio.run(main(args.type, args.limit)) 