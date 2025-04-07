"""
Database connection handling for TheLogicLoomDB.
"""

import os
import logging
import psycopg2
import psycopg2.extras
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from contextlib import contextmanager
from psycopg2.extras import execute_values, Json
from pgvector.psycopg2 import register_vector
import uuid

from src.config.settings import DB_CONFIG, ConfigError

# Get a logger for this module
logger = logging.getLogger("logicLoom.db")


class DatabaseError(Exception):
    """Exception raised for database errors."""
    pass


def get_db_connection():
    """
    Create a new database connection.
    
    Returns:
        psycopg2 connection object
        
    Raises:
        DatabaseError: If connection fails
    """
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        logger.debug(f"Connected to PostgreSQL database at {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise DatabaseError(f"Database connection failed. Please check your database settings in .env file: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error connecting to database: {str(e)}")
        raise DatabaseError(f"Unexpected database error: {str(e)}")


@contextmanager
def db_cursor(conn=None, cursor_factory=None, commit=False):
    """
    Context manager for database cursor operations.
    
    Args:
        conn: Optional existing connection to use
        cursor_factory: Optional psycopg2 cursor factory class
        commit: Whether to commit the transaction on exit
        
    Yields:
        Database cursor object
        
    Raises:
        DatabaseError: If cursor creation fails
    """
    conn_created = False
    try:
        # Create new connection if one wasn't provided
        if conn is None:
            conn = get_db_connection()
            conn_created = True
        
        # Create cursor
        cursor = conn.cursor(cursor_factory=cursor_factory)
        
        # Yield the cursor for use
        yield cursor
        
        # Commit if requested
        if commit:
            conn.commit()
            
    except psycopg2.Error as e:
        logger.error(f"Database error: {str(e)}")
        if conn and not conn.closed:
            conn.rollback()
        raise DatabaseError(f"Database operation failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during database operation: {str(e)}")
        if conn and not conn.closed:
            conn.rollback()
        raise
    finally:
        # Close cursor if it exists
        if 'cursor' in locals() and cursor:
            cursor.close()
        
        # Close connection if we created it
        if conn_created and conn and not conn.closed:
            conn.close()


def execute_query(conn, query, params=None, fetch=False, fetch_one=False, cursor_factory=None):
    """
    Execute a database query with proper error handling.
    
    Args:
        conn: Database connection
        query: SQL query string
        params: Optional query parameters
        fetch: Whether to fetch results
        fetch_one: Whether to fetch a single row
        cursor_factory: Optional psycopg2 cursor factory class
        
    Returns:
        Query results if fetch=True, otherwise None
    """
    try:
        with db_cursor(conn, cursor_factory=cursor_factory) as cursor:
            # Execute the query
            cursor.execute(query, params)
            
            # Return results if requested
            if fetch:
                if fetch_one:
                    return cursor.fetchone()
                else:
                    return cursor.fetchall()
            
            # Commit the transaction
            conn.commit()
            
    except psycopg2.Error as e:
        logger.error(f"Database query error: {str(e)}")
        logger.debug(f"Query: {query}")
        logger.debug(f"Params: {params}")
        if conn and not conn.closed:
            conn.rollback()
        raise DatabaseError(f"Database query failed: {str(e)}")


def init_db():
    """
    Initialize database tables if they don't exist.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_db_connection()
        
        # Enable pgvector extension
        execute_query(conn, "CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create tables
        execute_query(conn, """
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                duration INTEGER,
                folder_path TEXT,
                source_url TEXT,
                tool_used TEXT[],
                topics TEXT[],
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        execute_query(conn, """
            CREATE TABLE IF NOT EXISTS frames (
                frame_id TEXT PRIMARY KEY,
                video_id TEXT NOT NULL REFERENCES videos(video_id),
                timestamp FLOAT NOT NULL,
                frame_number INTEGER,
                image_url TEXT,
                sequence_index INTEGER,
                folder_name TEXT,
                file_name TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        execute_query(conn, """
            CREATE TABLE IF NOT EXISTS frame_details (
                frame_id TEXT PRIMARY KEY REFERENCES frames(frame_id),
                description TEXT,
                summary TEXT,
                tools_used TEXT[],
                actions_performed TEXT[],
                technical_details JSONB,
                workflow_stage TEXT,
                context_relationship TEXT,
                tags TEXT[],
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        execute_query(conn, """
            CREATE TABLE IF NOT EXISTS embeddings (
                embedding_id SERIAL PRIMARY KEY,
                reference_id TEXT NOT NULL,
                reference_type TEXT NOT NULL,
                model_name TEXT NOT NULL,
                text_content TEXT,
                embedding_vector VECTOR(1024),
                metadata JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create indexes
        execute_query(conn, "CREATE INDEX IF NOT EXISTS idx_embeddings_reference_id ON embeddings(reference_id);")
        execute_query(conn, "CREATE INDEX IF NOT EXISTS idx_embeddings_reference_type ON embeddings(reference_type);")
        execute_query(conn, "CREATE INDEX IF NOT EXISTS idx_frames_video_id ON frames(video_id);")
        
        # Create vector index using IVFFlat
        try:
            execute_query(conn, "CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING ivfflat (embedding_vector vector_l2_ops) WITH (lists = 100);")
        except DatabaseError:
            logger.warning("Could not create IVFFlat index on embedding_vector. Using default index instead.")
            execute_query(conn, "CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING hnsw (embedding_vector vector_l2_ops);")
        
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()


class DatabaseClient:
    def __init__(self):
        self.conn = None

    def connect(self):
        """Connect to the database."""
        self.conn = get_db_connection()

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def check_connection(self):
        """Check if the database connection is active."""
        return self.conn and not self.conn.closed

    def get_connection(self):
        """Get the current database connection."""
        return self.conn
    
    def _ensure_connection(self):
        """Ensure that a connection exists before executing queries."""
        if self.conn is None or self.conn.closed:
            logger.warning("Database connection is closed. Reconnecting...")
            self.connect()
        if self.conn is None:
            raise ConnectionError("Failed to establish database connection")

    def insert_frame_chunk(self, airtable_record_id: str, frame_path: str, 
                           chunk_sequence_id: int, chunk_text: str, 
                           full_metadata: dict, embedding: list) -> Optional[uuid.UUID]:
        """Insert a single frame chunk into the database."""
        self._ensure_connection()
        query = """
        INSERT INTO frame_chunks (airtable_record_id, frame_path, chunk_sequence_id, chunk_text, full_metadata, embedding)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        try:
            with self.conn.cursor() as cur:
                register_vector(cur) # Ensure vector type is registered for the cursor
                cur.execute(query, (airtable_record_id, frame_path, chunk_sequence_id, chunk_text, Json(full_metadata), embedding))
                result = cur.fetchone()
                self.conn.commit()
                logger.info(f"Inserted chunk {chunk_sequence_id} for Airtable record {airtable_record_id}")
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Error inserting frame chunk: {e}", exc_info=True)
            self.conn.rollback() # Rollback on error
            return None

    def batch_insert_frame_chunks(self, chunk_data: List[Tuple]) -> bool:
        """
        Insert multiple frame chunks in a single batch.
        
        Args:
            chunk_data: List of tuples, each tuple containing:
                        (airtable_record_id, frame_path, chunk_sequence_id, 
                         chunk_text, full_metadata (dict), embedding (list))
        """
        self._ensure_connection()
        query = """
        INSERT INTO frame_chunks (airtable_record_id, frame_path, chunk_sequence_id, chunk_text, full_metadata, embedding)
        VALUES %s
        ON CONFLICT (airtable_record_id, chunk_sequence_id) DO NOTHING; -- Optionally handle conflicts
        """
        # Prepare data with Json wrapper for metadata
        prepared_data = [
            (d[0], d[1], d[2], d[3], Json(d[4]), d[5]) for d in chunk_data
        ]
        try:
            with self.conn.cursor() as cur:
                register_vector(cur) # Ensure vector type is registered
                execute_values(cur, query, prepared_data, page_size=100) # Use execute_values for batch insert
                self.conn.commit()
                logger.info(f"Successfully batch inserted {len(chunk_data)} frame chunks.")
                return True
        except Exception as e:
            logger.error(f"Error during batch insert of frame chunks: {e}", exc_info=True)
            self.conn.rollback()
            return False

    def find_similar_chunks(self, query_embedding: list, top_k: int = 5, filters: Optional[Dict] = None) -> List[Dict]:
        """
        Find similar frame chunks based on embedding similarity.
        Optionally filter by metadata fields.
        """
        self._ensure_connection()
        
        # Base query for similarity search
        # Using <=> for cosine distance (closer to 0 is more similar)
        base_query = """
        SELECT id, airtable_record_id, frame_path, chunk_sequence_id, chunk_text, full_metadata, embedding <=> %s AS distance
        FROM frame_chunks
        """
        
        params = [query_embedding]
        where_clauses = []

        # Add metadata filters if provided
        if filters:
            for key, value in filters.items():
                # Example: filter by a top-level key in full_metadata JSONB
                # Adjust path `->>` based on your metadata structure
                where_clauses.append(f"(full_metadata ->> %s) = %s")
                params.extend([key, str(value)]) # Ensure value is string for ->>

        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)

        # Add ordering and limit
        base_query += " ORDER BY distance ASC LIMIT %s;"
        params.append(top_k)
        
        results = []
        try:
            with self.conn.cursor() as cur:
                register_vector(cur)
                cur.execute(base_query, tuple(params))
                rows = cur.fetchall()
                
                # Get column names for creating dictionaries
                colnames = [desc[0] for desc in cur.description]
                results = [dict(zip(colnames, row)) for row in rows]
                
            logger.info(f"Found {len(results)} similar chunks.")
            return results
        except Exception as e:
            logger.error(f"Error finding similar chunks: {e}", exc_info=True)
            self.conn.rollback()
            return []

    # --- Existing methods (insert_frame, insert_embedding, find_similar_embeddings, etc.) --- 
    # These might need to be updated or removed later depending on the final pipeline design.
    # For now, we keep them to avoid breaking existing code that might use them.

    def insert_frame(self, drive_file_id: str, file_name: str, video_id: Optional[str] = None,
                     frame_number: Optional[int] = None, timestamp: Optional[float] = None) -> Optional[int]:
        # ... (keep existing implementation for now)
        pass # Replace pass with actual existing code

    def insert_embedding(self, frame_id: int, embedding: list, model_version: str) -> Optional[int]:
        # ... (keep existing implementation for now)
        pass # Replace pass with actual existing code

    def find_similar_embeddings(self, query_embedding: list, top_k: int = 5) -> List[Tuple]:
        # ... (keep existing implementation for now)
        pass # Replace pass with actual existing code

    def get_frame_by_drive_id(self, drive_file_id: str) -> Optional[Tuple]:
        # ... (keep existing implementation for now)
        pass # Replace pass with actual existing code

    def get_embedding_by_frame_id(self, frame_id: int) -> Optional[Tuple]:
        # ... (keep existing implementation for now)
        pass # Replace pass with actual existing code

    def get_all_frames(self, limit: int = 100, offset: int = 0) -> List[Tuple]:
        # ... (keep existing implementation for now)
        pass # Replace pass with actual existing code

    def count_frames(self) -> int:
        # ... (keep existing implementation for now)
        pass # Replace pass with actual existing code

    def count_embeddings(self) -> int:
        # ... (keep existing implementation for now)
        pass # Replace pass with actual existing code

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Tuple]:
        # ... (keep existing implementation for now)
        pass # Replace pass with actual existing code

    def execute_non_query(self, query: str, params: Optional[tuple] = None) -> bool:
        # ... (keep existing implementation for now)
        pass # Replace pass with actual existing code 