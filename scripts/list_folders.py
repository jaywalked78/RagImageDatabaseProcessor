#!/usr/bin/env python3
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    pool = await asyncpg.create_pool(
        host=os.getenv('SUPABASE_DB_HOST', 'aws-0-us-east-1.pooler.supabase.com'),
        port=os.getenv('SUPABASE_DB_PORT', '5432'),
        database=os.getenv('SUPABASE_DB_NAME', 'postgres'),
        user=os.getenv('SUPABASE_DB_USER'),
        password=os.getenv('SUPABASE_DB_PASSWORD')
    )
    
    # Query all distinct folder names
    result = await pool.fetch('SELECT DISTINCT folder_name FROM content.frames')
    print("Available folders:")
    for i, row in enumerate(result):
        print(f"{i+1}. {row['folder_name']}")
    
    await pool.close()

if __name__ == "__main__":
    asyncio.run(main()) 