#!/usr/bin/env python3
"""
Minimalist RAG Intake API

This FastAPI application provides endpoints to receive frame data from n8n workflows
and temporarily store it for processing.

Usage:
  uvicorn main:app --host 0.0.0.0 --port 8777 --reload
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import json
import logging
from datetime import datetime
import uuid
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
log_dir = Path(os.getenv("LOGS_DIR", "./logs"))
log_dir.mkdir(exist_ok=True, parents=True)
log_file = log_dir / f"rag_intake_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)

logger = logging.getLogger("rag-intake")

# Ensure data directory exists
data_dir = Path(os.getenv("DATA_DIR", "./data"))
data_dir.mkdir(exist_ok=True, parents=True)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Data Intake API",
    description="API for receiving and processing frame data for RAG system",
    version=os.getenv("API_VERSION", "0.1.0")
)

# Data Models
class FrameData(BaseModel):
    folder_path: str
    file_name: str
    metadata: Dict[str, Any]
    content: Optional[str] = None
    embedding_id: Optional[str] = None

class FrameBatch(BaseModel):
    frames: List[FrameData]
    batch_id: Optional[str] = None

# In-memory storage (temporary solution)
processing_queue = []
processed_frames = {}

def save_frame_data(frame_data: Dict[str, Any]):
    """Save frame data to a JSON file"""
    # Extract folder and file names from the frame data
    folder_path = frame_data.get("folder_path", "")
    file_name = frame_data.get("file_name", "")
    
    # Create a filename based on folder and frame names
    if folder_path and file_name:
        # Extract just the folder name from the path
        folder_name = Path(folder_path).name
        
        # Create a subfolder based on the folder name without appending '_frames'
        subfolder_path = data_dir / folder_name
        subfolder_path.mkdir(exist_ok=True)
        
        # Clean up any path separators in the filename
        clean_file_name = Path(file_name).name
        
        # Remove file extension from frame filename
        frame_name_no_ext = Path(clean_file_name).stem
        
        # Create the new filename
        filename = f"{folder_name}_{frame_name_no_ext}.json"
        
        # Save to the subfolder
        data_file = subfolder_path / filename
    else:
        # Fallback to UUID if folder_path or file_name is missing
        filename = f"frame_{uuid.uuid4()}.json"
        data_file = data_dir / filename
    
    with open(data_file, "w") as f:
        json.dump(frame_data, f, indent=2)
    
    logger.info(f"Saved frame data to {data_file}")
    return str(data_file)

def process_frame_batch(batch: FrameBatch):
    """Background task to process frame batch"""
    batch_id = batch.batch_id or str(uuid.uuid4())
    logger.info(f"Processing batch {batch_id} with {len(batch.frames)} frames")
    
    for frame in batch.frames:
        try:
            # Store the frame data
            frame_dict = frame.dict()
            frame_dict["processed_at"] = datetime.now().isoformat()
            frame_dict["batch_id"] = batch_id
            
            # Save to file
            file_path = save_frame_data(frame_dict)
            
            # Update processed frames record
            processed_frames[f"{frame.folder_path}/{frame.file_name}"] = {
                "processed_at": frame_dict["processed_at"],
                "file_path": file_path,
                "batch_id": batch_id
            }
            
            logger.info(f"Processed frame: {frame.folder_path}/{frame.file_name}")
        except Exception as e:
            logger.error(f"Error processing frame {frame.folder_path}/{frame.file_name}: {str(e)}")

@app.post("/api/frames/batch", status_code=202)
async def receive_frames_batch(batch: FrameBatch, background_tasks: BackgroundTasks):
    """
    Receive a batch of frames for processing
    
    This endpoint accepts a batch of frame data and processes them in the background
    """
    if not batch.frames:
        raise HTTPException(status_code=400, detail="No frames provided in batch")
    
    # Generate batch ID if not provided
    if not batch.batch_id:
        batch.batch_id = str(uuid.uuid4())
    
    # Add to processing queue
    processing_queue.append(batch)
    
    # Start background processing
    background_tasks.add_task(process_frame_batch, batch)
    
    # Get folder name from first frame for response
    first_frame = batch.frames[0]
    folder_name = Path(first_frame.folder_path).name
    
    logger.info(f"Received batch {batch.batch_id} with {len(batch.frames)} frames from folder {folder_name}")
    
    return {
        "status": "accepted",
        "message": f"Processing {len(batch.frames)} frames in the background",
        "batch_id": batch.batch_id,
        "folder_name": folder_name,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def get_status():
    """Get the current status of the API"""
    return {
        "status": "operational",
        "version": os.getenv("API_VERSION", "0.1.0"),
        "queue_size": len(processing_queue),
        "processed_frames": len(processed_frames),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/frames/{folder_path}/{file_name}")
async def get_frame_status(folder_path: str, file_name: str):
    """Check if a specific frame has been processed"""
    frame_key = f"{folder_path}/{file_name}"
    if frame_key in processed_frames:
        return {
            "processed": True,
            "details": processed_frames[frame_key]
        }
    return {
        "processed": False,
        "message": "Frame not found in processed frames"
    }

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8777"))
    
    logger.info(f"Starting RAG Intake API on {host}:{port}")
    uvicorn.run(app, host=host, port=port)