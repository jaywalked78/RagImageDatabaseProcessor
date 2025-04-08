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
        register_vector(self.conn)
        return self.conn
        
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def check_connection(self):
        """Check if the connection is active."""
        return self.conn is not None and not self.conn.closed
    
    def get_connection(self):
        """Get the current connection, creating one if needed."""
        self._ensure_connection()
        return self.conn
    
    def _ensure_connection(self):
        """Ensure there is an active connection."""
        if not self.check_connection():
            self.connect()
            
    # Add methods for OCR data handling
    def insert_ocr_data(self, frame_id: str, ocr_data: Dict[str, Any]) -> bool:
        """
        Insert OCR data into the ocr_data table.
        
        Args:
            frame_id: Unique identifier for the frame
            ocr_data: Dictionary containing OCR data
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_connection()
        
        try:
            # Convert lists to array format
            topics = ocr_data.get('topics', [])
            content_types = ocr_data.get('content_types', [])
            urls = ocr_data.get('urls', [])
            
            query = """
                INSERT INTO ocr_data (
                    frame_id, raw_text, structured_data, is_flagged, 
                    sensitive_explanation, topics, content_types, urls,
                    word_count, char_count, processed_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
                )
                ON CONFLICT (frame_id) 
                DO UPDATE SET
                    raw_text = EXCLUDED.raw_text,
                    structured_data = EXCLUDED.structured_data,
                    is_flagged = EXCLUDED.is_flagged,
                    sensitive_explanation = EXCLUDED.sensitive_explanation,
                    topics = EXCLUDED.topics,
                    content_types = EXCLUDED.content_types,
                    urls = EXCLUDED.urls,
                    word_count = EXCLUDED.word_count,
                    char_count = EXCLUDED.char_count,
                    processed_at = CURRENT_TIMESTAMP
                RETURNING frame_id
            """
            
            params = (
                frame_id,
                ocr_data.get('raw_text', ''),
                Json(ocr_data),  # Store full structured data as JSONB
                ocr_data.get('is_flagged', False),
                ocr_data.get('sensitive_explanation', ''),
                topics,
                content_types,
                urls,
                ocr_data.get('word_count', 0),
                ocr_data.get('char_count', 0)
            )
            
            with db_cursor(self.conn, cursor_factory=psycopg2.extras.DictCursor, commit=True) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                
                if result:
                    logger.debug(f"Inserted OCR data for frame {frame_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error inserting OCR data for frame {frame_id}: {str(e)}")
            return False
            
    def get_ocr_data(self, frame_id: str) -> Optional[Dict[str, Any]]:
        """
        Get OCR data for a specific frame.
        
        Args:
            frame_id: Unique identifier for the frame
            
        Returns:
            Dictionary containing OCR data or None if not found
        """
        self._ensure_connection()
        
        try:
            query = """
                SELECT * FROM ocr_data WHERE frame_id = %s
            """
            
            with db_cursor(self.conn, cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(query, (frame_id,))
                result = cursor.fetchone()
                
                if result:
                    return dict(result)
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving OCR data for frame {frame_id}: {str(e)}")
            return None
            
    def update_embedding_with_ocr(self, doc_id: str, ocr_data: Dict[str, Any]) -> bool:
        """
        Update an existing embedding record with OCR data.
        
        Args:
            doc_id: Unique document ID for the embedding
            ocr_data: Dictionary containing OCR data
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_connection()
        
        try:
            query = """
                UPDATE embeddings
                SET ocr_data = %s,
                    ocr_text = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE doc_id = %s
                RETURNING doc_id
            """
            
            # Extract text for full-text search
            ocr_text = ocr_data.get('raw_text', '')
            if not ocr_text and 'paragraphs' in ocr_data:
                # Combine paragraphs if raw_text is not available
                ocr_text = ' '.join(ocr_data.get('paragraphs', []))
            
            params = (
                Json(ocr_data),  # Store full structured data as JSONB
                ocr_text,
                doc_id
            )
            
            with db_cursor(self.conn, cursor_factory=psycopg2.extras.DictCursor, commit=True) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                
                if result:
                    logger.debug(f"Updated embedding {doc_id} with OCR data")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error updating embedding {doc_id} with OCR data: {str(e)}")
            return False
    
    def search_ocr_text(self, search_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for frames containing specific OCR text.
        
        Args:
            search_text: Text to search for
            limit: Maximum number of results to return
            
        Returns:
            List of matching OCR data records
        """
        self._ensure_connection()
        
        try:
            query = """
                SELECT * FROM ocr_data
                WHERE to_tsvector('english', raw_text) @@ plainto_tsquery('english', %s)
                ORDER BY processed_at DESC
                LIMIT %s
            """
            
            with db_cursor(self.conn, cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute(query, (search_text, limit))
                results = cursor.fetchall()
                
                if results:
                    return [dict(row) for row in results]
                return []
                
        except Exception as e:
            logger.error(f"Error searching OCR data for '{search_text}': {str(e)}")
            return []
            
    def insert_frame_chunk(self, airtable_record_id: str, frame_path: str, 
                           chunk_sequence_id: int, chunk_text: str, 
                           full_metadata: dict, embedding: list,
                           ocr_data: Dict[str, Any] = None) -> Optional[uuid.UUID]:
        """
        Insert a frame chunk with embedding into the database.
        
        Args:
            airtable_record_id: ID of the record in Airtable
            frame_path: Path to the frame image file
            chunk_sequence_id: Sequence ID of the chunk
            chunk_text: Text content of the chunk
            full_metadata: Full metadata for the chunk
            embedding: Vector embedding for the chunk
            ocr_data: Optional OCR data for the chunk
            
        Returns:
            Generated UUID for the inserted record, or None on failure
        """
        self._ensure_connection()
        
        try:
            # Generate a unique ID for this document
            doc_id = str(uuid.uuid4())
            
            # Extract frame_id from metadata
            frame_id = full_metadata.get('FrameID', airtable_record_id)
            
            # Add OCR data to metadata if provided
            metadata_with_ocr = full_metadata.copy()
            if ocr_data:
                metadata_with_ocr['ocr_data'] = ocr_data
            
            query = """
                INSERT INTO embeddings (
                    doc_id, embedding, metadata, ocr_data, ocr_text, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                ) RETURNING doc_id
            """
            
            # Extract OCR text for full-text search
            ocr_text = ocr_data.get('raw_text', '') if ocr_data else ''
            
            params = (
                doc_id,
                embedding,
                Json(metadata_with_ocr),
                Json(ocr_data) if ocr_data else None,
                ocr_text
            )
            
            with db_cursor(self.conn, commit=True) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
                
                if result:
                    return uuid.UUID(result[0])
                return None
                
        except Exception as e:
            logger.error(f"Error inserting frame chunk for {frame_path}, chunk {chunk_sequence_id}: {str(e)}")
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