#!/usr/bin/env python3
"""
Script to chunk frame metadata and OCR data for embedding.

This script processes both frame metadata and OCR data (if available),
chunks the combined content, and saves the chunks for further processing
and embedding.

Usage:
  python chunk_metadata.py --input-file METADATA_FILE --output-dir OUTPUT_DIR [options]

Options:
  --input-file FILE        Path to metadata JSON file
  --output-dir DIR         Directory to save chunks
  --frame-id ID            Frame ID
  --frame-path PATH        Path to frame image
  --ocr-file FILE          Path to OCR structured data JSON file (optional)
  --chunk-size SIZE        Size of chunks (default: 500)
  --chunk-overlap OVERLAP  Overlap between chunks (default: 50)
  --max-chunks MAX         Maximum chunks per frame (default: 10)
"""

import argparse
import json
import os
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import traceback

# Add src to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.chunking import MetadataChunker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load data from a JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return None

def save_chunks(chunks: List[Dict[str, Any]], output_dir: str) -> bool:
    """Save chunks to output directory"""
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Save individual chunks
        for i, chunk in enumerate(chunks):
            chunk_file = os.path.join(output_dir, f"chunk_{i:03d}.json")
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, indent=2)
        
        # Save chunk info
        info_file = os.path.join(output_dir, "chunk_info.json")
        with open(info_file, 'w', encoding='utf-8') as f:
            info = {
                "total_chunks": len(chunks),
                "chunk_files": [f"chunk_{i:03d}.json" for i in range(len(chunks))],
                "has_ocr": any(chunk.get("ocr_data") is not None for chunk in chunks)
            }
            json.dump(info, f, indent=2)
        
        # Save chunks to CSV for easy access and querying
        save_chunks_to_csv(chunks, output_dir)
            
        return True
    except Exception as e:
        logger.error(f"Error saving chunks to {output_dir}: {e}")
        return False

def save_chunks_to_csv(chunks: List[Dict[str, Any]], output_dir: str) -> None:
    """
    Save chunks to CSV file with full OCR data.
    
    Args:
        chunks: List of chunk dictionaries
        output_dir: Directory to save CSV file
    """
    try:
        # Get base storage directory (2 levels up from chunks directory)
        storage_dir = Path(output_dir).parents[1]
        csv_file = storage_dir / "payloads" / "csv" / "frame_chunks.csv"
        
        # Ensure directory exists
        os.makedirs(csv_file.parent, exist_ok=True)
        
        # Get frame_id from the first chunk
        frame_id = chunks[0]["record_id"] if chunks else "unknown"
        
        # Check if CSV exists, create if not
        csv_exists = csv_file.exists()
        
        import csv
        import hashlib
        import json
        from datetime import datetime
        
        # Open in append mode
        with open(csv_file, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # Write header if file is new
            if not csv_exists:
                writer.writerow([
                    "frame_id",
                    "chunk_index",
                    "chunk_text",
                    "processed_time",
                    "chunk_hash",
                    "content_length",
                    "source",
                    "ocr_data",
                    "has_ocr",
                    "is_flagged"
                ])
            
            # Write each chunk
            for i, chunk in enumerate(chunks):
                chunk_text = chunk.get("chunk_text", "")
                
                # Create hash of chunk text
                chunk_hash = hashlib.md5(chunk_text.encode()).hexdigest()
                
                # Get OCR data if available
                ocr_data = chunk.get("ocr_data", {})
                has_ocr = "true" if ocr_data else "false"
                
                # Check if chunk contains flagged OCR data
                is_flagged = "0"
                if ocr_data and ocr_data.get("contains_sensitive_info", False):
                    is_flagged = "1"
                
                # Serialize OCR data to JSON
                ocr_data_json = json.dumps(ocr_data) if ocr_data else ""
                
                # Write row
                writer.writerow([
                    frame_id,
                    i,
                    chunk_text,
                    datetime.now().isoformat(),
                    chunk_hash,
                    len(chunk_text),
                    chunk.get("source", "metadata"),
                    ocr_data_json,
                    has_ocr,
                    is_flagged
                ])
        
        logger.info(f"Saved {len(chunks)} chunks to CSV for frame {frame_id}")
        
    except Exception as e:
        logger.error(f"Error saving chunks to CSV: {e}")
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="Chunk frame metadata and OCR data for embedding")
    parser.add_argument("--input-file", required=True, help="Path to metadata JSON file")
    parser.add_argument("--output-dir", required=True, help="Directory to save chunks")
    parser.add_argument("--frame-id", required=True, help="Frame ID")
    parser.add_argument("--frame-path", required=True, help="Path to frame image")
    parser.add_argument("--ocr-file", help="Path to OCR structured data JSON file")
    parser.add_argument("--chunk-size", type=int, default=500, help="Size of chunks")
    parser.add_argument("--chunk-overlap", type=int, default=50, help="Overlap between chunks")
    parser.add_argument("--max-chunks", type=int, default=10, help="Maximum chunks per frame")
    
    args = parser.parse_args()
    
    # Load metadata
    metadata = load_json_file(args.input_file)
    if not metadata:
        sys.exit(1)
    
    # Load OCR data if available
    ocr_data = None
    if args.ocr_file:
        ocr_data = load_json_file(args.ocr_file)
        logger.info(f"Loaded OCR data from {args.ocr_file}")
    
    # Initialize chunker
    chunker = MetadataChunker(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    
    # Process metadata and OCR data into chunks
    chunks = chunker.process_metadata(
        metadata=metadata,
        record_id=args.frame_id,
        frame_path=args.frame_path,
        ocr_data=ocr_data
    )
    
    # Apply max chunks limit if needed
    if args.max_chunks and len(chunks) > args.max_chunks:
        logger.info(f"Limiting chunks from {len(chunks)} to {args.max_chunks}")
        chunks = chunks[:args.max_chunks]
    
    # Save chunks
    success = save_chunks(chunks, args.output_dir)
    
    if success:
        logger.info(f"Successfully processed {len(chunks)} chunks for frame {args.frame_id}")
        if ocr_data:
            logger.info(f"Chunks include OCR data")
        
        # Create a payload for reference
        payload = chunker.create_metadata_payload(
            chunks=chunks,
            record_id=args.frame_id,
            frame_path=args.frame_path,
            ocr_data=ocr_data
        )
        
        # Save the complete payload for reference
        payload_file = os.path.join(args.output_dir, "payload.json")
        try:
            with open(payload_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
            logger.info(f"Saved payload to {payload_file}")
        except Exception as e:
            logger.error(f"Error saving payload: {e}")
    else:
        logger.error(f"Failed to process chunks for frame {args.frame_id}")
        sys.exit(1)

if __name__ == "__main__":
    main() 