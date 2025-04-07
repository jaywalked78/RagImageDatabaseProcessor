"""
FastAPI microservice for vector similarity search using TheLogicLoomDB with pgvector.
This service integrates with VoyageAI for embeddings generation and implements
both simple nearest neighbor search and CP-RAG (multi-probe) approach.
"""

import os
import json
import numpy as np
import requests
import time
from io import BytesIO
from datetime import datetime
from typing import List, Optional, Dict, Any, Union, Tuple
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks, Query, Body, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import psycopg2.extras
from sklearn.clusters import KMeans
import uvicorn
from PIL import Image
from voyageai import Client
import uuid
import io
import tempfile
import asyncio
import logging

# Import configuration and logging
from src.config.settings import (
    PORT, 
    HOST, 
    VOYAGE_API_KEY, 
    EMBEDDING_DIM,
    verify_config,
    debug_config,
    API_ROOT_PATH,
    DEBUG,
    SIMILARITY_THRESHOLD
)
from src.config.logging_config import configure_logging

# Import database functions
from src.db.connection import get_db_connection, execute_query, init_db, DatabaseError
from src.db.database_client import DatabaseClient
from src.models.embedding_client import get_embeddings, get_embedding_dimension

# Import integrations
from src.integrations.airtable import AirtableClient
from src.integrations.google_drive import GoogleDriveClient
from src.integrations.batch_processor import BatchProcessor

# Configure logging
logger = configure_logging()

# Verify configuration
config_status = verify_config()
if not all(config_status.values()):
    logger.warning("Some configuration components are missing or invalid")
    logger.debug(f"Configuration status: {config_status}")

# Initialize VoyageAI client
voyage_client = Client(api_key=VOYAGE_API_KEY)
logger.info("VoyageAI client initialized")

# Initialize FastAPI app
app = FastAPI(
    title="TheLogicLoom Vector Search API", 
    description="Vector similarity search using PostgreSQL with pgvector extension",
    version="1.0.0",
    root_path=API_ROOT_PATH,
    debug=DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests and responses."""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Log request
    logger.info(f"Request {request_id}: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response {request_id}: Status {response.status_code}, Processed in {process_time:.4f}s")
    
    return response

# Pydantic models for database tables (moved to models.py in a production app)
class VideoBase(BaseModel):
    video_id: str
    title: str
    description: Optional[str] = None
    duration: Optional[int] = None
    folder_path: Optional[str] = None
    source_url: Optional[str] = None
    tool_used: Optional[List[str]] = None
    topics: Optional[List[str]] = None

class FrameBase(BaseModel):
    frame_id: str
    video_id: str
    timestamp: float
    frame_number: Optional[int] = None
    image_url: Optional[str] = None
    sequence_index: Optional[int] = None
    folder_name: Optional[str] = None
    file_name: Optional[str] = None

class FrameDetails(BaseModel):
    frame_id: str
    description: Optional[str] = None
    summary: Optional[str] = None
    tools_used: Optional[List[str]] = None
    actions_performed: Optional[List[str]] = None
    technical_details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    workflow_stage: Optional[str] = None
    context_relationship: Optional[str] = None
    tags: Optional[List[str]] = None

class TextEmbedding(BaseModel):
    reference_id: str
    reference_type: str
    text_content: str
    model_name: str = "voyage-large-2"

class MultimodalEmbedding(BaseModel):
    reference_id: str
    reference_type: str
    text_content: Optional[str] = None
    image_url: str
    model_name: str = "voyage-large-2"

# Pydantic models for request/response validation
class IngestItem(BaseModel):
    doc_id: str
    image_url: Optional[str] = None
    text: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Optional detailed fields for comprehensive storage
    video_id: Optional[str] = None
    frame_number: Optional[int] = None
    timestamp: Optional[float] = None
    folder_name: Optional[str] = None
    file_name: Optional[str] = None
    description: Optional[str] = None
    summary: Optional[str] = None
    tools_used: Optional[List[str]] = None
    actions_performed: Optional[List[str]] = None
    technical_details: Optional[Dict[str, Any]] = None
    workflow_stage: Optional[str] = None
    context_relationship: Optional[str] = None
    tags: Optional[List[str]] = None

class IngestRequest(BaseModel):
    items: List[IngestItem]

class SearchRequest(BaseModel):
    query_text: str
    cp_rag: bool = False
    num_probes: int = 3
    neighbors_per_probe: int = 10
    filters: Optional[Dict[str, Any]] = None
    reference_types: Optional[List[str]] = ["all"]  # Can specify which types to search: "frame", "video", etc.
    
    @validator('reference_types')
    def validate_reference_types(cls, v):
        allowed_types = ["all", "frame", "video", "segment", "idea", "external_source"]
        for ref_type in v:
            if ref_type not in allowed_types:
                raise ValueError(f"Invalid reference type: {ref_type}. Allowed values: {allowed_types}")
        return v

class SearchResult(BaseModel):
    reference_id: str
    reference_type: str
    metadata: Dict[str, Any]
    score: float
    text_content: Optional[str] = None
    image_url: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]

class HealthResponse(BaseModel):
    status: str = "ok"
    db_connected: bool = False
    voyage_api_connected: bool = False
    version: str = "1.0.0"

# Batch Processing Related Pydantic Models
class BatchJobParams(BaseModel):
    """Parameters for configuring a batch job."""
    processing_mode: str = Field(default="Batch", description="Processing mode: 'Batch' or 'Sequential'")
    batch_size: int = Field(default=20, description="Number of frames to process in each batch")
    max_frames: Optional[int] = Field(default=None, description="Maximum number of frames to process (None for all)")
    update_airtable: bool = Field(default=True, description="Whether to update the processed status in Airtable")
    processed_field: str = Field(default="Processed", description="Field name in Airtable that tracks processing status")
    download_to_disk: bool = Field(default=False, description="Whether to download files to disk or memory")
    folder_path_field: str = Field(default="FolderPath", description="Field name to sort by in Sequential mode")

class BatchJobStatus(BaseModel):
    """Status of a batch job."""
    job_id: str
    status: str
    total_frames: int = 0
    successful: int = 0
    failed: int = 0
    elapsed_seconds: float = 0.0
    started_at: str
    completed_at: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "completed",
                "total_frames": 100,
                "successful": 95,
                "failed": 5,
                "elapsed_seconds": 120.5,
                "started_at": "2023-11-01T12:00:00Z",
                "completed_at": "2023-11-01T12:02:00Z"
            }
        }

# Global storage for batch job statuses
batch_jobs = {}

# Application startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and other resources on startup."""
    logger.info("Starting TheLogicLoom API service")
    init_db()  # Initialize database tables if they don't exist

# Health check endpoint
@app.get("/healthcheck", response_model=HealthResponse)
async def healthcheck():
    """Health check endpoint to verify API and dependencies are working."""
    response = HealthResponse()
    
    # Check database connection
    try:
        conn = get_db_connection()
        result = execute_query(conn, "SELECT 1", fetch=True, fetch_one=True)
        response.db_connected = result is not None and result[0] == 1
        conn.close()
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        response.db_connected = False
    
    # Check VoyageAI API connection
    try:
        # Simple API call to check if credentials are valid
        response_data = voyage_client.embed(
            model="voyage-large-2",
            texts=["Hello world"],
        )
        response.voyage_api_connected = "embeddings" in response_data and len(response_data["embeddings"]) > 0
    except Exception as e:
        logger.error(f"VoyageAI API health check failed: {str(e)}")
        response.voyage_api_connected = False
    
    # Update overall status if any dependency is down
    if not (response.db_connected and response.voyage_api_connected):
        response.status = "degraded"
    
    return response

# Helper function to load image from URL
async def load_image_from_url(image_url: str):
    """
    Load an image from a URL.
    
    Args:
        image_url: URL of the image to load
        
    Returns:
        PIL Image object
    """
    try:
        response = requests.get(image_url)
        return Image.open(BytesIO(response.content))
    except Exception as e:
        logger.error(f"Error loading image from URL {image_url}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error loading image: {str(e)}")

# Generate embedding using VoyageAI
async def generate_embedding(text: Optional[str] = None, image: Optional[Image.Image] = None):
    """
    Generate an embedding using VoyageAI's API.
    
    Args:
        text: Optional text to embed
        image: Optional image to embed
        
    Returns:
        List of embedding values
    """
    try:
        if text and image:
            # Multimodal embedding
            byte_arr = BytesIO()
            image.save(byte_arr, format='JPEG')
            byte_arr = byte_arr.getvalue()
            
            response = voyage_client.embed(
                model="voyage-large-2",
                texts=[text],
                images=[byte_arr]
            )
        elif text:
            # Text-only embedding
            response = voyage_client.embed(
                model="voyage-large-2",
                texts=[text]
            )
        elif image:
            # Image-only embedding
            byte_arr = BytesIO()
            image.save(byte_arr, format='JPEG')
            byte_arr = byte_arr.getvalue()
            
            response = voyage_client.embed(
                model="voyage-large-2",
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
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

# Frame processing function for batch processor
async def process_single_frame(img: Image.Image, metadata: Dict[str, Any]) -> bool:
    """
    Process a single frame downloaded from Google Drive.
    Stores frame data in database and generates embeddings.
    
    Args:
        img: The image data
        metadata: Metadata about the frame
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create a SimpleIngestItem with the frame data
        class SimpleIngestItem:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        
        # Extract fields from metadata
        frame_id = f"frame_{metadata.get('video_id')}_{metadata.get('frame_number')}"
        
        # Create a simplified version of IngestItem
        item = SimpleIngestItem(
            doc_id=frame_id,
            text=metadata.get('title', ''),
            video_id=metadata.get('video_id'),
            frame_number=metadata.get('frame_number'),
            timestamp=metadata.get('timestamp'),
            metadata=metadata,
        )
        
        # Generate embedding from the frame
        embedding = await generate_embedding(text=item.text, image=img)
        
        # Connect to database
        conn = get_db_connection()
        
        # Store the frame data
        try:
            # First, ensure video exists
            if item.video_id:
                result = execute_query(
                    conn, 
                    "SELECT 1 FROM videos WHERE video_id = %s", 
                    params=(item.video_id,), 
                    fetch=True, 
                    fetch_one=True
                )
                
                if not result:
                    # Create a minimal video record
                    execute_query(
                        conn, 
                        """
                        INSERT INTO videos (video_id, title)
                        VALUES (%s, %s)
                        ON CONFLICT (video_id) DO NOTHING
                        """, 
                        params=(item.video_id, f"Video {item.video_id}")
                    )
            
            # Store frame data
            execute_query(
                conn,
                """
                INSERT INTO frames (
                    frame_id, video_id, timestamp, frame_number
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (frame_id) DO UPDATE
                SET 
                    video_id = EXCLUDED.video_id,
                    timestamp = EXCLUDED.timestamp,
                    frame_number = EXCLUDED.frame_number,
                    updated_at = CURRENT_TIMESTAMP
                """,
                params=(
                    frame_id,
                    item.video_id,
                    item.timestamp,
                    item.frame_number
                )
            )
            
            # Store embedding
            execute_query(
                conn,
                """
                INSERT INTO embeddings (
                    reference_id, reference_type, model_name, text_content, embedding_vector, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                params=(
                    frame_id,
                    "frame",
                    "voyage-large-2",
                    item.text,
                    embedding,
                    json.dumps(metadata)
                )
            )
            
            logger.info(f"Successfully processed and stored frame {frame_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing frame data: {str(e)}")
            return False
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Error in process_single_frame: {str(e)}")
        return False

# Batch processing job implementation
async def run_batch_job(job_id: str, params: BatchJobParams):
    """
    Background task to process a batch of frames.
    
    Args:
        job_id: Unique identifier for this job
        params: Parameters for the batch job
    """
    # Update job status to running
    batch_jobs[job_id].update({"status": "running"})
    
    try:
        # Initialize clients
        airtable_client = AirtableClient()
        google_drive_client = GoogleDriveClient()
        
        # Process according to selected mode
        if params.processing_mode.lower() == "sequential":
            # Import the sequential processor
            from src.integrations.sequential_processor import SequentialProcessor
            
            # Create sequential processor
            processor = SequentialProcessor(
                process_frame_func=process_single_frame,
                airtable_client=airtable_client,
                google_drive_client=google_drive_client,
                download_to_disk=params.download_to_disk
            )
            
            # Process frames sequentially
            result = await processor.process_frames(
                max_frames=params.max_frames,
                processed_field=params.processed_field,
                update_airtable=params.update_airtable,
                folder_path_field=params.folder_path_field
            )
        else:
            # Use batch processor (default)
            from src.integrations.batch_processor import BatchProcessor
            
            # Create batch processor
            processor = BatchProcessor(
                process_frame_func=process_single_frame,
                airtable_client=airtable_client,
                google_drive_client=google_drive_client,
                download_to_disk=params.download_to_disk
            )
            
            # Process batch
            result = await processor.process_batch(
                batch_size=params.batch_size,
                max_frames=params.max_frames,
                processed_field=params.processed_field,
                update_airtable=params.update_airtable
            )
        
        # Update job status
        batch_jobs[job_id].update({
            "status": "completed",
            "total_frames": result["total_frames"],
            "successful": result["successful"],
            "failed": result["failed"],
            "elapsed_seconds": result["elapsed_seconds"],
            "completed_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in batch job {job_id}: {str(e)}")
        batch_jobs[job_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })

# Batch processing API endpoints
@app.post("/batch/process", response_model=BatchJobStatus)
async def start_batch_processing(
    background_tasks: BackgroundTasks,
    params: BatchJobParams = Body(...)
):
    """
    Start a new batch processing job.
    
    Args:
        params: Parameters for the batch job
        
    Returns:
        Batch job status
    """
    # Generate a job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    job_status = {
        "job_id": job_id,
        "status": "pending",
        "total_frames": 0,
        "successful": 0,
        "failed": 0,
        "elapsed_seconds": 0.0,
        "started_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    # Store job status
    batch_jobs[job_id] = job_status
    
    # Start batch processing in the background
    background_tasks.add_task(run_batch_job, job_id, params)
    
    return BatchJobStatus(**job_status)

@app.get("/batch/status/{job_id}", response_model=BatchJobStatus)
async def get_batch_job_status(job_id: str):
    """Get the status of a batch job."""
    if job_id not in batch_jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return BatchJobStatus(**batch_jobs[job_id])

@app.get("/batch/list", response_model=List[BatchJobStatus])
async def list_batch_jobs():
    """List all batch jobs."""
    return [BatchJobStatus(**job) for job in batch_jobs.values()]

# Dependency for getting DB client
# This ensures cleanup even if request handling fails
def get_db():
    db = DatabaseClient()
    try:
        db.connect()
        yield db
    finally:
        db.close()

# --- Pydantic Models for API --- 

class SearchQuery(BaseModel):
    query_text: Optional[str] = Field(default=None, description="Textual part of the search query.")
    top_k: int = Field(default=5, description="Number of similar results to return.")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters to apply (key-value pairs).")
    similarity_threshold: Optional[float] = Field(default=None, description=f"Optional similarity threshold (cosine distance). Defaults to config value: {SIMILARITY_THRESHOLD}")

class ChunkResult(BaseModel):
    chunk_id: str # UUID as string
    airtable_record_id: str
    frame_path: str
    chunk_sequence_id: int
    chunk_text: Optional[str]
    distance: float
    full_metadata: Optional[Dict[str, Any]] # Optionally return full metadata

class SearchResponse(BaseModel):
    query_text_used: Optional[str]
    image_provided: bool
    results: List[ChunkResult]
    message: Optional[str] = None

# --- API Endpoints --- 

@app.get("/health", tags=["General"])
async def health_check():
    """Check the health of the API."""
    # TODO: Add checks for DB connection, embedding model availability etc.
    return {"status": "ok"}

@app.post("/search/multimodal", response_model=SearchResponse, tags=["Search"])
async def search_multimodal(
    query_text: Optional[str] = Query(None, description="Textual part of the search query."), 
    image_file: Optional[UploadFile] = File(None, description="Optional image file for the search query."),
    top_k: int = Query(5, description="Number of similar results to return."),
    filters: Optional[str] = Query(None, description="JSON string for metadata filters (key-value pairs)."),
    similarity_threshold: Optional[float] = Query(None, description=f"Optional similarity threshold (cosine distance). Defaults to config value: {SIMILARITY_THRESHOLD}"),
    db: DatabaseClient = Depends(get_db)
):
    """
    Perform multimodal similarity search based on text and/or image query.
    Retrieves relevant chunks from the database.
    """
    query_image_bytes: Optional[bytes] = None
    image_provided = False
    parsed_filters: Optional[Dict] = None

    if not query_text and not image_file:
        raise HTTPException(status_code=400, detail="Please provide either query text or an image file.")

    # Process image file if provided
    if image_file:
        if not image_file.content_type.startswith("image/"):
             raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
        try:
            query_image_bytes = await image_file.read()
            # Optional: Validate image size/format here before sending to embedder
            Image.open(io.BytesIO(query_image_bytes)) # Basic validation: can Pillow open it?
            image_provided = True
        except Exception as e:
             logger.error(f"Failed to read or validate uploaded image: {e}", exc_info=True)
             raise HTTPException(status_code=400, detail=f"Could not process uploaded image: {e}")
        finally:
             await image_file.close()

    # Process filters if provided (expecting JSON string)
    if filters:
        try:
            parsed_filters = json.loads(filters)
            if not isinstance(parsed_filters, dict):
                 raise ValueError("Filters must be a JSON object (key-value pairs).")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid format for filters. Please provide a valid JSON string.")
        except ValueError as e:
             raise HTTPException(status_code=400, detail=str(e))

    # --- Generate Query Embedding --- 
    # Prepare input for get_embeddings: List[Tuple[List[str], Optional[bytes]]]
    # For a query, the text list might contain just the single query text
    query_input_text = [query_text] if query_text else []
    query_embedding_input = [(query_input_text, query_image_bytes)]
    
    logger.debug(f"Generating query embedding for text: '{query_text}', image_provided: {image_provided}")
    query_embedding_list = get_embeddings(query_embedding_input)
    
    if not query_embedding_list or len(query_embedding_list) != 1:
        logger.error("Failed to generate query embedding or unexpected result format.")
        raise HTTPException(status_code=500, detail="Failed to generate query embedding.")
        
    query_embedding = query_embedding_list[0]
    logger.debug("Query embedding generated successfully.")

    # --- Perform Database Search --- 
    effective_threshold = similarity_threshold if similarity_threshold is not None else SIMILARITY_THRESHOLD
    logger.debug(f"Searching for top {top_k} chunks with threshold {effective_threshold} and filters: {parsed_filters}")
    
    similar_chunks_raw = db.find_similar_chunks(
        query_embedding=query_embedding, 
        top_k=top_k, 
        filters=parsed_filters
    )

    # --- Process and Filter Results --- 
    search_results = []
    for chunk in similar_chunks_raw:
        # Apply similarity threshold (distance is cosine distance, lower is better)
        if chunk['distance'] <= (1.0 - effective_threshold): # Convert similarity threshold to distance threshold if needed, assuming distance is 1-similarity
             # Adjust based on actual distance metric used (e.g. L2, inner product)
             # If using <=> (cosine dist): distance is 0 (identical) to 2 (opposite). 
             # Threshold might need interpretation. If `find_similar_chunks` returns cosine *similarity*, then filter > threshold. 
             # Let's assume <=> returns cosine distance. 
             # SIMILARITY_THRESHOLD = 0.75 means distance <= 0.25 is desired.
             # For now, let's use the distance directly as returned by the function.
             # A threshold check might be better implemented *within* find_similar_chunks using WHERE distance <= ...
             # Let's refine the distance/similarity handling.
             # Assuming SIMILARITY_THRESHOLD is cosine similarity (0 to 1), higher is better.
             # And assuming db.find_similar_chunks returns 'distance' which is 1 - similarity.
            if chunk['distance'] <= (1.0 - effective_threshold):
                 search_results.append(ChunkResult(
                    chunk_id=str(chunk['id']),
                    airtable_record_id=chunk['airtable_record_id'],
                    frame_path=chunk['frame_path'],
                    chunk_sequence_id=chunk['chunk_sequence_id'],
                    chunk_text=chunk.get('chunk_text'), # Use .get for safety
                    distance=chunk['distance'],
                    full_metadata=chunk.get('full_metadata') # Optionally include metadata
                ))
            else:
                 logger.debug(f"Chunk {chunk['id']} skipped due to distance {chunk['distance']} > threshold distance {(1.0 - effective_threshold)}")

    # TODO: Implement Re-ranking or result grouping if needed based on RAG plan

    return SearchResponse(
        query_text_used=query_text,
        image_provided=image_provided,
        results=search_results
    )

# Main entry point
async def run():
    """Run the application."""
    config = uvicorn.Config(app, host=HOST, port=int(PORT))
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(run()) 