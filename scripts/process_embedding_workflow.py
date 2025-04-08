#!/usr/bin/env python
"""
Process Embedding Workflow

This script demonstrates the complete workflow for processing frames and chunks,
generating embeddings, and ensuring consistent reference IDs across schemas.
"""

import os
import sys
import logging
import asyncio
import numpy as np
import pandas as pd
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logging_config import configure_logging

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)

# Mock dimension for embeddings (should match env settings)
EMBEDDING_DIM = 1024

# Helper function to convert numpy types to Python native types
def convert_numpy_to_python(obj):
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, 
                      np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.bool_)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_numpy_to_python(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_python(item) for item in obj]
    elif obj is None:
        return None
    else:
        return obj

# Create a mock PostgresVectorStore class for testing
class MockPostgresVectorStore:
    """
    Mock implementation of PostgresVectorStore for testing without a real database.
    """
    
    def __init__(self):
        """Initialize the mock store with in-memory data structures."""
        self.connected = False
        self.frames = {}
        self.chunks = {}
        self.frame_embeddings = {}
        self.chunk_embeddings = {}
        self.chunk_embeddings_multimodal = {}  # New table for multimodal_embeddings_chunks
        self.frame_details = {}
        self.chunk_details = {}
        self.process_chunks_data = {}
        self.next_frame_id = 1
        self.next_chunk_id = 1
        
    async def connect(self) -> bool:
        """Simulate connecting to the database."""
        self.connected = True
        logger.info("Connected to mock PostgreSQL database")
        return True
    
    async def close(self):
        """Simulate closing the database connection."""
        self.connected = False
        logger.info("Mock PostgreSQL connection closed")
    
    async def store_frame(self, 
                         frame_name: str, 
                         folder_path: Optional[str] = None,
                         folder_name: Optional[str] = None,
                         frame_timestamp: Optional[str] = None,
                         google_drive_url: Optional[str] = None,
                         airtable_record_id: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """Store frame information and return frame ID."""
        frame_id = self.next_frame_id
        self.next_frame_id += 1
        
        # Store frame data
        self.frames[frame_id] = {
            "id": frame_id,
            "frame_name": frame_name,
            "folder_path": folder_path,
            "folder_name": folder_name,
            "frame_timestamp": frame_timestamp,
            "google_drive_url": google_drive_url,
            "airtable_record_id": airtable_record_id,
            "metadata": metadata,
            "created_at": datetime.now().isoformat()
        }
        
        # Create reference_id in the format "folder_name_frame_name" using underscores
        reference_id = f"{folder_name}_{frame_name}" if folder_name else frame_name
        
        # Store frame details
        self.frame_details[frame_id] = {
            "frame_id": frame_id,
            "reference_id": reference_id,
            "metadata": metadata
        }
        
        logger.info(f"Stored frame information for '{frame_name}' with ID {frame_id}")
        return frame_id
    
    async def store_chunk(self,
                        frame_reference_id: str,
                        chunk_text: str,
                        chunk_sequence_id: int,
                        chunk_start_index: int = None,
                        chunk_end_index: int = None,
                        metadata: Dict[str, Any] = None) -> Optional[int]:
        """Store chunk details using a frame reference ID."""
        # Get frame_id from reference_id
        frame_id = None
        for fid, details in self.frame_details.items():
            if details["reference_id"] == frame_reference_id:
                frame_id = fid
                break
        
        if not frame_id:
            logger.error(f"Frame with reference_id {frame_reference_id} not found")
            return None
        
        chunk_id = self.next_chunk_id
        self.next_chunk_id += 1
        
        # Store chunk data
        self.chunks[chunk_id] = {
            "id": chunk_id,
            "frame_id": frame_id,
            "chunk_sequence_id": chunk_sequence_id,
            "chunk_text": chunk_text,
            "chunk_start_index": chunk_start_index,
            "chunk_end_index": chunk_end_index,
            "created_at": datetime.now().isoformat()
        }
        
        # Create reference_id for chunk in the standard format with underscores
        chunk_reference_id = f"{frame_reference_id}_chunk_{chunk_sequence_id}"
        
        # Store chunk details
        self.chunk_details[chunk_id] = {
            "chunk_id": chunk_id,
            "reference_id": chunk_reference_id,
            "chunk_sequence_id": chunk_sequence_id,
            "metadata": metadata
        }
        
        logger.info(f"Stored chunk {chunk_sequence_id} with ID {chunk_id} and reference_id {chunk_reference_id}")
        return chunk_id
    
    async def store_frame_embedding(self,
                                   frame_id: int,
                                   embedding: List[float],
                                   model_name: str,
                                   reference_id: str = None) -> Optional[str]:
        """Store a frame embedding and return the embedding ID."""
        embedding_id = str(uuid.uuid4())
        
        # Get reference_id if not provided
        if not reference_id:
            reference_id = self.frame_details.get(frame_id, {}).get("reference_id")
        
        # Store frame embedding
        self.frame_embeddings[embedding_id] = {
            "id": embedding_id,
            "frame_id": frame_id,
            "embedding": embedding,
            "model_name": model_name,
            "reference_id": reference_id,
            "creation_time": datetime.now().isoformat()
        }
        
        logger.info(f"Stored frame embedding for frame ID {frame_id} with embedding ID {embedding_id}")
        return embedding_id
    
    async def store_chunk_embedding(self,
                                   chunk_id: int,
                                   embedding: List[float],
                                   model_name: str,
                                   reference_id: str = None) -> Optional[str]:
        """Store a chunk embedding and return the embedding ID."""
        embedding_id = str(uuid.uuid4())
        
        # Get reference_id if not provided
        if not reference_id:
            reference_id = self.chunk_details.get(chunk_id, {}).get("reference_id")
        
        # Get chunk text
        chunk_text = self.chunks.get(chunk_id, {}).get("chunk_text", "")
        
        # Store chunk embedding in regular embeddings table
        self.chunk_embeddings[embedding_id] = {
            "id": embedding_id,
            "chunk_id": chunk_id,
            "embedding": embedding,
            "model_name": model_name,
            "reference_id": reference_id,
            "text_content": chunk_text,
            "creation_time": datetime.now().isoformat()
        }
        
        # Also store in multimodal_embeddings_chunks table
        self.chunk_embeddings_multimodal[embedding_id] = {
            "id": embedding_id,
            "chunk_id": chunk_id,
            "embedding_vector": embedding,
            "model_name": model_name,
            "reference_id": reference_id,
            "text_content": chunk_text,
            "creation_time": datetime.now().isoformat(),
            "dimensions": len(embedding)
        }
        
        logger.info(f"Stored chunk embedding for chunk ID {chunk_id} with embedding ID {embedding_id} in both embedding tables")
        return embedding_id
    
    async def store_process_chunk_data(self,
                                    frame_id: int,
                                    chunk_id: int,
                                    airtable_record_id: str,
                                    processing_status: str = "processed",
                                    chunk_type: str = "text",
                                    chunk_format: str = "plain",
                                    processing_metadata: Dict[str, Any] = None) -> bool:
        """Store processing information for a frame-chunk pair."""
        key = f"{frame_id}_{chunk_id}"
        
        self.process_chunks_data[key] = {
            "frame_id": frame_id,
            "chunk_id": chunk_id,
            "airtable_record_id": airtable_record_id,
            "processing_status": processing_status,
            "chunk_type": chunk_type,
            "chunk_format": chunk_format,
            "processing_metadata": processing_metadata or {},
            "processing_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Stored processing data for frame ID {frame_id}, chunk ID {chunk_id}")
        return True
    
    async def check_reference_id_in_metadata(self, reference_id: str) -> bool:
        """Check if a reference_id exists in the metadata schema."""
        # Check in frame_details
        for details in self.frame_details.values():
            if details["reference_id"] == reference_id:
                return True
        
        # Check in chunk_details
        for details in self.chunk_details.values():
            if details["reference_id"] == reference_id:
                return True
        
        return False
    
    async def check_reference_id_in_embeddings(self, reference_id: str) -> bool:
        """Check if a reference_id exists in the embeddings schema."""
        # Check in frame_embeddings
        for embedding in self.frame_embeddings.values():
            if embedding["reference_id"] == reference_id:
                return True
        
        # Check in chunk_embeddings
        for embedding in self.chunk_embeddings.values():
            if embedding["reference_id"] == reference_id:
                return True
        
        return False
    
    async def get_metadata_by_reference_id(self, reference_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a reference_id."""
        # Check if it's a frame reference_id
        for frame_id, details in self.frame_details.items():
            if details["reference_id"] == reference_id:
                frame = self.frames.get(frame_id, {})
                return {
                    "type": "frame",
                    "reference_id": reference_id,
                    "frame_name": frame.get("frame_name"),
                    "folder_name": frame.get("folder_name"),
                    "google_drive_url": frame.get("google_drive_url"),
                    "metadata": details.get("metadata")
                }
        
        # Check if it's a chunk reference_id
        for chunk_id, details in self.chunk_details.items():
            if details["reference_id"] == reference_id:
                chunk = self.chunks.get(chunk_id, {})
                frame_id = chunk.get("frame_id")
                frame = self.frames.get(frame_id, {}) if frame_id else {}
                
                return {
                    "type": "chunk",
                    "reference_id": reference_id,
                    "chunk_sequence_id": details.get("chunk_sequence_id"),
                    "chunk_text": chunk.get("chunk_text"),
                    "frame_name": frame.get("frame_name"),
                    "folder_name": frame.get("folder_name"),
                    "metadata": details.get("metadata")
                }
        
        return None
    
    async def get_chunk_processing_status(self, airtable_record_id: str) -> List[Dict[str, Any]]:
        """Get processing status for all chunks associated with an Airtable record."""
        results = []
        
        for data in self.process_chunks_data.values():
            if data["airtable_record_id"] == airtable_record_id:
                chunk_id = data["chunk_id"]
                frame_id = data["frame_id"]
                
                chunk = self.chunks.get(chunk_id, {})
                frame = self.frames.get(frame_id, {})
                
                result = {
                    **data,
                    "frame_name": frame.get("frame_name"),
                    "folder_name": frame.get("folder_name"),
                    "chunk_text": chunk.get("chunk_text"),
                    "chunk_sequence_id": chunk.get("chunk_sequence_id")
                }
                
                results.append(result)
        
        return results
    
    async def get_all_frames_with_embeddings(self) -> List[Dict[str, Any]]:
        """Get all frames with their embeddings."""
        results = []
        
        # Map embedding IDs to frame IDs
        frame_to_embedding = {}
        for embedding_id, embedding in self.frame_embeddings.items():
            frame_id = embedding.get("frame_id")
            if frame_id:
                frame_to_embedding[frame_id] = embedding_id
        
        # Build results
        for frame_id, frame in self.frames.items():
            details = self.frame_details.get(frame_id, {})
            embedding_id = frame_to_embedding.get(frame_id)
            
            result = {
                "frame_id": frame_id,
                "frame_name": frame.get("frame_name"),
                "folder_name": frame.get("folder_name"),
                "reference_id": details.get("reference_id"),
                "google_drive_url": frame.get("google_drive_url"),
                "airtable_record_id": frame.get("airtable_record_id"),
                "frame_metadata": frame.get("metadata")
            }
            
            if embedding_id:
                embedding = self.frame_embeddings[embedding_id]
                result["embedding_id"] = embedding_id
                result["model_name"] = embedding.get("model_name")
            
            results.append(result)
        
        return results
    
    async def get_all_chunks_with_embeddings(self) -> List[Dict[str, Any]]:
        """Get all chunks with their embeddings from both embedding tables."""
        results = []
        
        # Map embedding IDs to chunk IDs
        chunk_to_embedding = {}
        chunk_to_multimodal_embedding = {}
        
        for embedding_id, embedding in self.chunk_embeddings.items():
            chunk_id = embedding.get("chunk_id")
            if chunk_id:
                chunk_to_embedding[chunk_id] = embedding_id
                
        for embedding_id, embedding in self.chunk_embeddings_multimodal.items():
            chunk_id = embedding.get("chunk_id")
            if chunk_id:
                chunk_to_multimodal_embedding[chunk_id] = embedding_id
        
        # Build results
        for chunk_id, chunk in self.chunks.items():
            details = self.chunk_details.get(chunk_id, {})
            embedding_id = chunk_to_embedding.get(chunk_id)
            multimodal_embedding_id = chunk_to_multimodal_embedding.get(chunk_id)
            frame_id = chunk.get("frame_id")
            
            result = {
                "chunk_id": chunk_id,
                "frame_id": frame_id,
                "chunk_sequence_id": chunk.get("chunk_sequence_id"),
                "chunk_text_preview": chunk.get("chunk_text", "")[:100] if chunk.get("chunk_text") else "",
                "reference_id": details.get("reference_id")
            }
            
            if embedding_id:
                embedding = self.chunk_embeddings[embedding_id]
                result["embedding_id"] = embedding_id
                result["model_name"] = embedding.get("model_name")
            
            if multimodal_embedding_id:
                multimodal_embedding = self.chunk_embeddings_multimodal[multimodal_embedding_id]
                result["multimodal_embedding_id"] = multimodal_embedding_id
                result["dimensions"] = multimodal_embedding.get("dimensions")
            
            # Include chunking data from process_chunks_data if available
            for proc_key, proc_data in self.process_chunks_data.items():
                if proc_data.get("chunk_id") == chunk_id:
                    result["processing_status"] = proc_data.get("processing_status", "")
                    result["chunk_type"] = proc_data.get("chunk_type", "")
                    result["chunk_format"] = proc_data.get("chunk_format", "")
                    result["processing_metadata"] = proc_data.get("processing_metadata", {})
                    break
            
            results.append(result)
        
        return results
    
    async def store_chunking_data(self,
                               chunk_id: int,
                               chunk_data: Dict[str, Any]) -> bool:
        """
        Store additional chunking data for a specific chunk.
        
        Args:
            chunk_id: ID of the chunk
            chunk_data: Additional data about the chunk to store
            
        Returns:
            Boolean indicating success
        """
        if chunk_id not in self.chunks:
            logger.error(f"Chunk with ID {chunk_id} not found")
            return False
            
        # Update chunk data with the new information
        self.chunks[chunk_id].update(chunk_data)
        
        # If there's metadata, update it in the chunk details
        if "metadata" in chunk_data and chunk_id in self.chunk_details:
            existing_metadata = self.chunk_details[chunk_id].get("metadata", {}) or {}
            updated_metadata = {**existing_metadata, **chunk_data.get("metadata", {})}
            self.chunk_details[chunk_id]["metadata"] = updated_metadata
        
        logger.info(f"Updated chunking data for chunk ID {chunk_id}")
        return True

    @property
    def connection_pool(self):
        """Create a mock connection pool for compatibility."""
        return MockConnectionPool(self)

    async def search_embeddings(self,
                            embedding: List[float],
                            reference_type: str = "frame",
                            table: str = "default",
                            limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings in the database.
        
        Args:
            embedding: Vector to search against
            reference_type: Type of embedding to search (frame or chunk)
            table: Table to search in ('default' for normal table, 'multimodal_chunks' for the multimodal_embeddings_chunks table)
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries with search results
        """
        try:
            results = []
            
            # Convert input embedding to numpy for cosine similarity calculation
            query_vector = np.array(embedding)
            query_norm = np.linalg.norm(query_vector)
            if query_norm > 0:
                query_vector = query_vector / query_norm
            
            # Choose the appropriate embeddings collection based on reference_type and table
            if reference_type.lower() == "frame":
                embeddings_collection = self.frame_embeddings
                id_field = "frame_id"
            else:  # chunk
                if table.lower() == "multimodal_chunks":
                    embeddings_collection = self.chunk_embeddings_multimodal
                else:
                    embeddings_collection = self.chunk_embeddings
                id_field = "chunk_id"
            
            # Calculate similarity for each embedding
            similarities = []
            for embedding_id, item in embeddings_collection.items():
                # Skip if no embedding vector
                vector_key = "embedding_vector" if "embedding_vector" in item else "embedding"
                if vector_key not in item:
                    continue
                
                # Get the embedding vector and calculate similarity
                db_vector = np.array(item[vector_key])
                db_norm = np.linalg.norm(db_vector)
                if db_norm > 0:
                    db_vector = db_vector / db_norm
                
                # Calculate cosine similarity
                similarity = np.dot(query_vector, db_vector)
                
                # Store result with similarity score
                similarities.append({
                    "embedding_id": embedding_id,
                    id_field: item.get(id_field),
                    "reference_id": item.get("reference_id"),
                    "similarity": float(similarity),
                    "dimensions": len(db_vector),
                    "model_name": item.get("model_name")
                })
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Return top results
            results = similarities[:limit]
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching for embeddings: {str(e)}")
            return []

class MockConnectionPool:
    """Mock connection pool for compatibility with real code."""
    
    def __init__(self, store):
        """Initialize with a reference to the mock store."""
        self.store = store
    
    async def acquire(self):
        """Return a mock connection."""
        return MockConnection(self.store)
    
    async def release(self, conn):
        """Release a mock connection."""
        pass
    
    async def close(self):
        """Close the mock connection pool."""
        pass

class MockConnection:
    """Mock database connection."""
    
    def __init__(self, store):
        """Initialize with a reference to the mock store."""
        self.store = store
    
    async def __aenter__(self):
        """Enter context manager."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        pass
    
    async def fetchrow(self, query, *args, **kwargs):
        """Simulate fetching a single row."""
        # This is highly simplified and only handles known query patterns
        if "frame_details_full" in query and "frame_id" in args:
            frame_id = args[0]
            if frame_id in self.store.frames:
                frame = self.store.frames[frame_id]
                frame_details = self.store.frame_details.get(frame_id, {})
                
                return {
                    "reference_id": frame_details.get("reference_id"),
                    "metadata": frame_details.get("metadata"),
                    "airtable_record_id": frame.get("airtable_record_id"),
                    "google_drive_url": frame.get("google_drive_url"),
                    "frame_name": frame.get("frame_name"),
                    "folder_name": frame.get("folder_name"),
                    "description": None,
                    "summary": None,
                    "frame_metadata": frame_details.get("metadata")
                }
        
        elif "frame_details_chunk" in query and "chunk_id" in args:
            chunk_id = args[0]
            if chunk_id in self.store.chunks:
                chunk = self.store.chunks[chunk_id]
                chunk_details = self.store.chunk_details.get(chunk_id, {})
                frame_id = chunk.get("frame_id")
                frame = self.store.frames.get(frame_id, {})
                
                return {
                    "reference_id": chunk_details.get("reference_id"),
                    "metadata": chunk_details.get("metadata"),
                    "chunk_text": chunk.get("chunk_text"),
                    "chunk_sequence_id": chunk.get("chunk_sequence_id"),
                    "frame_name": frame.get("frame_name"),
                    "folder_name": frame.get("folder_name")
                }
        
        elif "process_frames_chunks" in query and "chunk_id" in args:
            chunk_id = args[0]
            for data in self.store.process_chunks_data.values():
                if data["chunk_id"] == chunk_id:
                    return {
                        "processing_status": data.get("processing_status"),
                        "chunk_type": data.get("chunk_type"),
                        "chunk_format": data.get("chunk_format")
                    }
        
        return None
    
    async def fetchval(self, query, *args, **kwargs):
        """Simulate fetching a single value."""
        return None
    
    async def fetch(self, query, *args, **kwargs):
        """Simulate fetching multiple rows."""
        if "metadata.process_frames_chunks" in query and "airtable_record_id" in args:
            airtable_id = args[0]
            return [MockRecord(data) for data in self.store.get_chunk_processing_status(airtable_id)]
        
        return []
    
    async def execute(self, query, *args, **kwargs):
        """Simulate executing a query."""
        return None

class MockRecord(dict):
    """Mock database record that acts like both a dict and an object."""
    
    def __getattr__(self, name):
        """Allow attribute access for dictionary keys."""
        if name in self:
            return self[name]
        raise AttributeError(f"'MockRecord' object has no attribute '{name}'")

def generate_mock_embedding(dimension: int = EMBEDDING_DIM) -> List[float]:
    """Generate a mock embedding vector for testing purposes."""
    embedding = np.random.normal(0, 1, dimension).tolist()
    # Normalize the embedding
    norm = np.linalg.norm(embedding)
    normalized_embedding = [x / norm for x in embedding]
    return normalized_embedding

def generate_mock_airtable_data(index: int = 0) -> Dict[str, Any]:
    """
    Generate mock Airtable data to simulate what would come from Airtable.
    
    Args:
        index: Index to create varied data
        
    Returns:
        Dict containing mock Airtable fields
    """
    # Create a standard set of Airtable fields
    statuses = ["New", "Processing", "Completed", "Archived"]
    categories = ["Invoice", "Contract", "Report", "Letter", "Form"]
    users = ["User A", "User B", "User C"]
    priorities = ["Low", "Medium", "High"]
    approval_statuses = ["Pending", "Approved", "Rejected", None]
    file_types = ["PDF", "DOCX", "TXT", "JPG"]
    
    airtable_data = {
        "ID": f"recAirtable{index}{uuid.uuid4().hex[:8]}",
        "Name": f"Sample Document {index}",
        "Description": f"This is a sample document {index} with detailed metadata",
        "Status": statuses[np.random.randint(0, len(statuses))],
        "Category": categories[np.random.randint(0, len(categories))],
        "Tags": [f"tag{i}" for i in range(1, np.random.randint(2, 5))],
        "Created Date": (datetime.now() - timedelta(days=np.random.randint(1, 30))).isoformat(),
        "Modified Date": datetime.now().isoformat(),
        "Assigned To": users[np.random.randint(0, len(users))],
        "Priority": priorities[np.random.randint(0, len(priorities))],
        "Due Date": (datetime.now() + timedelta(days=np.random.randint(1, 14))).isoformat(),
        "Related Records": [f"rec{uuid.uuid4().hex[:10]}" for _ in range(np.random.randint(0, 3))],
        "Comments": [f"Comment {i}: This is a comment on document {index}" for i in range(np.random.randint(0, 3))],
        "Approval Status": approval_statuses[np.random.randint(0, len(approval_statuses))],
        "Word Count": int(np.random.randint(100, 5000)),
        "Page Count": int(np.random.randint(1, 20)),
        "File Type": file_types[np.random.randint(0, len(file_types))],
        "Processed": bool(np.random.choice([True, False])),
    }
    
    # Convert all numpy types to Python native types
    return convert_numpy_to_python(airtable_data)

def generate_mock_ocr_results(text_length: int = 500) -> Dict[str, Any]:
    """
    Generate mock OCR processing results.
    
    Args:
        text_length: Length of OCR text to generate
        
    Returns:
        Dict containing mock OCR results
    """
    # Generate some random text
    words = ["Lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", "elit", 
             "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore", "et", "dolore", 
             "magna", "aliqua", "Ut", "enim", "ad", "minim", "veniam", "quis", "nostrud", 
             "exercitation", "ullamco", "laboris", "nisi", "ut", "aliquip", "ex", "ea", "commodo",
             "consequat", "Duis", "aute", "irure", "dolor", "in", "reprehenderit", "in", "voluptate", 
             "velit", "esse", "cillum", "dolore", "eu", "fugiat", "nulla", "pariatur"]
    
    languages = ["en", "es", "fr", "de"]
    
    sentence_length = np.random.randint(5, 15)
    num_sentences = text_length // sentence_length
    
    sentences = []
    for _ in range(num_sentences):
        sentence_words = np.random.choice(words, sentence_length)
        sentence = " ".join(sentence_words)
        sentences.append(sentence.capitalize() + ".")
    
    ocr_text = " ".join(sentences)
    
    # Create OCR results structure
    ocr_results = {
        "processed_text": ocr_text,
        "confidence_score": float(np.random.uniform(0.7, 0.99)),
        "processing_time_ms": int(np.random.randint(500, 3000)),
        "detected_language": languages[np.random.randint(0, len(languages))],
        "page_count": int(np.random.randint(1, 10)),
        "has_tables": bool(np.random.choice([True, False])),
        "has_images": bool(np.random.choice([True, False])),
        "word_count": len(ocr_text.split()),
        "character_count": len(ocr_text),
        "detected_entities": {
            "people": [f"Person {i}" for i in range(np.random.randint(0, 3))],
            "organizations": [f"Org {i}" for i in range(np.random.randint(0, 3))],
            "locations": [f"Location {i}" for i in range(np.random.randint(0, 2))],
            "dates": [f"2023-{np.random.randint(1, 12):02d}-{np.random.randint(1, 28):02d}" for _ in range(np.random.randint(0, 2))]
        }
    }
    
    # Convert all numpy types to Python native types
    return convert_numpy_to_python(ocr_results)

async def process_frame_with_airtable_data(
    store: MockPostgresVectorStore,
    frame_name: str,
    folder_name: str,
    airtable_data: Dict[str, Any],
    ocr_results: Dict[str, Any] = None
) -> Tuple[bool, Optional[str], Optional[int], Optional[str]]:
    """
    Process a frame with Airtable data and optional OCR results, storing all data in PostgreSQL.
    
    Args:
        store: MockPostgresVectorStore instance
        frame_name: Name of the frame file
        folder_name: Name of the folder containing the frame
        airtable_data: Airtable record data
        ocr_results: Optional OCR processing results
        
    Returns:
        Tuple of (success, reference_id, frame_id, airtable_record_id)
    """
    try:
        airtable_record_id = airtable_data.get("ID", f"rec{uuid.uuid4().hex[:14]}")
        logger.info(f"Processing frame: {folder_name}/{frame_name} with Airtable ID: {airtable_record_id}")
        
        # Create reference_id in the standard format for database retrieval using underscores
        reference_id = f"{folder_name}_{frame_name}"
        
        # Store frame details in metadata schema
        frame_timestamp = datetime.now().isoformat()
        
        # Generate a Google Drive ID for this frame
        google_drive_id = str(uuid.uuid4())
        google_drive_url = f"https://drive.google.com/file/d/{google_drive_id}/view"
        
        # Combine Airtable data and OCR results into metadata
        metadata = {
            "airtable": airtable_data,
            "google_drive_id": google_drive_id
        }
        
        # Add OCR results if available
        if ocr_results:
            metadata["ocr_results"] = ocr_results
        
        frame_id = await store.store_frame(
            frame_name=frame_name,
            folder_path=f"/path/to/{folder_name}",
            folder_name=folder_name,
            frame_timestamp=frame_timestamp,
            google_drive_url=google_drive_url,
            airtable_record_id=airtable_record_id,
            metadata=metadata
        )
        
        if not frame_id:
            logger.error(f"Failed to store frame {reference_id}")
            return False, None, None, None
            
        # Generate and store frame embedding
        embedding = generate_mock_embedding()
        embedding_success = await store.store_frame_embedding(
            frame_id=frame_id,
            embedding=embedding,
            model_name="mock-model-v1",
            reference_id=reference_id
        )
        
        if not embedding_success:
            logger.error(f"Failed to store embedding for frame {reference_id}")
            return False, None, None, None
            
        logger.info(f"Successfully processed frame {reference_id} with database ID {frame_id}, " 
                    f"Airtable ID {airtable_record_id}, and Google Drive ID {google_drive_id}")
        return True, reference_id, frame_id, airtable_record_id
        
    except Exception as e:
        logger.error(f"Error processing frame {folder_name}/{frame_name}: {str(e)}")
        return False, None, None, None

async def process_chunks(
    store: MockPostgresVectorStore,
    frame_reference_id: str,
    frame_id: int,
    airtable_record_id: str,
    chunks: List[Dict[str, Any]]
) -> List[str]:
    """
    Process chunks for a frame, storing chunk data and embeddings with consistent reference_ids.
    Also records processing status in the metadata.process_frames_chunks table.
    
    Args:
        store: MockPostgresVectorStore instance
        frame_reference_id: Reference ID of the parent frame
        frame_id: Database ID of the parent frame
        airtable_record_id: Airtable record ID associated with the frame
        chunks: List of chunk data dictionaries
        
    Returns:
        List of successfully processed chunk reference IDs
    """
    successful_chunks = []
    
    for i, chunk in enumerate(chunks):
        try:
            # Create reference_id for chunk in the standard format with underscores
            chunk_reference_id = f"{frame_reference_id}_chunk_{i}"
            
            logger.info(f"Processing chunk: {chunk_reference_id}")
            
            # Get chunk metadata and processing info
            chunk_metadata = chunk.get("metadata", {}).copy()
            chunk_type = chunk_metadata.pop("chunk_type", "text")
            chunk_format = chunk_metadata.pop("chunk_format", "plain")
            processing_status = "processing"
            
            # Store chunk details in metadata schema
            chunk_id = await store.store_chunk(
                frame_reference_id=frame_reference_id,
                chunk_text=chunk.get("text", ""),
                chunk_sequence_id=i,
                chunk_start_index=chunk.get("start_index", 0),
                chunk_end_index=chunk.get("end_index", 0),
                metadata=chunk_metadata
            )
            
            if not chunk_id:
                logger.error(f"Failed to store chunk {chunk_reference_id}")
                
                # Record failed processing status
                await store.store_process_chunk_data(
                    frame_id=frame_id,
                    chunk_id=-1,  # Invalid ID to indicate failure
                    airtable_record_id=airtable_record_id,
                    processing_status="failed",
                    chunk_type=chunk_type,
                    chunk_format=chunk_format,
                    processing_metadata={
                        "error": "Failed to store chunk",
                        "chunk_reference_id": chunk_reference_id
                    }
                )
                continue
                
            # Generate and store chunk embedding
            embedding = generate_mock_embedding()
            embedding_success = await store.store_chunk_embedding(
                chunk_id=chunk_id,
                embedding=embedding,
                model_name="mock-model-v1",
                reference_id=chunk_reference_id
            )
            
            if not embedding_success:
                logger.error(f"Failed to store embedding for chunk {chunk_reference_id}")
                
                # Record failed embedding status
                await store.store_process_chunk_data(
                    frame_id=frame_id,
                    chunk_id=chunk_id,
                    airtable_record_id=airtable_record_id,
                    processing_status="failed_embedding",
                    chunk_type=chunk_type,
                    chunk_format=chunk_format,
                    processing_metadata={
                        "error": "Failed to store embedding",
                        "chunk_reference_id": chunk_reference_id
                    }
                )
                continue
            
            # Record successful processing status
            processing_metadata = {
                "chunk_reference_id": chunk_reference_id,
                "model": "mock-model-v1",
                "embedding_dim": EMBEDDING_DIM,
                "chunk_sequence_id": i,
                "processing_time": datetime.now().isoformat()
            }
            
            # Add any additional metadata from the chunk
            if chunk_metadata:
                processing_metadata.update({"original_metadata": chunk_metadata})
                
            await store.store_process_chunk_data(
                frame_id=frame_id,
                chunk_id=chunk_id,
                airtable_record_id=airtable_record_id,
                processing_status="completed",
                chunk_type=chunk_type,
                chunk_format=chunk_format,
                processing_metadata=processing_metadata
            )
                
            logger.info(f"Successfully processed chunk {chunk_reference_id}")
            successful_chunks.append(chunk_reference_id)
            
        except Exception as e:
            logger.error(f"Error processing chunk {i} for frame {frame_reference_id}: {str(e)}")
            
            # Record error in processing status
            try:
                await store.store_process_chunk_data(
                    frame_id=frame_id,
                    chunk_id=-1,  # Unknown chunk ID due to error
                    airtable_record_id=airtable_record_id,
                    processing_status="error",
                    chunk_type="unknown",
                    chunk_format="unknown",
                    processing_metadata={
                        "error": str(e),
                        "chunk_index": i,
                        "frame_reference_id": frame_reference_id
                    }
                )
            except Exception as inner_e:
                logger.error(f"Failed to record error status: {str(inner_e)}")
    
    return successful_chunks

async def verify_reference_ids(
    store: MockPostgresVectorStore,
    reference_ids: List[str],
    frame_id_mapping: Optional[Dict[int, str]] = None
) -> Dict[str, bool]:
    """
    Verify that reference_ids exist in both metadata and embeddings schemas,
    and that frame IDs correctly map to reference IDs.
    
    Args:
        store: MockPostgresVectorStore instance
        reference_ids: List of reference IDs to check
        frame_id_mapping: Optional mapping of frame IDs to reference IDs
        
    Returns:
        Dictionary mapping reference_ids to verification results
    """
    results = {}
    
    # First verify each reference ID exists in both schemas
    for ref_id in reference_ids:
        try:
            # Check if reference_id exists in metadata schema
            metadata_exists = await store.check_reference_id_in_metadata(ref_id)
            
            # Check if reference_id exists in embeddings schema
            embedding_exists = await store.check_reference_id_in_embeddings(ref_id)
            
            # Both should exist for consistency
            is_consistent = metadata_exists and embedding_exists
            
            results[ref_id] = is_consistent
            
            if is_consistent:
                logger.info(f"Reference ID {ref_id} is consistent across schemas")
            else:
                logger.warning(
                    f"Reference ID {ref_id} is inconsistent: "
                    f"metadata={metadata_exists}, embeddings={embedding_exists}"
                )
                
        except Exception as e:
            logger.error(f"Error verifying reference ID {ref_id}: {str(e)}")
            results[ref_id] = False
    
    # Verify frame ID to reference ID mappings if provided
    if frame_id_mapping:
        logger.info("Verifying frame ID to reference ID mappings")
        
        try:
            for frame_id, ref_id in frame_id_mapping.items():
                # Get the reference_id from the store
                stored_ref_id = store.frame_details.get(frame_id, {}).get("reference_id")
                
                if stored_ref_id == ref_id:
                    logger.info(f"Frame ID {frame_id} correctly maps to reference ID {ref_id}")
                else:
                    logger.warning(f"Frame ID {frame_id} maps to {stored_ref_id} in DB, expected {ref_id}")
                    # Mark this reference ID as inconsistent
                    results[ref_id] = False
        except Exception as e:
            logger.error(f"Error verifying frame ID mappings: {str(e)}")
    
    return results

async def search_similar_embeddings(
    store: MockPostgresVectorStore,
    query_text: str,
    reference_type: str = "frame",
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for similar embeddings and return results with metadata.
    
    Args:
        store: MockPostgresVectorStore instance
        query_text: Query text to convert to embedding
        reference_type: Type of reference to search ('frame' or 'chunk')
        limit: Maximum number of results to return
        
    Returns:
        List of dictionaries with search results
    """
    try:
        # Generate embedding for query text
        query_embedding = generate_mock_embedding()
        
        # Search for similar embeddings
        results = await store.search_embeddings(
            embedding=query_embedding,
            reference_type=reference_type,
            limit=limit
        )
        
        # For each result, fetch the corresponding metadata
        enhanced_results = []
        for result in results:
            reference_id = result.get("reference_id")
            if not reference_id:
                continue
                
            # Fetch metadata for this reference_id
            metadata = await store.get_metadata_by_reference_id(reference_id)
            
            # Combine embedding results with metadata
            enhanced_result = {
                **result,
                "metadata": metadata
            }
            
            enhanced_results.append(enhanced_result)
            
        return enhanced_results
        
    except Exception as e:
        logger.error(f"Error searching for similar embeddings: {str(e)}")
        return []

async def export_to_csv(
    store: MockPostgresVectorStore,
    output_dir: str = "output"
) -> bool:
    """
    Export frame and chunk data to CSV files, including Airtable data, OCR results,
    database IDs, reference IDs, and other metadata.
    
    Args:
        store: MockPostgresVectorStore instance
        output_dir: Directory to save CSV files
        
    Returns:
        Boolean indicating success
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Export frames data
        frames_data = await store.get_all_frames_with_embeddings()
        if frames_data:
            # Expand metadata fields for each frame
            expanded_frames = []
            
            for frame in frames_data:
                # Create a new expanded frame record
                expanded_frame = frame.copy()
                
                # Extract Google Drive ID from URL if available
                google_drive_url = frame.get("google_drive_url", "")
                if google_drive_url and "/file/d/" in google_drive_url:
                    drive_id = google_drive_url.split("/file/d/")[1].split("/")[0]
                    expanded_frame["google_drive_id"] = drive_id
                else:
                    expanded_frame["google_drive_id"] = ""
                
                # Extract and flatten Airtable data
                frame_metadata = frame.get("frame_metadata", {})
                if frame_metadata and isinstance(frame_metadata, dict):
                    # Add Airtable fields with airtable_ prefix
                    airtable_data = frame_metadata.get("airtable", {})
                    if airtable_data and isinstance(airtable_data, dict):
                        for key, value in airtable_data.items():
                            if isinstance(value, (str, int, float, bool)):
                                expanded_frame[f"airtable_{key}"] = value
                            else:
                                # Convert numpy types and serialize
                                expanded_frame[f"airtable_{key}"] = json.dumps(convert_numpy_to_python(value))
                    
                    # Add OCR results with ocr_ prefix
                    ocr_results = frame_metadata.get("ocr_results", {})
                    if ocr_results and isinstance(ocr_results, dict):
                        for key, value in ocr_results.items():
                            if key == "detected_entities" and isinstance(value, dict):
                                # Flatten nested entities
                                for entity_type, entities in value.items():
                                    # Convert numpy types and serialize
                                    expanded_frame[f"ocr_entities_{entity_type}"] = json.dumps(convert_numpy_to_python(entities))
                            else:
                                if isinstance(value, (str, int, float, bool)):
                                    expanded_frame[f"ocr_{key}"] = value
                                else:
                                    # Convert numpy types and serialize
                                    expanded_frame[f"ocr_{key}"] = json.dumps(convert_numpy_to_python(value))
                
                expanded_frames.append(expanded_frame)
            
            # Convert to DataFrame
            frames_df = pd.DataFrame(expanded_frames)
            
            # Reorder columns to place IDs first, then Airtable data, then OCR data
            id_columns = ["frame_id", "reference_id", "airtable_ID", "google_drive_id"]
            airtable_columns = [col for col in frames_df.columns if col.startswith("airtable_")]
            ocr_columns = [col for col in frames_df.columns if col.startswith("ocr_")]
            other_columns = [col for col in frames_df.columns if col not in id_columns + airtable_columns + ocr_columns]
            
            ordered_columns = id_columns + airtable_columns + ocr_columns + other_columns
            
            # Ensure all required columns exist
            for col in id_columns:
                if col not in frames_df.columns:
                    frames_df[col] = ""
                    
            # Select available columns in the ordered sequence
            available_columns = [col for col in ordered_columns if col in frames_df.columns]
            if available_columns:
                frames_df = frames_df[available_columns]
            
            frames_csv_path = os.path.join(output_dir, "frames.csv")
            frames_df.to_csv(frames_csv_path, index=False)
            logger.info(f"Exported {len(frames_data)} frames to {frames_csv_path}")
            
            # Create a separate ID mapping file for easy lookup
            id_cols = [col for col in id_columns if col in frames_df.columns]
            if id_cols:
                id_mapping_df = frames_df[id_cols]
                id_mapping_csv_path = os.path.join(output_dir, "frame_id_mapping.csv")
                id_mapping_df.to_csv(id_mapping_csv_path, index=False)
                logger.info(f"Exported frame ID mapping to {id_mapping_csv_path}")
        else:
            logger.warning("No frame data to export")
        
        # Export chunks data
        chunks_data = await store.get_all_chunks_with_embeddings()
        if chunks_data:
            # Get frame information for each chunk including Airtable and OCR data
            expanded_chunks = []
            
            for chunk in chunks_data:
                expanded_chunk = chunk.copy()
                frame_id = chunk.get("frame_id")
                
                if frame_id:
                    # Get frame data
                    frame = store.frames.get(frame_id, {})
                    frame_details = store.frame_details.get(frame_id, {})
                    
                    # Add basic frame identifiers
                    expanded_chunk["frame_reference_id"] = frame_details.get("reference_id", "")
                    expanded_chunk["frame_airtable_id"] = frame.get("airtable_record_id", "")
                    
                    # Extract Google Drive ID
                    google_drive_url = frame.get("google_drive_url", "")
                    if google_drive_url and "/file/d/" in google_drive_url:
                        drive_id = google_drive_url.split("/file/d/")[1].split("/")[0]
                        expanded_chunk["frame_google_drive_id"] = drive_id
                    
                    # Add relevant Airtable data
                    frame_metadata = frame.get("metadata", {})
                    if frame_metadata and isinstance(frame_metadata, dict):
                        airtable_data = frame_metadata.get("airtable", {})
                        if airtable_data and isinstance(airtable_data, dict):
                            for key in ["ID", "Name", "Category", "Status"]:
                                if key in airtable_data:
                                    expanded_chunk[f"frame_airtable_{key}"] = airtable_data[key]
                
                # Get chunk-specific metadata
                chunk_id = chunk.get("chunk_id")
                if chunk_id:
                    chunk_details = store.chunk_details.get(chunk_id, {})
                    metadata = chunk_details.get("metadata", {})
                    
                    if metadata and isinstance(metadata, dict):
                        # Add selected chunk metadata fields
                        for key, value in metadata.items():
                            if key in ["importance", "sentiment", "chunk_type", "chunk_format"]:
                                expanded_chunk[f"chunk_{key}"] = value
                
                    # Include multimodal embedding info if available
                    if "multimodal_embedding_id" in chunk:
                        expanded_chunk["has_multimodal_embedding"] = True
                        expanded_chunk["embedding_dimensions"] = chunk.get("dimensions", EMBEDDING_DIM)
                
                expanded_chunks.append(expanded_chunk)
            
            # Convert to DataFrame
            chunks_df = pd.DataFrame(expanded_chunks)
            
            # Reorder columns to place IDs and related data first
            id_columns = [
                "chunk_id", "reference_id", 
                "frame_id", "frame_reference_id", "frame_airtable_id", "frame_google_drive_id",
                "processing_status", "chunk_type", "chunk_format", "has_multimodal_embedding", "embedding_dimensions"
            ]
            airtable_columns = [col for col in chunks_df.columns if col.startswith("frame_airtable_")]
            chunk_meta_columns = [col for col in chunks_df.columns if col.startswith("chunk_") and col not in ["chunk_id", "chunk_type", "chunk_format"]]
            other_columns = [col for col in chunks_df.columns if col not in id_columns + airtable_columns + chunk_meta_columns]
            
            ordered_columns = id_columns + airtable_columns + chunk_meta_columns + other_columns
            
            # Ensure all required columns exist
            for col in id_columns:
                if col not in chunks_df.columns:
                    chunks_df[col] = ""
                    
            # Select available columns in the ordered sequence
            available_columns = [col for col in ordered_columns if col in chunks_df.columns]
            if available_columns:
                chunks_df = chunks_df[available_columns]
            
            chunks_csv_path = os.path.join(output_dir, "chunks.csv")
            chunks_df.to_csv(chunks_csv_path, index=False)
            logger.info(f"Exported {len(chunks_data)} chunks to {chunks_csv_path}")
            
            # Create a separate ID mapping file for chunks
            chunk_id_cols = [col for col in [
                "chunk_id", "reference_id", 
                "frame_id", "frame_reference_id", "frame_airtable_id",
                "has_multimodal_embedding", "multimodal_embedding_id"
            ] if col in chunks_df.columns]
            if chunk_id_cols:
                chunk_id_mapping_df = chunks_df[chunk_id_cols]
                chunk_id_mapping_csv_path = os.path.join(output_dir, "chunk_id_mapping.csv")
                chunk_id_mapping_df.to_csv(chunk_id_mapping_csv_path, index=False)
                logger.info(f"Exported chunk ID mapping to {chunk_id_mapping_csv_path}")
        else:
            logger.warning("No chunk data to export")
            
        return True
        
    except Exception as e:
        logger.error(f"Error exporting data to CSV: {str(e)}")
        return False

async def print_processing_status(store: MockPostgresVectorStore, airtable_id: str) -> None:
    """
    Print the processing status of all chunks for a given Airtable record.
    
    Args:
        store: MockPostgresVectorStore instance
        airtable_id: Airtable record ID to check
    """
    logger.info(f"Checking processing status for Airtable ID: {airtable_id}")
    
    # Get processing status data
    status_data = await store.get_chunk_processing_status(airtable_id)
    
    if not status_data:
        logger.warning(f"No processing data found for Airtable ID: {airtable_id}")
        return
    
    # Group by status for summary
    status_counts = {}
    for item in status_data:
        status = item.get("processing_status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    # Print summary
    total_chunks = len(status_data)
    logger.info(f"Processing summary for Airtable ID {airtable_id}:")
    logger.info(f"  Total chunks: {total_chunks}")
    for status, count in status_counts.items():
        percentage = (count / total_chunks) * 100
        logger.info(f"  {status}: {count} chunks ({percentage:.1f}%)")
    
    # Print details for each chunk
    logger.info("Detailed chunk processing status:")
    for item in status_data:
        chunk_id = item.get("chunk_id")
        seq_id = item.get("chunk_sequence_id")
        status = item.get("processing_status")
        chunk_type = item.get("chunk_type")
        timestamp = item.get("processing_timestamp")
        
        # Format text preview (truncate to 30 chars)
        text_preview = item.get("chunk_text", "")
        if len(text_preview) > 30:
            text_preview = text_preview[:27] + "..."
        
        logger.info(f"  Chunk {seq_id} (ID: {chunk_id}) - Status: {status}, Type: {chunk_type}")
        logger.info(f"    Processed: {timestamp}")
        logger.info(f"    Text: {text_preview}")

async def main():
    """Main workflow demonstration function."""
    logger.info("Starting embedding workflow demonstration")
    
    try:
        # Initialize MockPostgresVectorStore
        store = MockPostgresVectorStore()
        connected = await store.connect()
        
        if not connected:
            logger.error("Failed to connect to database")
            return
            
        logger.info("Connected to database successfully")
        
        # Process sample frames
        frame_reference_ids = []
        frame_db_ids = []
        frame_airtable_ids = []
        chunk_reference_ids = []
        
        # Process 3 sample frames with Airtable data and OCR results
        for i in range(3):
            frame_name = f"sample_frame_{i}.jpg"
            folder_name = "test_batch"
            
            # Generate mock Airtable data and OCR results
            airtable_data = generate_mock_airtable_data(i)
            ocr_results = generate_mock_ocr_results()
            
            success, reference_id, frame_id, airtable_id = await process_frame_with_airtable_data(
                store=store,
                frame_name=frame_name,
                folder_name=folder_name,
                airtable_data=airtable_data,
                ocr_results=ocr_results
            )
            
            if success and reference_id and frame_id:
                frame_reference_ids.append(reference_id)
                frame_db_ids.append(frame_id)
                frame_airtable_ids.append(airtable_id)
                
                # Generate 2-3 chunks per frame
                num_chunks = np.random.randint(2, 4)
                chunks = []
                
                for j in range(num_chunks):
                    # Add some variety in chunk types for demonstration
                    chunk_type = "text" if j % 2 == 0 else "image_text"
                    chunk_format = "plain" if j % 2 == 0 else "markdown"
                    
                    # Extract a subset of the OCR text to create chunks
                    if ocr_results and "processed_text" in ocr_results:
                        full_text = ocr_results["processed_text"]
                        words = full_text.split()
                        
                        # Divide text into chunks
                        chunk_size = len(words) // num_chunks
                        start_idx = j * chunk_size
                        end_idx = min((j + 1) * chunk_size, len(words))
                        
                        chunk_text = " ".join(words[start_idx:end_idx])
                    else:
                        chunk_text = f"This is sample text for chunk {j} in frame {i}"
                    
                    chunk = {
                        "text": chunk_text,
                        "start_index": j * 100,
                        "end_index": (j + 1) * 100 - 1,
                        "metadata": {
                            "importance": np.random.random(),
                            "sentiment": np.random.choice(["positive", "neutral", "negative"]),
                            "frame_db_id": frame_id,  # Store frame DB ID in chunk metadata
                            "airtable_record_id": airtable_id,  # Store Airtable ID for reference
                            "google_drive_reference": reference_id,  # Store reference ID for retrieval
                            "chunk_type": chunk_type,  # Type of chunk
                            "chunk_format": chunk_format,  # Format of chunk content
                            # Add a subset of Airtable data relevant to the chunk
                            "airtable_metadata": {
                                "Category": airtable_data.get("Category"),
                                "Tags": airtable_data.get("Tags"),
                                "Status": airtable_data.get("Status")
                            }
                        }
                    }
                    chunks.append(chunk)
                
                # Process chunks for this frame
                processed_chunk_refs = await process_chunks(
                    store=store,
                    frame_reference_id=reference_id,
                    frame_id=frame_id,
                    airtable_record_id=airtable_id,
                    chunks=chunks
                )
                
                chunk_reference_ids.extend(processed_chunk_refs)
        
        # Store the mapping between various IDs
        id_mapping = {
            "database_ids": frame_db_ids,
            "reference_ids": frame_reference_ids,
            "airtable_ids": frame_airtable_ids,
            "db_to_reference": dict(zip(frame_db_ids, frame_reference_ids)),
            "db_to_airtable": dict(zip(frame_db_ids, frame_airtable_ids)),
            "airtable_to_reference": dict(zip(frame_airtable_ids, frame_reference_ids))
        }
        
        logger.info(f"Frame ID to reference ID mapping: {id_mapping['db_to_reference']}")
        logger.info(f"Frame ID to Airtable ID mapping: {id_mapping['db_to_airtable']}")
        
        # Verify reference IDs for consistency
        logger.info("Verifying reference ID consistency")
        all_reference_ids = frame_reference_ids + chunk_reference_ids
        verification_results = await verify_reference_ids(
            store, 
            all_reference_ids, 
            id_mapping['db_to_reference']
        )
        
        consistent_count = sum(1 for result in verification_results.values() if result)
        logger.info(f"{consistent_count} out of {len(verification_results)} reference IDs are consistent")
        
        # Demonstrate chunk processing status checking
        if frame_airtable_ids:
            # Check processing status for the first frame
            await print_processing_status(store, frame_airtable_ids[0])
        
        # Search for similar embeddings using both embedding tables
        if chunk_reference_ids:
            logger.info("Demonstrating search in both embedding tables")
            
            # Use a sample text for search
            query_text = "Sample search query for testing embedding retrieval"
            logger.info(f"Searching with query: '{query_text}'")
            
            # Generate embedding for the search query
            query_embedding = generate_mock_embedding()
            
            # Search in regular chunk embeddings table
            regular_results = await store.search_embeddings(
                embedding=query_embedding,
                reference_type="chunk",
                table="default",
                limit=3
            )
            
            logger.info(f"Search results from regular embeddings table:")
            for idx, result in enumerate(regular_results, 1):
                logger.info(f"  {idx}. Chunk ID: {result.get('chunk_id')}, "
                            f"Reference ID: {result.get('reference_id')}, "
                            f"Similarity: {result.get('similarity'):.4f}")
            
            # Search in multimodal_embeddings_chunks table
            multimodal_results = await store.search_embeddings(
                embedding=query_embedding,
                reference_type="chunk",
                table="multimodal_chunks",
                limit=3
            )
            
            logger.info(f"Search results from multimodal_embeddings_chunks table:")
            for idx, result in enumerate(multimodal_results, 1):
                logger.info(f"  {idx}. Chunk ID: {result.get('chunk_id')}, "
                            f"Reference ID: {result.get('reference_id')}, "
                            f"Similarity: {result.get('similarity'):.4f}, "
                            f"Dimensions: {result.get('dimensions')}")
            
            # Verify that both tables contain the same chunks
            regular_ref_ids = [r.get('reference_id') for r in regular_results]
            multimodal_ref_ids = [r.get('reference_id') for r in multimodal_results]
            
            common_ids = set(regular_ref_ids).intersection(set(multimodal_ref_ids))
            logger.info(f"Number of common reference IDs in both tables: {len(common_ids)}")
        
        # Export data to CSV with all Airtable data and OCR results
        logger.info("Exporting data to CSV with Airtable data and OCR results")
        export_success = await export_to_csv(store)
        
        if export_success:
            logger.info("Successfully exported comprehensive data to CSV files")
            logger.info("CSV files include all Airtable metadata and OCR processing results")
            
            # Demonstrate using chunking data storage
            if len(chunk_reference_ids) > 0:
                # Get first chunk ID from our processed chunks
                sample_chunk_id = None
                for chunk_id, chunk in store.chunks.items():
                    sample_chunk_id = chunk_id
                    break
                    
                if sample_chunk_id:
                    logger.info(f"Demonstrating additional chunking data storage for chunk ID {sample_chunk_id}")
                    
                    # Store additional chunking metadata
                    chunking_data = {
                        "chunk_importance_score": 0.85,
                        "chunk_sentiment_score": 0.42,
                        "chunk_keywords": ["sample", "test", "metadata"],
                        "chunk_entities_extracted": ["Person A", "Organization B"],
                        "metadata": {
                            "processing_time_ms": 125,
                            "additional_metadata": {
                                "language_detected": "en",
                                "confidence": 0.92
                            }
                        }
                    }
                    
                    success = await store.store_chunking_data(
                        chunk_id=sample_chunk_id,
                        chunk_data=chunking_data
                    )
                    
                    if success:
                        logger.info(f"Successfully stored additional chunking data for chunk ID {sample_chunk_id}")
                        
                        # Get the updated chunk data
                        updated_chunk = store.chunks.get(sample_chunk_id, {})
                        logger.info("Updated chunk data includes:")
                        for key in chunking_data:
                            if key in updated_chunk:
                                logger.info(f"  {key}: {updated_chunk[key]}")
                                
                        # Verify metadata was updated
                        chunk_details = store.chunk_details.get(sample_chunk_id, {})
                        if "metadata" in chunk_details:
                            logger.info("Updated chunk metadata includes:")
                            for key, value in chunk_details["metadata"].items():
                                if isinstance(value, dict):
                                    logger.info(f"  {key}: {len(value)} fields")
                                else:
                                    logger.info(f"  {key}: {value}")
                    else:
                        logger.error(f"Failed to store additional chunking data")
        else:
            logger.error("Failed to export data to CSV")
        
        logger.info("Embedding workflow demonstration completed")
        
    except Exception as e:
        logger.error(f"Error in main workflow: {str(e)}")
    finally:
        # Close database connection
        if 'store' in locals():
            await store.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    asyncio.run(main()) 