#!/usr/bin/env python3

import os
import sys
import logging
import asyncio
import asyncpg
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("check")

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-us-east-1.pooler.supabase.com')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')

async def check_frames_and_constraints():
    """Check the content.frames table and foreign key constraints in metadata schema."""
    
    # Connect to the database
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    try:
        # Check if content.frames exists
        exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = 'content' AND table_name = 'frames')"
        )
        
        if not exists:
            logger.error("Table content.frames does not exist")
            return
        
        # Check frames in content.frames
        frames = await conn.fetch("SELECT * FROM content.frames LIMIT 5")
        logger.info(f"Found {len(frames)} frames in content.frames (showing max 5):")
        for frame in frames:
            logger.info(f"  {frame}")
        
        # Get total count of frames
        count = await conn.fetchval("SELECT COUNT(*) FROM content.frames")
        logger.info(f"Total frames in content.frames: {count}")
        
        # Get foreign key constraints in metadata schema
        constraints = await conn.fetch("""
            SELECT tc.constraint_name, tc.table_name, kcu.column_name, 
                   ccu.table_schema AS foreign_table_schema,
                   ccu.table_name AS foreign_table_name, 
                   ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' 
              AND tc.table_schema = 'metadata'
        """)
        
        logger.info("\nForeign key constraints in metadata schema:")
        for constraint in constraints:
            logger.info(f"  {constraint['table_name']}.{constraint['column_name']} -> "
                        f"{constraint['foreign_table_schema']}.{constraint['foreign_table_name']}.{constraint['foreign_column_name']} "
                        f"(constraint: {constraint['constraint_name']})")
    
    finally:
        # Close the connection
        await conn.close()

async def main():
    """Main function."""
    try:
        await check_frames_and_constraints()
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 