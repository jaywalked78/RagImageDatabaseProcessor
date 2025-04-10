#!/usr/bin/env python3
"""
Process JSON Files Script

This script:
1. Finds JSON files in a specified folder
2. Processes each file using semantic chunking based on markdown headers
3. Organizes data into a structured format for n8n processing
4. Sends the processed data to a webhook (test or production)

Usage:
    python process_json_files.py --folder <folder_name> [--test] [--file <specific_file>]
"""

import os
import sys
import json
import glob
import argparse
import logging
import requests
import traceback
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure logs and data directories exist
Path("logs").mkdir(exist_ok=True, parents=True)
Path("data").mkdir(exist_ok=True, parents=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/process_json.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get configuration from environment variables
TEST_WEBHOOK_URL = os.getenv("TEST_WEBHOOK_URL", "")
PRODUCTION_WEBHOOK_URL = os.getenv("PRODUCTION_WEBHOOK_URL", "")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))  # Default chunk size in characters
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))  # Default overlap in characters
TOKEN_CHUNK_SIZE = int(os.getenv("TOKEN_CHUNK_SIZE", "400"))  # Default chunk size in tokens
TOKEN_CHUNK_OVERLAP = int(os.getenv("TOKEN_CHUNK_OVERLAP", "40"))  # Default overlap in tokens
FRAME_BASE_DIR = os.getenv("FRAME_BASE_DIR", "")

# Validate essential environment variables
if not FRAME_BASE_DIR:
    logger.error("FRAME_BASE_DIR not set in environment variables")
    sys.exit(1)

if not TEST_WEBHOOK_URL or not PRODUCTION_WEBHOOK_URL:
    logger.warning("TEST_WEBHOOK_URL or PRODUCTION_WEBHOOK_URL not set in environment")

def normalize_folder_name(folder_name: str) -> str:
    """
    Remove '_frames' suffix from folder name if present.
    """
    if folder_name and folder_name.endswith('_frames'):
        return folder_name[:-7]  # Remove the '_frames' suffix
    return folder_name

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load a JSON file and return its contents as a dictionary"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {e}")
        return {}

def structure_metadata(metadata: Dict[str, Any], frame_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Process raw metadata into a structured format for easier retrieval.
    
    Args:
        metadata: Raw metadata dictionary
        frame_path: Path to the frame image (optional)
        
    Returns:
        Structured metadata dictionary
    """
    structured = {}
    
    # Keep track of source information
    # Look for the record ID in various possible fields
    record_id = metadata.get("RecordID", "")
    if not record_id:
        record_id = metadata.get("id", "")
    structured["airtable_record_id"] = record_id
    
    structured["frame_path"] = str(frame_path) if frame_path else ""
    
    # Extract frame summary (use existing Summary field for now)
    structured["frame_summary"] = metadata.get("Summary", "")
    
    # Extract key fields with clean names
    field_mappings = {
        "Timestamp": "timestamp",
        "ToolsVisible": "tools_visible",
        "ActionsDetected": "actions_detected",
        "TechnicalDetails": "technical_details",
        "OCRData": "ocr_data",
        "StageOfWork": "stage_of_work",
        "FrameNumber": "frame_number",
        "FolderName": "folder_name",
        "RelationshipToPrevious": "context_relationship"
    }
    
    # Copy fields with cleaned names
    for original, clean in field_mappings.items():
        if original in metadata and metadata[original]:
            structured[clean] = metadata[original]
    
    return structured

def create_text_representation(structured_metadata: Dict[str, Any]) -> str:
    """
    Create a coherent text representation from structured metadata.
    
    Args:
        structured_metadata: Structured metadata dictionary
        
    Returns:
        Formatted text string optimized for semantic chunking
    """
    text = []
    
    # Add frame summary as a prominent first section
    if "frame_summary" in structured_metadata and structured_metadata["frame_summary"]:
        text.append(f"# Frame Summary\n{structured_metadata['frame_summary']}\n")
    
    # Add main contextual information
    context_section = []
    
    if "timestamp" in structured_metadata:
        context_section.append(f"Timestamp: {structured_metadata['timestamp']}")
    
    if "stage_of_work" in structured_metadata:
        context_section.append(f"Stage: {structured_metadata['stage_of_work']}")
    
    if "tools_visible" in structured_metadata:
        context_section.append(f"Tools Visible: {structured_metadata['tools_visible']}")
    
    if "actions_detected" in structured_metadata:
        context_section.append(f"Actions Detected: {structured_metadata['actions_detected']}")
    
    if "context_relationship" in structured_metadata:
        context_section.append(f"Context: {structured_metadata['context_relationship']}")
    
    if context_section:
        text.append("## Context\n" + "\n".join(context_section) + "\n")
    
    # Add technical details as a separate section
    if "technical_details" in structured_metadata and structured_metadata["technical_details"]:
        text.append(f"## Technical Details\n{structured_metadata['technical_details']}\n")
    
    # Add OCR data as a separate section
    if "ocr_data" in structured_metadata and structured_metadata["ocr_data"]:
        text.append(f"## Screen Content (OCR)\n{structured_metadata['ocr_data']}\n")
    
    # Add source information
    source_info = []
    if "airtable_record_id" in structured_metadata:
        source_info.append(f"Airtable ID: {structured_metadata['airtable_record_id']}")
    
    if "frame_path" in structured_metadata:
        source_info.append(f"Frame Path: {structured_metadata['frame_path']}")
    
    if source_info:
        text.append("## Source\n" + "\n".join(source_info))
    
    return "\n\n".join(text)

def simple_chunk_text(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Simple fallback chunker if advanced chunking fails."""
    if not text:
        return []
        
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        if end < text_length and end - start == chunk_size:
            # Find the last space in the chunk to avoid cutting words
            last_space = text[start:end].rfind(' ')
            if last_space != -1:
                end = start + last_space + 1
        
        chunks.append(text[start:end].strip())
        start = end - chunk_overlap if end - chunk_overlap > start else end
    
    return chunks

def semantic_chunk_text(text: str, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP) -> List[Dict[str, Any]]:
    """
    Split text based on Markdown headers, with token-based secondary splitting for large sections.
    Returns chunks with metadata about which section they belong to.
    
    Args:
        text: Text to split into chunks
        chunk_size: Maximum chunk size in characters (for secondary splitting fallback)
        chunk_overlap: Amount of overlap between chunks (for secondary splitting fallback)
        
    Returns:
        List of dictionaries with chunk text and metadata
    """
    if not text:
        return []
    
    try:
        # Try to import required libraries
        try:
            from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
            has_langchain = True
        except ImportError:
            logger.warning("langchain not installed. Falling back to simple chunking.")
            has_langchain = False
            
        # If we don't have langchain, use the simple chunker
        if not has_langchain:
            return [{"text": chunk, "metadata": {}} for chunk in simple_chunk_text(text, chunk_size, chunk_overlap)]
        
        # Define headers to split on
        headers_to_split_on = [
            ("#", "header_1"),     # Frame Summary (H1)
            ("##", "header_2"),    # Context, Technical Details, etc. (H2)
        ]
        
        # Create markdown splitter
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        
        # Split by headers first
        header_splits = markdown_splitter.split_text(text)
        
        # For token-based secondary splitting
        try:
            import tiktoken
            has_tiktoken = True
            encoding = tiktoken.get_encoding("cl100k_base")  # Good general-purpose tokenizer
            
            # Function to count tokens
            def token_counter(text):
                return len(encoding.encode(text))
            
            # Create token-based splitter for oversized sections
            recursive_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                encoding_name="cl100k_base",
                chunk_size=TOKEN_CHUNK_SIZE,
                chunk_overlap=TOKEN_CHUNK_OVERLAP,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
        except ImportError:
            # Fall back to character-based if tiktoken is not available
            logger.warning("tiktoken not available, falling back to character-based splitting")
            has_tiktoken = False
            recursive_splitter = RecursiveCharacterTextSplitter(
                separators=["\n\n", "\n", ". ", " ", ""],
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len
            )
        
        # Process each header section
        final_chunks = []
        for chunk_doc in header_splits:
            # Extract header information
            section_content = chunk_doc.page_content
            metadata = chunk_doc.metadata
            header_1 = metadata.get("header_1", "")
            header_2 = metadata.get("header_2", "")
            
            # Determine section title and level
            section_title = header_2 if header_2 else header_1
            header_level = 2 if header_2 else 1
            header_prefix = "#" * header_level
            
            # Check if secondary splitting is needed
            needs_splitting = False
            if has_tiktoken:
                if token_counter(section_content) > TOKEN_CHUNK_SIZE:
                    needs_splitting = True
            else:
                # Fall back to character length
                if len(section_content) > chunk_size:
                    needs_splitting = True
            
            if not needs_splitting:
                # If the section is small enough, keep it as one chunk
                section_text = f"{header_prefix} {section_title}\n{section_content}"
                final_chunks.append({
                    "text": section_text.strip(),
                    "metadata": {
                        "header_1": header_1,
                        "header_2": header_2,
                        "is_subsection": False
                    }
                })
            else:
                # Section is too large, apply secondary splitting
                logger.info(f"Applying secondary splitting to large section: {section_title}")
                sub_chunks = recursive_splitter.split_text(section_content)
                
                for i, sub_chunk in enumerate(sub_chunks):
                    # Include the header in each sub-chunk for context
                    sub_section_text = f"{header_prefix} {section_title} (Part {i+1}/{len(sub_chunks)})\n{sub_chunk}"
                    final_chunks.append({
                        "text": sub_section_text.strip(),
                        "metadata": {
                            "header_1": header_1,
                            "header_2": header_2,
                            "is_subsection": True,
                            "subsection_index": i,
                            "subsection_total": len(sub_chunks)
                        }
                    })
        
        return final_chunks
    
    except Exception as e:
        logger.error(f"Error in semantic_chunk_text: {str(e)}")
        logger.error(traceback.format_exc())
        # Fall back to simple chunking
        return [{"text": chunk, "metadata": {}} for chunk in simple_chunk_text(text, chunk_size, chunk_overlap)]

def get_frame_image_path(folder_name: str, frame_number: str) -> Optional[Path]:
    """
    Get the path to the frame image in the base directory.
    
    Args:
        folder_name: Name of the folder containing the frame
        frame_number: Frame number/name
        
    Returns:
        Path to the frame image or None if not found
    """
    # Normalize folder name
    folder_name = normalize_folder_name(folder_name)
    
    # Construct base folder path
    base_folder_path = Path(FRAME_BASE_DIR) / folder_name
    
    if not base_folder_path.exists():
        logger.error(f"Frame folder not found: {base_folder_path}")
        return None
    
    logger.info(f"Looking for frame in location: {base_folder_path}")
    
    # Try different extensions for the frame image
    extensions = ['.jpg', '.jpeg', '.png']
    
    for ext in extensions:
        # Try exact match first
        frame_path = base_folder_path / f"{frame_number}{ext}"
        if frame_path.exists():
            logger.info(f"Found frame image at: {frame_path}")
            return frame_path
        
        # Try with common frame name patterns
        patterns = [
            f"{frame_number}{ext}",
            f"frame_{frame_number}{ext}",
            f"frame_{frame_number.zfill(6)}{ext}"
        ]
        
        for pattern in patterns:
            for file_path in base_folder_path.glob(pattern):
                logger.info(f"Found frame image at: {file_path}")
                return file_path
    
    logger.error(f"Frame image not found for {folder_name}/{frame_number}")
    return None

def process_json_file(file_path: Path, test_mode: bool = False) -> Dict[str, Any]:
    """
    Process a JSON file:
    1. Extract metadata
    2. Structure the metadata
    3. Create a semantic text representation
    4. Chunk the text using header-based semantic chunking
    5. Structure the output with nested arrays and section metadata
    
    Args:
        file_path: Path to the JSON file
        test_mode: Whether to run in test mode
        
    Returns:
        Dictionary with processed data including chunks
    """
    data = load_json_file(file_path)
    if not data:
        logger.error(f"Failed to load JSON data from {file_path}")
        return {}
    
    # Extract relevant fields
    folder_path = data.get("folder_path", "")
    file_name = data.get("file_name", "")
    metadata = data.get("metadata", {})
    content = data.get("content", "")
    
    # Extract folder and frame names
    folder_name = Path(folder_path).name if folder_path else ""
    frame_number = Path(file_name).stem if file_name else ""
    
    # Normalize folder name
    folder_name = normalize_folder_name(folder_name)
    
    # Check if we have necessary information
    if not folder_name or not frame_number:
        logger.error(f"Missing folder_name or frame_number in {file_path}")
        return {}
    
    logger.info(f"Processing frame: {folder_name}/{frame_number}")
    
    # Get the frame image path for multimodal processing
    frame_image_path = get_frame_image_path(folder_name, frame_number)
    
    # Structure the metadata
    logger.info("Structuring metadata")
    structured_metadata = structure_metadata(metadata, frame_image_path)
    
    # Create semantic text representation
    logger.info("Creating text representation")
    text_to_chunk = create_text_representation(structured_metadata)
    
    # Chunk the text using our enhanced semantic chunking
    logger.info("Chunking text using semantic header-based chunking")
    # Fixed: Using semantic_chunk_text function instead of variable with same name as function
    chunks_with_metadata = semantic_chunk_text(text_to_chunk, CHUNK_SIZE, CHUNK_OVERLAP)
    logger.info(f"Created {len(chunks_with_metadata)} semantically meaningful chunks from {file_path}")
    
    # Process each chunk
    all_chunks = []
    for i, chunk_info in enumerate(chunks_with_metadata):
        chunk_text = chunk_info["text"]
        chunk_metadata = chunk_info["metadata"]
        
        all_chunks.append({
            "id": f"{folder_name}_{frame_number}_chunk_{i}",
            "chunk_index": i,
            "text": chunk_text,
            "section_metadata": chunk_metadata  # Include section metadata for retrieval context
        })
    
    # Create the frame result with the new structure
    frame_result = {
        "id": f"{folder_name}_{frame_number}",
        "folder_name": folder_name,
        "file_name": file_name,
        "frame_number": frame_number,
        "frame_image_path": str(frame_image_path) if frame_image_path else "",
        "metadata": structured_metadata,  # Use the structured metadata
        "raw_metadata": metadata,  # Keep the original metadata for reference
        "content": content,
        "chunks": all_chunks,
        "processed_at": datetime.now().isoformat(),
        "test_mode": test_mode
    }
    
    logger.info(f"Completed processing of {file_path}")
    return frame_result

def send_to_webhook(data: Dict[str, Any], test_mode: bool = False) -> bool:
    """
    Send processed data to webhook.
    
    Args:
        data: Data to send
        test_mode: Whether to use test webhook
        
    Returns:
        Success status (True/False)
    """
    webhook_url = TEST_WEBHOOK_URL if test_mode else PRODUCTION_WEBHOOK_URL
    
    if not webhook_url:
        logger.error(f"{'TEST' if test_mode else 'PRODUCTION'}_WEBHOOK_URL not set")
        return False
    
    try:
        logger.info(f"Sending data to {'test' if test_mode else 'production'} webhook: {webhook_url}")
        
        response = requests.post(
            webhook_url,
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in (200, 201, 202):
            logger.info(f"Successfully sent data to webhook: {response.status_code}")
            return True
        else:
            logger.error(f"Error sending data to webhook: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Exception sending data to webhook: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def find_json_files(folder_name: str) -> List[Path]:
    """
    Find JSON files for a specific folder in the data directory.
    
    Args:
        folder_name: Folder name to filter by
        
    Returns:
        List of paths to JSON files
    """
    # Normalize folder name
    normalized_name = normalize_folder_name(folder_name)
    
    # Define possible folder paths
    possible_folders = [
        Path("data") / normalized_name,  # Without '_frames'
        Path("data") / f"{normalized_name}_frames"  # With '_frames'
    ]
    
    files = []
    for folder_path in possible_folders:
        if folder_path.exists():
            logger.info(f"Looking for JSON files in {folder_path}")
            pattern = str(folder_path / "*.json")
            folder_files = [Path(p) for p in glob.glob(pattern)]
            files.extend(folder_files)
            
    if not files:
        logger.error(f"No JSON files found for folder {folder_name}")
        
    logger.info(f"Found {len(files)} JSON files for folder {folder_name}")
    return files

def process_folder(folder_name: str, test_mode: bool = False) -> Dict[str, Any]:
    """
    Process all JSON files in a specific folder.
    
    Args:
        folder_name: Name of the folder to process
        test_mode: Whether to run in test mode
        
    Returns:
        Summary of processing results
    """
    # Get JSON files for the folder
    files = find_json_files(folder_name)
    
    if not files:
        logger.error(f"No files found for folder {folder_name}")
        return {
            "status": "error",
            "message": f"No files found for folder {folder_name}",
            "folder_name": folder_name,
            "timestamp": datetime.now().isoformat()
        }
    
    # Initialize result arrays - frames
    frames = []
    
    # Process each file
    processed_count = 0
    error_count = 0
    
    for file_path in files:
        try:
            logger.info(f"Processing file {file_path}")
            
            # Process the file
            result = process_json_file(file_path, test_mode)
            
            if not result:
                logger.error(f"Failed to process {file_path}")
                error_count += 1
                continue
                
            # Add the frame to our frames array
            frames.append(result)
            
            processed_count += 1
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            logger.error(traceback.format_exc())
            error_count += 1
    
    # Create the final output structure
    output = {
        "folder_name": folder_name,
        "processed_at": datetime.now().isoformat(),
        "test_mode": test_mode,
        "frames": frames,
        "stats": {
            "total_files": len(files),
            "processed": processed_count,
            "errors": error_count
        }
    }
    
    # Send to webhook if we have frames
    if frames:
        logger.info(f"Sending {len(frames)} frames to webhook")
        send_to_webhook(output, test_mode)
    else:
        logger.warning("No frames to send to webhook")
    
    return output

def process_specific_file(folder_name: str, file_path: str, test_mode: bool = False) -> Dict[str, Any]:
    """
    Process a specific JSON file.
    
    Args:
        folder_name: Name of the folder (context only)
        file_path: Path to the JSON file
        test_mode: Whether to run in test mode
        
    Returns:
        Processing result
    """
    # Check if file exists
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {file_path}")
        return {
            "status": "error",
            "message": f"File not found: {file_path}",
            "folder_name": folder_name,
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        logger.info(f"Processing specific file: {file_path}")
        
        # Process the file
        result = process_json_file(path, test_mode)
        
        if not result:
            logger.error(f"Failed to process {file_path}")
            return {
                "status": "error",
                "message": f"Failed to process {file_path}",
                "folder_name": folder_name,
                "timestamp": datetime.now().isoformat()
            }
        
        # Create the output with just this frame
        output = {
            "folder_name": folder_name,
            "processed_at": datetime.now().isoformat(),
            "test_mode": test_mode,
            "frames": [result],
            "stats": {
                "total_files": 1,
                "processed": 1,
                "errors": 0
            }
        }
        
        # Send to webhook
        logger.info("Sending frame to webhook")
        send_to_webhook(output, test_mode)
        
        return output
        
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": f"Error processing {file_path}: {str(e)}",
            "folder_name": folder_name,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Process JSON files in a folder')
    parser.add_argument('--folder', '-f', required=True, help='Folder name to process')
    parser.add_argument('--test', '-t', action='store_true', help='Run in test mode')
    parser.add_argument('--file', help='Process a specific file')
    
    args = parser.parse_args()
    
    logger.info(f"Starting processing with arguments: {args}")
    
    # Process specific file or entire folder
    if args.file:
        result = process_specific_file(args.folder, args.file, args.test)
    else:
        result = process_folder(args.folder, args.test)
    
    logger.info(f"Processing complete: {result.get('stats', {})}")
    return result

if __name__ == "__main__":
    main()