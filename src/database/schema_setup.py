#!/usr/bin/env python3
"""
Database schema setup script for PostgreSQL with pgvector support.

This script creates the necessary schemas, tables, and extensions for the
frame embedding system, supporting both whole-frame embeddings and chunk embeddings.
"""

import os
import sys
import logging
import argparse
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("schema_setup")

# Database connection parameters from environment variables
DB_PARAMS = {
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'dbname': os.getenv('POSTGRES_DB')
}

# Schema definitions
SCHEMAS = [
    'content',    # For storing frame data and content
    'metadata',   # For storing embeddings and metadata
    'retrieval'   # For retrieval utilities like cached searches
]

# SQL statements for extensions
EXTENSIONS = [
    "CREATE EXTENSION IF NOT EXISTS pgvector;",
    "CREATE EXTENSION IF NOT EXISTS pg_trgm;",
    "CREATE EXTENSION IF NOT EXISTS hstore;",
]

# SQL statements for tables
TABLES = [
    # Content schema - Stores frame information
    """
    CREATE TABLE IF NOT EXISTS content.frames (
        id SERIAL PRIMARY KEY,
        frame_name TEXT NOT NULL,
        folder_path TEXT,
        folder_name TEXT,
        frame_timestamp TIMESTAMPTZ,
        creation_time TIMESTAMPTZ DEFAULT NOW(),
        google_drive_url TEXT,
        airtable_record_id TEXT,
        metadata JSONB,
        UNIQUE(frame_name, folder_path)
    );
    """,
    
    # Content schema - Stores chunk information
    """
    CREATE TABLE IF NOT EXISTS content.chunks (
        id SERIAL PRIMARY KEY,
        frame_id INTEGER REFERENCES content.frames(id) ON DELETE CASCADE,
        chunk_sequence_id INTEGER NOT NULL,
        chunk_text TEXT NOT NULL,
        creation_time TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE(frame_id, chunk_sequence_id)
    );
    """,
    
    # Metadata schema - Stores whole-frame embeddings
    """
    CREATE TABLE IF NOT EXISTS metadata.frame_embeddings (
        id UUID PRIMARY KEY,
        frame_id INTEGER REFERENCES content.frames(id) ON DELETE CASCADE,
        embedding vector(1024),
        model_name TEXT NOT NULL,
        creation_time TIMESTAMPTZ DEFAULT NOW()
    );
    """,
    
    # Metadata schema - Stores chunk embeddings
    """
    CREATE TABLE IF NOT EXISTS metadata.chunk_embeddings (
        id UUID PRIMARY KEY,
        chunk_id INTEGER REFERENCES content.chunks(id) ON DELETE CASCADE,
        embedding vector(1024),
        model_name TEXT NOT NULL,
        creation_time TIMESTAMPTZ DEFAULT NOW()
    );
    """,
    
    # Retrieval schema - Stores cached search results
    """
    CREATE TABLE IF NOT EXISTS retrieval.cached_searches (
        id SERIAL PRIMARY KEY,
        query_text TEXT NOT NULL,
        query_embedding vector(1024),
        results JSONB,
        model_name TEXT NOT NULL,
        creation_time TIMESTAMPTZ DEFAULT NOW(),
        expiration_time TIMESTAMPTZ
    );
    """
]

# SQL statements for indexes
INDEXES = [
    # Content indexes
    "CREATE INDEX IF NOT EXISTS idx_frames_frame_name ON content.frames (frame_name);",
    "CREATE INDEX IF NOT EXISTS idx_frames_folder_path ON content.frames (folder_path);",
    "CREATE INDEX IF NOT EXISTS idx_frames_airtable_id ON content.frames (airtable_record_id);",
    "CREATE INDEX IF NOT EXISTS idx_frames_metadata ON content.frames USING GIN (metadata jsonb_path_ops);",
    
    # Chunk indexes
    "CREATE INDEX IF NOT EXISTS idx_chunks_frame_id ON content.chunks (frame_id);",
    
    # Embedding indexes - using HNSW for efficient vector search
    """
    CREATE INDEX IF NOT EXISTS idx_frame_embeddings_vector ON metadata.frame_embeddings 
    USING hnsw (embedding vector_cosine_ops) 
    WITH (m = 16, ef_construction = 64);
    """,
    
    """
    CREATE INDEX IF NOT EXISTS idx_chunk_embeddings_vector ON metadata.chunk_embeddings 
    USING hnsw (embedding vector_cosine_ops) 
    WITH (m = 16, ef_construction = 64);
    """,
    
    # Cached search indexes
    "CREATE INDEX IF NOT EXISTS idx_cached_searches_query ON retrieval.cached_searches USING GIN (to_tsvector('english', query_text));"
]

# SQL statements for functions
FUNCTIONS = [
    # Function to search frame embeddings with cosine similarity
    """
    CREATE OR REPLACE FUNCTION search_frames(
        query_embedding vector(1024),
        similarity_threshold float,
        max_results integer
    )
    RETURNS TABLE (
        frame_id integer,
        frame_name text,
        similarity float
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            f.id as frame_id,
            f.frame_name,
            1 - (fe.embedding <=> query_embedding) as similarity
        FROM 
            metadata.frame_embeddings fe
        JOIN 
            content.frames f ON fe.frame_id = f.id
        WHERE 
            1 - (fe.embedding <=> query_embedding) > similarity_threshold
        ORDER BY 
            similarity DESC
        LIMIT 
            max_results;
    END;
    $$;
    """,
    
    # Function to search chunk embeddings with cosine similarity
    """
    CREATE OR REPLACE FUNCTION search_chunks(
        query_embedding vector(1024),
        similarity_threshold float,
        max_results integer
    )
    RETURNS TABLE (
        chunk_id integer,
        frame_id integer,
        frame_name text,
        chunk_text text,
        chunk_sequence_id integer,
        similarity float
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            c.id as chunk_id,
            f.id as frame_id,
            f.frame_name,
            c.chunk_text,
            c.chunk_sequence_id,
            1 - (ce.embedding <=> query_embedding) as similarity
        FROM 
            metadata.chunk_embeddings ce
        JOIN 
            content.chunks c ON ce.chunk_id = c.id
        JOIN 
            content.frames f ON c.frame_id = f.id
        WHERE 
            1 - (ce.embedding <=> query_embedding) > similarity_threshold
        ORDER BY 
            similarity DESC
        LIMIT 
            max_results;
    END;
    $$;
    """,
    
    # Function to search with metadata filters
    """
    CREATE OR REPLACE FUNCTION search_frames_with_metadata(
        query_embedding vector(1024),
        metadata_filters jsonb,
        similarity_threshold float,
        max_results integer
    )
    RETURNS TABLE (
        frame_id integer,
        frame_name text,
        similarity float
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            f.id as frame_id,
            f.frame_name,
            1 - (fe.embedding <=> query_embedding) as similarity
        FROM 
            metadata.frame_embeddings fe
        JOIN 
            content.frames f ON fe.frame_id = f.id
        WHERE 
            1 - (fe.embedding <=> query_embedding) > similarity_threshold
            AND (metadata_filters IS NULL OR f.metadata @> metadata_filters)
        ORDER BY 
            similarity DESC
        LIMIT 
            max_results;
    END;
    $$;
    """
]

def connect_db(admin_mode=False):
    """Connect to PostgreSQL database."""
    params = DB_PARAMS.copy()
    
    # Use 'postgres' database for admin operations if needed
    if admin_mode and 'dbname' in params:
        params['dbname'] = 'postgres'
    
    try:
        logger.info(f"Connecting to PostgreSQL database at {params['host']}:{params['port']}")
        conn = psycopg2.connect(**params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        logger.info("Database connection established")
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        sys.exit(1)

def execute_sql(conn, sql_statement, params=None):
    """Execute a SQL statement with parameters."""
    with conn.cursor() as cursor:
        try:
            cursor.execute(sql_statement, params)
            logger.debug(f"Executed SQL: {sql_statement}")
            return True
        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            logger.error(f"Failed SQL: {sql_statement}")
            return False

def setup_schemas(conn):
    """Create schemas if they don't exist."""
    for schema in SCHEMAS:
        schema_sql = sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema))
        if execute_sql(conn, schema_sql):
            logger.info(f"Schema '{schema}' created or already exists")
        else:
            logger.warning(f"Failed to create schema '{schema}'")

def setup_extensions(conn):
    """Create required PostgreSQL extensions."""
    for extension_sql in EXTENSIONS:
        if execute_sql(conn, extension_sql):
            extension_name = extension_sql.split()[3].strip(';')
            logger.info(f"Extension '{extension_name}' created or already exists")
        else:
            logger.warning(f"Failed to create extension: {extension_sql}")

def setup_tables(conn):
    """Create tables if they don't exist."""
    for table_sql in TABLES:
        if execute_sql(conn, table_sql):
            # Extract table name from SQL for logging
            table_name = table_sql.split('CREATE TABLE IF NOT EXISTS')[1].split('(')[0].strip()
            logger.info(f"Table '{table_name}' created or already exists")
        else:
            logger.warning(f"Failed to create table")

def setup_indexes(conn):
    """Create indexes if they don't exist."""
    for index_sql in INDEXES:
        if execute_sql(conn, index_sql):
            logger.info(f"Index created or already exists")
        else:
            logger.warning(f"Failed to create index")

def setup_functions(conn):
    """Create or replace database functions."""
    for function_sql in FUNCTIONS:
        if execute_sql(conn, function_sql):
            # Extract function name from SQL for logging
            function_name = function_sql.split('CREATE OR REPLACE FUNCTION')[1].split('(')[0].strip()
            logger.info(f"Function '{function_name}' created or updated")
        else:
            logger.warning(f"Failed to create function")

def main():
    """Main function to set up database schema."""
    parser = argparse.ArgumentParser(description='Set up PostgreSQL database schema')
    parser.add_argument('--admin', action='store_true', help='Connect as admin to create database')
    args = parser.parse_args()
    
    # Connect to database
    conn = connect_db(admin_mode=args.admin)
    
    try:
        # Set up database components
        setup_extensions(conn)
        setup_schemas(conn)
        setup_tables(conn)
        setup_indexes(conn)
        setup_functions(conn)
        
        logger.info("Database schema setup completed successfully")
    finally:
        conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    main() 