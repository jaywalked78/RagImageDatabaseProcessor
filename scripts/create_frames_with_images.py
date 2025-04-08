#!/usr/bin/env python3
"""
Script to create frames in the database from images in a directory.
"""

import os
import sys
import logging
import asyncio
import datetime
import re
import glob
import pathlib
from dotenv import load_dotenv
import asyncpg

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("frame_creator")

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-us-east-1.pooler.supabase.com')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')

# Constants
FRAMES_DIR = os.path.expanduser("~/Videos/screenRecordings/screen_recording_2025_02_20_at_10_59_16_am")
FOLDER_NAME = "screen_recording_2025_02_20_at_10_59_16_am"
FRAME_PATTERN = "frame_*.jpg"

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

async def get_existing_frames(pool, folder_name):
    """Get the list of frames that already exist in the database for the folder."""
    async with pool.acquire() as conn:
        logger.info(f"Checking existing frames in folder: {folder_name}")
        
        # Query to get frames in the folder
        frames = await conn.fetch("""
            SELECT frame_id FROM content.frames
            WHERE folder_name = $1
        """, folder_name)
        
        existing_frames = set(frame["frame_id"] for frame in frames)
        logger.info(f"Found {len(existing_frames)} existing frames in the database for folder {folder_name}")
        return existing_frames

async def create_frames(pool, frames_dir, folder_name, existing_frames):
    """Create frames in the database from images in the directory."""
    # Find all frame image files
    pattern = os.path.join(frames_dir, FRAME_PATTERN)
    frame_files = glob.glob(pattern)
    
    if not frame_files:
        logger.warning(f"No frame files found matching pattern {pattern}")
        return []
    
    logger.info(f"Found {len(frame_files)} frame files in directory {frames_dir}")
    
    # Sort by frame number
    frame_files.sort(key=lambda x: int(re.search(r'frame_0*(\d+)\.jpg', os.path.basename(x)).group(1)))
    
    # Create frames in database
    created_frames = []
    async with pool.acquire() as conn:
        for frame_file in frame_files:
            frame_id = os.path.basename(frame_file)
            
            if frame_id in existing_frames:
                logger.info(f"Frame {frame_id} already exists in database")
                continue
            
            # Create the frame in the database
            file_name = frame_id
            image_url = frame_file
            video_id = None
            
            # Use timestamp as float instead of datetime
            timestamp = datetime.datetime.now().timestamp()
            
            try:
                await conn.execute("""
                    INSERT INTO content.frames (
                        frame_id, folder_name, file_name, image_url, video_id, timestamp
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6
                    )
                """, frame_id, folder_name, file_name, image_url, video_id, timestamp)
                
                created_frames.append(frame_id)
                logger.info(f"Created frame {frame_id} in database")
            except Exception as e:
                logger.error(f"Error creating frame {frame_id}: {str(e)}")
    
    logger.info(f"Created {len(created_frames)} new frames in database")
    return created_frames

async def main():
    """Main function."""
    logger.info(f"Starting to create frames from directory: {FRAMES_DIR}")
    
    # Check if directory exists
    if not os.path.isdir(FRAMES_DIR):
        logger.error(f"Directory does not exist: {FRAMES_DIR}")
        return False
    
    try:
        # Create connection pool
        pool = await create_connection_pool()
        
        # Get existing frames
        existing_frames = await get_existing_frames(pool, FOLDER_NAME)
        
        # Create frames
        created_frames = await create_frames(pool, FRAMES_DIR, FOLDER_NAME, existing_frames)
        
        # Close the connection pool
        await pool.close()
        logger.info("Frame creation completed. PostgreSQL connection pool closed.")
        
        if created_frames:
            logger.info(f"Successfully created {len(created_frames)} new frames")
            logger.info("You can now process these frames using process_earliest_frames.py")
        else:
            logger.info("No new frames were created")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during frame creation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 