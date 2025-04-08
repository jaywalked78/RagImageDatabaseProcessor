#!/usr/bin/env python3
"""
Script to check embedding vectors in Supabase database.
Retrieves a sample embedding vector and displays its dimensions and values.
"""

import os
import sys
import logging
import asyncio
import json
from dotenv import load_dotenv
import asyncpg
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("vector_checker")

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('SUPABASE_DB_HOST', 'aws-0-us-east-1.pooler.supabase.com')
DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
DB_USER = os.getenv('SUPABASE_DB_USER')
DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD')

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

async def check_vector_column(pool):
    """Determine the name of the embedding vector column."""
    async with pool.acquire() as conn:
        columns = await conn.fetch("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'embeddings' AND table_name = 'multimodal_embeddings_chunks'
        """)
        
        available_columns = [col['column_name'] for col in columns]
        logger.info(f"Available columns in embeddings.multimodal_embeddings_chunks: {', '.join(available_columns)}")
        
        # Try different possible column names for embedding vectors
        possible_vector_columns = ['embedding_vector', 'embedding', 'vector', 'content_vector']
        for col in possible_vector_columns:
            if col in available_columns:
                logger.info(f"Found embedding vector column: {col}")
                return col
        
        logger.error("No embedding vector column found in table")
        return None

async def check_vector_data_type(pool, column_name):
    """Check the data type of the embedding vector column."""
    async with pool.acquire() as conn:
        data_type = await conn.fetchval(f"""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'embeddings' 
            AND table_name = 'multimodal_embeddings_chunks'
            AND column_name = '{column_name}'
        """)
        
        logger.info(f"Embedding vector column '{column_name}' has data type: {data_type}")
        return data_type

async def get_sample_vector(pool, column_name):
    """Retrieve a sample embedding vector and analyze it."""
    async with pool.acquire() as conn:
        try:
            # First try retrieving as an array
            vector_data = await conn.fetchval(f"""
                SELECT {column_name}
                FROM embeddings.multimodal_embeddings_chunks
                WHERE {column_name} IS NOT NULL
                LIMIT 1
            """)
            
            if vector_data is not None:
                if isinstance(vector_data, list):
                    # Handle standard PostgreSQL array
                    logger.info(f"Retrieved vector with {len(vector_data)} dimensions")
                    
                    # Display first 10 values and last 10 values
                    if len(vector_data) > 20:
                        first_values = vector_data[:10]
                        last_values = vector_data[-10:]
                        logger.info(f"First 10 values: {first_values}")
                        logger.info(f"Last 10 values: {last_values}")
                    else:
                        logger.info(f"Full vector: {vector_data}")
                    
                    # Basic statistics
                    np_vector = np.array(vector_data)
                    logger.info(f"Vector mean: {np.mean(np_vector)}")
                    logger.info(f"Vector std: {np.std(np_vector)}")
                    logger.info(f"Vector min: {np.min(np_vector)}")
                    logger.info(f"Vector max: {np.max(np_vector)}")
                    
                    return vector_data
                else:
                    # Handle pgvector or other custom types
                    logger.info(f"Retrieved vector data of type {type(vector_data)}")
                    vector_str = str(vector_data)
                    logger.info(f"Vector raw data (first 100 chars): {vector_str[:100]}...")
                    
                    # Parse pgvector format: typically looks like "[val1,val2,...]"
                    # Remove any leading/trailing brackets and split by comma
                    try:
                        # Clean the string to handle pgvector format
                        clean_str = vector_str.strip()
                        if clean_str.startswith('[') and clean_str.endswith(']'):
                            clean_str = clean_str[1:-1]  # Remove brackets
                        elif clean_str.startswith('(') and clean_str.endswith(')'):
                            clean_str = clean_str[1:-1]  # Remove parentheses
                            
                        # Split by comma and convert to float
                        values = [float(x.strip()) for x in clean_str.split(',')]
                        
                        logger.info(f"Successfully parsed vector with {len(values)} dimensions")
                        
                        # Display sample values
                        if len(values) > 20:
                            first_values = values[:10]
                            last_values = values[-10:]
                            logger.info(f"First 10 values: {first_values}")
                            logger.info(f"Last 10 values: {last_values}")
                        else:
                            logger.info(f"Full vector: {values}")
                        
                        # Calculate statistics
                        np_vector = np.array(values)
                        logger.info(f"Vector mean: {np.mean(np_vector)}")
                        logger.info(f"Vector std: {np.std(np_vector)}")
                        logger.info(f"Vector min: {np.min(np_vector)}")
                        logger.info(f"Vector max: {np.max(np_vector)}")
                        logger.info(f"Vector L2 norm: {np.linalg.norm(np_vector)}")
                        
                        # Check if vector is normalized (L2 norm ≈ 1.0)
                        norm = np.linalg.norm(np_vector)
                        if 0.99 <= norm <= 1.01:
                            logger.info("Vector appears to be normalized (L2 norm ≈ 1.0)")
                        else:
                            logger.info(f"Vector is not normalized (L2 norm = {norm})")
                        
                        return values
                    except Exception as parse_error:
                        logger.error(f"Error parsing vector string: {str(parse_error)}")
                        logger.info("Trying alternative parsing method...")
                        
                        # Try alternative parsing for different formats
                        try:
                            # Remove any non-numeric characters except for decimal points, minus signs and commas
                            import re
                            clean_str = re.sub(r'[^\d\-\.,]', '', vector_str)
                            # Replace multiple commas with a single comma
                            clean_str = re.sub(r',+', ',', clean_str)
                            # Remove leading/trailing commas
                            clean_str = clean_str.strip(',')
                            
                            values = [float(x.strip()) for x in clean_str.split(',')]
                            
                            logger.info(f"Alternative parsing successful with {len(values)} dimensions")
                            
                            # Calculate statistics
                            np_vector = np.array(values)
                            logger.info(f"Vector mean: {np.mean(np_vector)}")
                            logger.info(f"Vector std: {np.std(np_vector)}")
                            
                            return values
                        except Exception as alt_error:
                            logger.error(f"Alternative parsing also failed: {str(alt_error)}")
                            return None
            else:
                logger.warning(f"No vector data found in column '{column_name}'")
                return None
        except Exception as e:
            logger.error(f"Error retrieving vector data: {str(e)}")
            
            # Try alternative approach for pgvector format
            try:
                logger.info("Trying alternative query for pgvector format...")
                vector_str = await conn.fetchval(f"""
                    SELECT {column_name}::text
                    FROM embeddings.multimodal_embeddings_chunks
                    WHERE {column_name} IS NOT NULL
                    LIMIT 1
                """)
                
                if vector_str:
                    logger.info(f"Retrieved vector as string: {vector_str[:100]}...")
                    
                    # Try to parse the string
                    try:
                        # Remove brackets if present
                        clean_str = vector_str.strip()
                        if clean_str.startswith('[') and clean_str.endswith(']'):
                            clean_str = clean_str[1:-1]
                        elif clean_str.startswith('(') and clean_str.endswith(')'):
                            clean_str = clean_str[1:-1]
                            
                        # Split by comma and convert to float
                        values = [float(x.strip()) for x in clean_str.split(',')]
                        
                        logger.info(f"Successfully parsed vector with {len(values)} dimensions")
                        
                        # Calculate statistics
                        np_vector = np.array(values)
                        logger.info(f"Vector mean: {np.mean(np_vector)}")
                        logger.info(f"Vector std: {np.std(np_vector)}")
                        logger.info(f"Vector L2 norm: {np.linalg.norm(np_vector)}")
                        
                        return values
                    except Exception as parse_error:
                        logger.error(f"Error parsing vector string: {str(parse_error)}")
                        return None
                
                return None
            except Exception as e2:
                logger.error(f"Error with alternative query: {str(e2)}")
                return None

async def count_vectors_by_dimension(pool, column_name):
    """Count how many vectors exist by dimension."""
    async with pool.acquire() as conn:
        try:
            # Create a temporary function to get vector dimensions if it doesn't exist
            await conn.execute("""
                CREATE OR REPLACE FUNCTION temp_vector_length(v anyelement) RETURNS INTEGER AS $$
                BEGIN
                    -- Try different approaches based on the type
                    BEGIN
                        RETURN array_length(v, 1);
                    EXCEPTION WHEN OTHERS THEN
                        -- For pgvector, try string conversion and counting
                        BEGIN
                            RETURN (length(v::text) - length(replace(v::text, ',', ''))) + 1;
                        EXCEPTION WHEN OTHERS THEN
                            RETURN NULL;
                        END;
                    END;
                END;
                $$ LANGUAGE plpgsql;
            """)
            
            # Query to count vectors by dimension
            results = await conn.fetch(f"""
                WITH vector_dims AS (
                    SELECT embedding_id, temp_vector_length({column_name}) as dim
                    FROM embeddings.multimodal_embeddings_chunks
                    WHERE {column_name} IS NOT NULL
                )
                SELECT dim, COUNT(*) as count
                FROM vector_dims
                GROUP BY dim
                ORDER BY dim
            """)
            
            if results:
                logger.info("Vector dimensions distribution:")
                for row in results:
                    logger.info(f"Dimension {row['dim']}: {row['count']} vectors")
            else:
                logger.warning("Could not determine vector dimensions distribution")
                
            # Clean up temporary function
            await conn.execute("DROP FUNCTION IF EXISTS temp_vector_length(anyelement);")
            
        except Exception as e:
            logger.error(f"Error counting vectors by dimension: {str(e)}")

async def main():
    """Main function."""
    logger.info("Starting embedding vector verification...")
    
    try:
        # Create connection pool
        pool = await create_connection_pool()
        
        # Check for vector column
        vector_column = await check_vector_column(pool)
        if not vector_column:
            logger.error("No vector column found. Exiting.")
            return
        
        # Check vector data type
        await check_vector_data_type(pool, vector_column)
        
        # Get a sample vector
        await get_sample_vector(pool, vector_column)
        
        # Count vectors by dimension
        await count_vectors_by_dimension(pool, vector_column)
        
        # Close the connection pool
        await pool.close()
        logger.info("PostgreSQL connection pool closed")
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        
if __name__ == "__main__":
    asyncio.run(main()) 