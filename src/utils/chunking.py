#!/usr/bin/env python3
"""
Utility functions for chunking text into manageable pieces for processing and embedding.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import os
import json
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter, TokenTextSplitter

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DEFAULT_CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', '500'))
DEFAULT_CHUNK_OVERLAP = int(os.environ.get('CHUNK_OVERLAP', '50'))

class MetadataChunker:
    """Class for chunking frame metadata into processable pieces for embedding."""
    
    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP):
        """
        Initialize the metadata chunker.
        
        Args:
            chunk_size: Size of chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize the text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        
        logger.info(f"Using LangChain RecursiveCharacterTextSplitter with chunk_size={chunk_size}, overlap={chunk_overlap}")
    
    def create_text_representation(self, metadata: Dict[str, Any], ocr_data: Dict[str, Any] = None) -> str:
        """
        Create a single text representation from frame metadata and OCR data.
        
        Args:
            metadata: Dictionary of frame metadata
            ocr_data: Dictionary of OCR data (optional)
            
        Returns:
            Text representation of the metadata and OCR
        """
        # Extract key fields
        frame_number = metadata.get('FrameNumber', '')
        folder_name = metadata.get('FolderName', '')
        summary = metadata.get('Summary', '')
        actions = metadata.get('ActionsDetected', '')
        stage = metadata.get('StageOfWork', '')
        details = metadata.get('TechnicalDetails', '')
        relationship = metadata.get('RelationshipToPrevious', '')
        
        # Create text representation
        text = f"Frame {frame_number} from {folder_name}\n\n"
        
        if summary:
            text += f"Summary: {summary}\n\n"
        
        if actions:
            text += f"Actions: {actions}\n\n"
        
        if stage:
            text += f"Stage: {stage}\n\n"
        
        if details:
            text += f"Technical Details: {details}\n\n"
        
        if relationship:
            text += f"Relationship to Previous: {relationship}\n\n"
        
        # Add any other fields that might be useful
        for key, value in metadata.items():
            if key not in ['FrameNumber', 'FolderName', 'Summary', 'ActionsDetected', 
                          'StageOfWork', 'TechnicalDetails', 'RelationshipToPrevious']:
                if value and isinstance(value, (str, int, float, bool)):
                    text += f"{key}: {value}\n\n"
        
        # Add OCR data if available
        if ocr_data:
            text += "OCR TEXT:\n"
            
            # Add raw OCR text if available
            if 'raw_text' in ocr_data and ocr_data['raw_text']:
                text += f"{ocr_data['raw_text']}\n\n"
            
            # Add structured OCR data
            if 'topics' in ocr_data and ocr_data['topics']:
                text += f"OCR Topics: {', '.join(ocr_data['topics'])}\n\n"
                
            if 'content_types' in ocr_data and ocr_data['content_types']:
                text += f"OCR Content Types: {', '.join(ocr_data['content_types'])}\n\n"
                
            if 'urls' in ocr_data and ocr_data['urls']:
                text += f"OCR URLs: {', '.join(ocr_data['urls'])}\n\n"
                
            if 'paragraphs' in ocr_data and ocr_data['paragraphs']:
                text += f"OCR Text Content: {' '.join(ocr_data['paragraphs'])}\n\n"
        
        return text
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        chunks = self.text_splitter.split_text(text)
        logger.info(f"Split text into {len(chunks)} chunks using LangChain")
        return chunks
    
    def process_metadata(self, metadata: Dict[str, Any], 
                        record_id: str, 
                        frame_path: str,
                        ocr_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Process metadata and OCR data into chunks.
        
        Args:
            metadata: Dictionary of frame metadata
            record_id: ID of the record in the database
            frame_path: Path to the frame file
            ocr_data: Dictionary of OCR data (optional)
            
        Returns:
            List of chunk dictionaries
        """
        # Create text representation with OCR data if available
        text = self.create_text_representation(metadata, ocr_data)
        
        # Split text into chunks
        text_chunks = self.split_text(text)
        
        # Create chunk dictionaries
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            chunk = {
                "chunk_sequence_id": i,
                "chunk_text": chunk_text,
                "record_id": record_id,
                "frame_path": frame_path,
                "metadata": metadata,
                "ocr_data": ocr_data,
                "total_chunks": len(text_chunks),
                "source": "metadata_with_ocr" if ocr_data else "metadata"
            }
            chunks.append(chunk)
        
        return chunks
    
    def create_metadata_payload(self, chunks: List[Dict[str, Any]], 
                               record_id: str, 
                               frame_path: str,
                               ocr_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create a payload for storing metadata, OCR data, and chunks.
        
        Args:
            chunks: List of chunk dictionaries
            record_id: ID of the record in the database
            frame_path: Path to the frame file
            ocr_data: Dictionary of OCR data (optional)
            
        Returns:
            Payload dictionary
        """
        return {
            "record_id": record_id,
            "frame_path": frame_path,
            "chunks": chunks,
            "chunk_count": len(chunks),
            "ocr_data": ocr_data,
            "has_ocr": ocr_data is not None,
            "timestamp": os.path.getmtime(frame_path) if os.path.exists(frame_path) else None
        }

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks of specified size.
    
    Args:
        text: The text to split into chunks
        chunk_size: The maximum size of each chunk
        chunk_overlap: The overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or not isinstance(text, str):
        return []
    
    # If text is smaller than chunk size, return it as is
    if len(text) <= chunk_size:
        return [text]
    
    # Divide text into paragraphs
    paragraphs = text.split('\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    chunks = []
    current_chunk = []
    current_size = 0
    
    for paragraph in paragraphs:
        # If a single paragraph is larger than chunk_size, split it
        if len(paragraph) > chunk_size:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
            
            # Split the paragraph into smaller pieces
            sub_chunks = chunk_long_text(paragraph, chunk_size)
            chunks.extend(sub_chunks)
            continue
        
        # If adding this paragraph would exceed the chunk size
        if current_size + len(paragraph) > chunk_size:
            # Add the current chunk to the list of chunks
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            # Start a new chunk with overlap
            overlap_size = 0
            overlap_chunks = []
            
            # Include some of the previous chunks for overlap
            for prev_chunk in reversed(current_chunk):
                if overlap_size + len(prev_chunk) <= chunk_overlap:
                    overlap_chunks.insert(0, prev_chunk)
                    overlap_size += len(prev_chunk) + 1  # +1 for space
                else:
                    break
            
            current_chunk = overlap_chunks
            current_size = overlap_size
            
            # Add current paragraph
            current_chunk.append(paragraph)
            current_size += len(paragraph)
        else:
            # Add paragraph to current chunk
            current_chunk.append(paragraph)
            current_size += len(paragraph) + (1 if current_size > 0 else 0)  # +1 for space
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def chunk_long_text(text: str, chunk_size: int) -> List[str]:
    """
    Split very long text into equal parts, trying to split at sentence boundaries.
    
    Args:
        text: Long text to split
        chunk_size: Maximum size for each chunk
    
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    remaining_text = text
    
    while len(remaining_text) > chunk_size:
        # Try to find a sentence boundary near the chunk_size
        split_point = remaining_text.rfind('. ', 0, chunk_size - 1)
        
        if split_point == -1:
            # If no sentence boundary, try to find a space
            split_point = remaining_text.rfind(' ', 0, chunk_size - 1)
        
        if split_point == -1:
            # If no good split point, just split at chunk_size
            split_point = chunk_size - 1
        else:
            # Include the period or space
            split_point += 2
        
        chunks.append(remaining_text[:split_point].strip())
        remaining_text = remaining_text[split_point:].strip()
    
    # Add the last piece
    if remaining_text:
        chunks.append(remaining_text)
    
    return chunks

def create_structured_chunks(text: str, metadata: Dict[str, Any] = None, 
                            chunk_size: int = 500, chunk_overlap: int = 50,
                            max_chunks: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Create structured chunks with metadata and sequence IDs.
    
    Args:
        text: The text to chunk
        metadata: Optional metadata to include with each chunk
        chunk_size: Maximum size for each chunk
        chunk_overlap: Overlap between chunks
        max_chunks: Maximum number of chunks to return
        
    Returns:
        List of dictionaries containing chunk text and metadata
    """
    chunks = chunk_text(text, chunk_size, chunk_overlap)
    
    if max_chunks and len(chunks) > max_chunks:
        logger.info(f"Limiting from {len(chunks)} to {max_chunks} chunks")
        chunks = chunks[:max_chunks]
    
    structured_chunks = []
    metadata = metadata or {}
    
    for i, chunk_text in enumerate(chunks):
        chunk = {
            "text": chunk_text,
            "sequence_id": i,
            "total_chunks": len(chunks),
            "metadata": metadata.copy()
        }
        structured_chunks.append(chunk)
    
    return structured_chunks

def combine_chunks(chunks: List[Dict[str, Any]]) -> str:
    """
    Combine structured chunks back into a single text.
    
    Args:
        chunks: List of structured chunks
        
    Returns:
        Combined text from all chunks
    """
    # Sort chunks by sequence_id
    sorted_chunks = sorted(chunks, key=lambda x: x.get("sequence_id", 0))
    
    # Extract text and join
    combined_text = ' '.join([chunk["text"] for chunk in sorted_chunks])
    
    return combined_text

async def semantic_chunk_text(text: str, 
                           embedder,
                           chunk_size: int = 500, 
                           chunk_overlap: int = 50,
                           similarity_threshold: float = 0.7) -> List[str]:
    """
    Split text into chunks based on semantic similarity using embeddings.
    
    This uses a combination of initial character-based chunking and then
    merges or splits chunks based on embedding similarity.
    
    Args:
        text: Text to split into chunks
        embedder: Function or object that generates embeddings for text
        chunk_size: Maximum size for each chunk
        chunk_overlap: Overlap between chunks
        similarity_threshold: Threshold for merging chunks (0.0 to 1.0)
        
    Returns:
        List of semantically coherent text chunks
    """
    # First, create initial chunks based on character count
    initial_chunks = chunk_text(text, chunk_size, chunk_overlap)
    
    if len(initial_chunks) <= 1:
        return initial_chunks
    
    try:
        # Generate embeddings for each chunk
        chunk_embeddings = []
        for chunk in initial_chunks:
            embedding = await embedder.embed_text(chunk)
            chunk_embeddings.append((chunk, embedding))
        
        # Calculate similarity between adjacent chunks
        final_chunks = [chunk_embeddings[0][0]]  # Start with the first chunk
        
        for i in range(1, len(chunk_embeddings)):
            current_chunk, current_embedding = chunk_embeddings[i]
            previous_embedding = chunk_embeddings[i-1][1]
            
            # Calculate cosine similarity
            similarity = cosine_similarity(previous_embedding, current_embedding)
            
            if similarity > similarity_threshold:
                # Merge with previous chunk
                merged_text = final_chunks.pop() + " " + current_chunk
                final_chunks.append(merged_text)
            else:
                # Add as separate chunk
                final_chunks.append(current_chunk)
        
        logger.info(f"Semantic chunking: reduced from {len(initial_chunks)} to {len(final_chunks)} chunks")
        return final_chunks
    
    except Exception as e:
        logger.error(f"Error in semantic chunking, falling back to basic chunking: {e}")
        return initial_chunks

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    # Avoid division by zero
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0.0
    
    return dot_product / (norm_vec1 * norm_vec2)

async def create_semantic_chunks(text: str, 
                              embedder,
                              metadata: Dict[str, Any] = None,
                              chunk_size: int = 500, 
                              chunk_overlap: int = 50,
                              max_chunks: Optional[int] = None,
                              similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
    """
    Create semantically coherent structured chunks.
    
    Args:
        text: Text to split into chunks
        embedder: Function or object that generates embeddings for text
        metadata: Optional metadata to include with each chunk
        chunk_size: Maximum size for each chunk
        chunk_overlap: Overlap between chunks
        max_chunks: Maximum number of chunks to return
        similarity_threshold: Threshold for merging chunks (0.0 to 1.0)
        
    Returns:
        List of dictionaries containing semantically coherent chunks with metadata
    """
    # Use semantic chunking to split the text
    chunks = await semantic_chunk_text(
        text, embedder, chunk_size, chunk_overlap, similarity_threshold
    )
    
    if max_chunks and len(chunks) > max_chunks:
        logger.info(f"Limiting from {len(chunks)} to {max_chunks} semantic chunks")
        chunks = chunks[:max_chunks]
    
    structured_chunks = []
    metadata = metadata or {}
    
    for i, chunk_text in enumerate(chunks):
        chunk = {
            "text": chunk_text,
            "sequence_id": i,
            "total_chunks": len(chunks),
            "metadata": metadata.copy(),
            "is_semantic_chunk": True
        }
        structured_chunks.append(chunk)
    
    return structured_chunks 