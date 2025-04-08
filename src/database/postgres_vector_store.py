#!/usr/bin/env python3
"""
PostgresVectorStore module for storing and retrieving embeddings from PostgreSQL.
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple

import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
import numpy as np
from dotenv import load_dotenv
from pathlib import Path

import asyncpg
import dotenv
import uuid

# Load environment variables
load_dotenv()
dotenv.load_dotenv()

# PostgreSQL connection parameters
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB = os.environ.get("POSTGRES_DB")

# Configure logging
logger = logging.getLogger("database")

class PostgresVectorStore:
    """
    PostgreSQL vector store for storing embeddings and frame data.
    Supports pgvector operations.
    """
    
    def __init__(self):
        """Initialize the PostgreSQL vector store."""
        self.connection_pool = None
        self.embedding_dim = int(os.getenv('EMBEDDING_DIM', 1024))
        self.connected = False
        self.vector_dimension = int(os.getenv("VECTOR_DIMENSION", "1024"))
        self.embedding_distance_threshold = float(os.getenv("EMBEDDING_DISTANCE_THRESHOLD", "0.2"))
    
    async def connect(self) -> bool:
        """Connect to the PostgreSQL database."""
        if self.connected and self.connection_pool:
            return True
        
        # Get connection parameters from environment
        host = os.getenv('POSTGRES_HOST')
        port = os.getenv('POSTGRES_PORT')
        database = os.getenv('POSTGRES_DB')
        user = os.getenv('POSTGRES_USER')
        password = os.getenv('POSTGRES_PASS')
        
        # Check if all parameters are available
        if not all([host, port, database, user, password]):
            logger.warning("Incomplete PostgreSQL connection information")
            return False
        
        try:
            # Create connection pool
            dsn = f"postgres://{user}:{password}@{host}:{port}/{database}"
            self.connection_pool = await asyncpg.create_pool(dsn=dsn)
            self.connected = True
            
            logger.info(f"Connected to PostgreSQL database at {host}:{port}/{database}")
            
            # Ensure schema and tables are set up
            await self._ensure_database_setup()
            
            return True
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL database: {e}")
            self.connected = False
            return False
    
    async def _ensure_connected(self) -> bool:
        """Ensure there is a connection to the database."""
        if not self.connected or not self.connection_pool:
            return await self.connect()
        return True
    
    async def _ensure_database_setup(self) -> None:
        """Ensure the database has the necessary schemas, extensions, and tables."""
        if not await self._ensure_connected():
            return

        async with self.connection_pool.acquire() as conn:
            # Create schemas if they don't exist
            await conn.execute("""
                CREATE SCHEMA IF NOT EXISTS content;
                CREATE SCHEMA IF NOT EXISTS metadata;
                CREATE SCHEMA IF NOT EXISTS embeddings;
            """)
            
            # Create pgvector extension if it doesn't exist
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Ensure tables exist
            await self._ensure_frames_table(conn)
            await self._ensure_chunks_table(conn)
            await self._ensure_frame_details_table(conn)
            await self._ensure_chunk_details_table(conn)
            await self._ensure_process_frames_chunks_table(conn)  # New table for processing info
            await self._ensure_embeddings_table(conn)
            
            logger.info("Database schemas and tables verified")

    async def _ensure_frames_table(self, conn) -> None:
        """Ensure the content.frames table exists."""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS content.frames (
                id SERIAL PRIMARY KEY,
                frame_name TEXT NOT NULL,
                folder_path TEXT NOT NULL,
                folder_name TEXT NOT NULL,
                frame_timestamp TIMESTAMP,
                google_drive_url TEXT,
                airtable_record_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS frames_frame_name_idx ON content.frames(frame_name);
            CREATE INDEX IF NOT EXISTS frames_folder_name_idx ON content.frames(folder_name);
            CREATE INDEX IF NOT EXISTS frames_airtable_id_idx ON content.frames(airtable_record_id);
        """)

    async def _ensure_process_frames_chunks_table(self, conn) -> None:
        """Ensure the metadata.process_frames_chunks table exists."""
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS metadata.process_frames_chunks (
                id SERIAL PRIMARY KEY,
                frame_id INTEGER REFERENCES content.frames(id),
                chunk_id INTEGER REFERENCES content.chunks(id),
                airtable_record_id TEXT,
                processing_status TEXT,
                chunk_type TEXT,
                chunk_format TEXT,
                processing_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processing_metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS process_chunks_frame_id_idx ON metadata.process_frames_chunks(frame_id);
            CREATE INDEX IF NOT EXISTS process_chunks_chunk_id_idx ON metadata.process_frames_chunks(chunk_id);
            CREATE INDEX IF NOT EXISTS process_chunks_airtable_id_idx ON metadata.process_frames_chunks(airtable_record_id);
            CREATE INDEX IF NOT EXISTS process_chunks_status_idx ON metadata.process_frames_chunks(processing_status);
        """)

    async def store_process_chunk_data(
        self,
        frame_id: int,
        chunk_id: int,
        airtable_record_id: str,
        processing_status: str = "processed",
        chunk_type: str = "text",
        chunk_format: str = "plain",
        processing_metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Store processing information for a frame-chunk pair.
        
        Args:
            frame_id: ID of the frame
            chunk_id: ID of the chunk
            airtable_record_id: ID of the corresponding Airtable record
            processing_status: Status of the processing (e.g., "processed", "failed")
            chunk_type: Type of the chunk (e.g., "text", "image")
            chunk_format: Format of the chunk (e.g., "plain", "markdown")
            processing_metadata: Additional metadata about the processing
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not await self._ensure_connected():
            return False
        
        try:
            async with self.connection_pool.acquire() as conn:
                # Check if entry already exists
                exists = await conn.fetchval("""
                    SELECT EXISTS(
                        SELECT 1 FROM metadata.process_frames_chunks 
                        WHERE frame_id = $1 AND chunk_id = $2
                    )
                """, frame_id, chunk_id)
                
                if exists:
                    # Update existing entry
                    await conn.execute("""
                        UPDATE metadata.process_frames_chunks
                        SET 
                            airtable_record_id = $3,
                            processing_status = $4,
                            chunk_type = $5,
                            chunk_format = $6,
                            processing_metadata = $7,
                            processing_timestamp = CURRENT_TIMESTAMP,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE frame_id = $1 AND chunk_id = $2
                    """, frame_id, chunk_id, airtable_record_id, processing_status, 
                        chunk_type, chunk_format, processing_metadata or {})
                    
                    logger.info(f"Updated processing data for frame ID {frame_id}, chunk ID {chunk_id}")
                else:
                    # Insert new entry
                    await conn.execute("""
                        INSERT INTO metadata.process_frames_chunks
                        (frame_id, chunk_id, airtable_record_id, processing_status, 
                         chunk_type, chunk_format, processing_metadata)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """, frame_id, chunk_id, airtable_record_id, processing_status,
                        chunk_type, chunk_format, processing_metadata or {})
                    
                    logger.info(f"Stored processing data for frame ID {frame_id}, chunk ID {chunk_id}")
                
                return True
                    
        except Exception as e:
            logger.error(f"Error storing process data for frame ID {frame_id}, chunk ID {chunk_id}: {str(e)}")
            return False
    
    async def get_chunk_processing_status(self, airtable_record_id: str) -> List[Dict[str, Any]]:
        """
        Get processing status for all chunks associated with an Airtable record.
        
        Args:
            airtable_record_id: ID of the Airtable record
            
        Returns:
            List of dictionaries with processing status information
        """
        if not await self._ensure_connected():
            return []
        
        try:
            async with self.connection_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        pfc.id,
                        pfc.frame_id,
                        pfc.chunk_id,
                        pfc.processing_status,
                        pfc.chunk_type,
                        pfc.chunk_format,
                        pfc.processing_timestamp,
                        f.frame_name,
                        f.folder_name,
                        c.chunk_sequence_id,
                        c.chunk_text
                    FROM metadata.process_frames_chunks pfc
                    JOIN content.frames f ON pfc.frame_id = f.id
                    JOIN content.chunks c ON pfc.chunk_id = c.id
                    WHERE pfc.airtable_record_id = $1
                    ORDER BY f.id, c.chunk_sequence_id
                """, airtable_record_id)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting processing status for Airtable ID {airtable_record_id}: {str(e)}")
            return []
    
    async def store_frame(self, 
                         frame_name: str, 
                         folder_path: Optional[str] = None,
                         folder_name: Optional[str] = None,
                         frame_timestamp: Optional[str] = None,
                         google_drive_url: Optional[str] = None,
                         airtable_record_id: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """Store frame information and return frame ID."""
        if not await self._ensure_connected():
            return None
        
        try:
            async with self.connection_pool.acquire() as conn:
                # Insert or update frame
                frame_id = await conn.fetchval("""
                INSERT INTO content.frames (
                    frame_name, folder_path, folder_name, frame_timestamp, 
                    google_drive_url, airtable_record_id, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (frame_name, folder_path) DO UPDATE SET
                    folder_name = $3,
                    frame_timestamp = $4,
                    google_drive_url = $5,
                    airtable_record_id = $6,
                    metadata = $7
                    RETURNING id
                """, frame_name, folder_path, folder_name, frame_timestamp, 
                   google_drive_url, airtable_record_id, 
                   json.dumps(metadata) if metadata else None)
                
                # Create reference_id in the format "folder_name/frame_name"
                reference_id = f"{folder_name}/{frame_name}" if folder_name else frame_name
                
                # Insert or update frame_details_full
                await conn.execute("""
                INSERT INTO metadata.frame_details_full (frame_id, reference_id)
                VALUES ($1, $2)
                ON CONFLICT (frame_id) DO UPDATE SET
                    reference_id = $2,
                    updated_at = CURRENT_TIMESTAMP
                """, frame_id, reference_id)
                
                logger.info(f"Stored frame information for '{frame_name}' with ID {frame_id}")
                return frame_id
                    
        except Exception as e:
            logger.error(f"Error storing frame '{frame_name}': {e}")
            return None
    
    async def store_chunk(
        self,
        frame_reference_id: str,
        chunk_text: str,
        chunk_sequence_id: int,
        chunk_start_index: int = None,
        chunk_end_index: int = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[int]:
        """
        Store chunk details in the database using a frame reference ID.
        
        Args:
            frame_reference_id: Reference ID of the parent frame
            chunk_text: Text content of the chunk
            chunk_sequence_id: Sequence ID of the chunk
            chunk_start_index: Start index of the chunk in the source text
            chunk_end_index: End index of the chunk in the source text
            metadata: Additional metadata for the chunk
            
        Returns:
            int: Chunk ID if successful, None otherwise
        """
        if not await self._ensure_connected():
            return None
        
        try:
            # Create reference_id for chunk in the standard format
            chunk_reference_id = f"{frame_reference_id}/chunk_{chunk_sequence_id}"
            
            async with self.connection_pool.acquire() as conn:
                # Get frame_id from reference_id
                frame_id = await conn.fetchval("""
                    SELECT f.id 
                    FROM content.frames f
                    JOIN metadata.frame_details_full fd ON f.id = fd.frame_id
                    WHERE fd.reference_id = $1
                """, frame_reference_id)
                
                if not frame_id:
                    logger.error(f"Frame with reference_id {frame_reference_id} not found")
                    return None
                
                # Insert chunk record
                chunk_id = await conn.fetchval("""
                    INSERT INTO content.chunks 
                    (frame_id, chunk_sequence_id, chunk_text, chunk_start_index, chunk_end_index)
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING id
                """, frame_id, chunk_sequence_id, chunk_text, chunk_start_index, chunk_end_index)
                
                if not chunk_id:
                    logger.error(f"Failed to insert chunk {chunk_sequence_id} for frame {frame_reference_id}")
                    return None
                
                # Insert chunk details in metadata schema with consistent reference_id
                await conn.execute("""
                    INSERT INTO metadata.frame_details_chunk 
                    (chunk_id, reference_id, chunk_sequence_id, metadata)
                    VALUES ($1, $2, $3, $4)
                """, chunk_id, chunk_reference_id, chunk_sequence_id, metadata or {})
                
                logger.info(f"Stored chunk {chunk_sequence_id} with ID {chunk_id} and reference_id {chunk_reference_id}")
                return chunk_id
                
        except Exception as e:
            logger.error(f"Error storing chunk for frame {frame_reference_id}: {str(e)}")
            return None
    
    async def store_frame_embedding(self,
                                  frame_id: int,
                                  embedding: List[float],
                                   model_name: str) -> Optional[str]:
        """Store a frame embedding and return the embedding ID."""
        if not await self._ensure_connected():
            return None
        
        try:
            # Generate a UUID for the embedding
            embedding_id = str(uuid.uuid4())
            
            async with self.connection_pool.acquire() as conn:
                # Get frame information and reference_id
                frame_info = await conn.fetchrow("""
                SELECT f.frame_name, f.folder_name, f.google_drive_url, fdf.reference_id
                FROM content.frames f
                LEFT JOIN metadata.frame_details_full fdf ON f.id = fdf.frame_id
                WHERE f.id = $1
                """, frame_id)
                
                if not frame_info:
                    logger.error(f"Frame with ID {frame_id} not found")
                    return None
                
                # Store in metadata.frame_embeddings
                await conn.execute("""
                INSERT INTO metadata.frame_embeddings (id, frame_id, embedding, model_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE SET 
                    embedding = $3,
                    model_name = $4,
                    creation_time = CURRENT_TIMESTAMP
                """, embedding_id, frame_id, embedding, model_name)
                
                # Store in embeddings.multimodal_embeddings
                await conn.execute("""
                INSERT INTO embeddings.multimodal_embeddings (
                    embedding_id, reference_id, reference_type, 
                    text_content, image_url, embedding, model_name
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (embedding_id) DO UPDATE SET
                    reference_id = $2,
                    text_content = $4,
                    image_url = $5,
                    embedding = $6,
                    model_name = $7,
                    updated_at = CURRENT_TIMESTAMP
                """, embedding_id, frame_info['reference_id'], 'frame', 
                   None, frame_info['google_drive_url'], embedding, model_name)
                
                logger.info(f"Stored frame embedding for frame ID {frame_id} with embedding ID {embedding_id}")
                return embedding_id
                
        except Exception as e:
            logger.error(f"Error storing frame embedding for frame ID {frame_id}: {e}")
            return None
    
    async def store_chunk_embedding(self,
                                  chunk_id: int,
                                  embedding: List[float],
                                   model_name: str) -> Optional[str]:
        """Store a chunk embedding and return the embedding ID."""
        if not await self._ensure_connected():
            return None
        
        try:
            # Generate a UUID for the embedding
            embedding_id = str(uuid.uuid4())
            
            async with self.connection_pool.acquire() as conn:
                # Get chunk information and reference_id
                chunk_info = await conn.fetchrow("""
                SELECT c.frame_id, c.chunk_sequence_id, c.chunk_text, fdc.reference_id
                FROM content.chunks c
                LEFT JOIN metadata.frame_details_chunk fdc ON c.id = fdc.chunk_id
                WHERE c.id = $1
                """, chunk_id)
                
                if not chunk_info:
                    logger.error(f"Chunk with ID {chunk_id} not found")
                    return None
                
                # Store in metadata.chunk_embeddings
                await conn.execute("""
                INSERT INTO metadata.chunk_embeddings (id, chunk_id, embedding, model_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE SET 
                    embedding = $3,
                    model_name = $4,
                    creation_time = CURRENT_TIMESTAMP
                """, embedding_id, chunk_id, embedding, model_name)
                
                # Store in embeddings.multimodal_embeddings
                await conn.execute("""
                INSERT INTO embeddings.multimodal_embeddings (
                    embedding_id, reference_id, reference_type, 
                    text_content, image_url, embedding, model_name
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (embedding_id) DO UPDATE SET
                    reference_id = $2,
                    text_content = $4,
                    embedding = $6,
                    model_name = $7,
                    updated_at = CURRENT_TIMESTAMP
                """, embedding_id, chunk_info['reference_id'], 'chunk', 
                   chunk_info['chunk_text'], None, embedding, model_name)
                
                logger.info(f"Stored chunk embedding for chunk ID {chunk_id} with embedding ID {embedding_id}")
                return embedding_id
                
        except Exception as e:
            logger.error(f"Error storing chunk embedding for chunk ID {chunk_id}: {e}")
            return None
    
    async def search_frame_embeddings(self, 
                          query_embedding: List[float],
                          similarity_threshold: float = 0.7,
                          limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar frame embeddings."""
        if not await self._ensure_connected():
            return []
        
        try:
            async with self.connection_pool.acquire() as conn:
                results = await conn.fetch("""
                SELECT 
                    mfe.id as embedding_id,
                    f.id as frame_id,
                    f.frame_name,
                    f.folder_name,
                    f.google_drive_url,
                    fdf.reference_id,
                    f.airtable_record_id,
                    1 - (mfe.embedding <=> $1) as similarity
                FROM 
                    metadata.frame_embeddings mfe
                INNER JOIN 
                    content.frames f ON mfe.frame_id = f.id
                LEFT JOIN
                    metadata.frame_details_full fdf ON f.id = fdf.frame_id
                WHERE 
                    1 - (mfe.embedding <=> $1) > $2
                ORDER BY 
                    similarity DESC
                LIMIT $3
                """, query_embedding, similarity_threshold, limit)
                
                return [dict(r) for r in results]
                
        except Exception as e:
            logger.error(f"Error searching frame embeddings: {e}")
            return []
    
    async def search_chunk_embeddings(self, 
                          query_embedding: List[float],
                          similarity_threshold: float = 0.7,
                                    limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar chunk embeddings."""
        if not await self._ensure_connected():
            return []
        
        try:
            async with self.connection_pool.acquire() as conn:
                results = await conn.fetch("""
                SELECT 
                    mce.id as embedding_id,
                    c.id as chunk_id,
                    c.frame_id,
                    c.chunk_sequence_id,
                    c.chunk_text,
                    fdc.reference_id,
                    1 - (mce.embedding <=> $1) as similarity
                FROM 
                    metadata.chunk_embeddings mce
                INNER JOIN 
                    content.chunks c ON mce.chunk_id = c.id
                LEFT JOIN
                    metadata.frame_details_chunk fdc ON c.id = fdc.chunk_id
                WHERE 
                    1 - (mce.embedding <=> $1) > $2
                ORDER BY 
                    similarity DESC
                LIMIT $3
                """, query_embedding, similarity_threshold, limit)
                
                return [dict(r) for r in results]
                
        except Exception as e:
            logger.error(f"Error searching chunk embeddings: {e}")
            return []
    
    async def close(self):
        """Close the database connection pool."""
        if self.connection_pool:
            await self.connection_pool.close()
            self.connected = False
            logger.info("PostgreSQL connection pool closed")

    async def check_reference_id_in_metadata(self, reference_id: str) -> bool:
        """
        Check if a reference_id exists in the metadata schema.
        
        Args:
            reference_id: Reference ID to check
            
        Returns:
            bool: True if reference_id exists, False otherwise
        """
        if not await self._ensure_connected():
            return False
            
        try:
            async with self.connection_pool.acquire() as conn:
                # Check in frame_details_full
                frame_exists = await conn.fetchval("""
                    SELECT EXISTS(SELECT 1 FROM metadata.frame_details_full WHERE reference_id = $1)
                """, reference_id)
                
                if frame_exists:
                    return True
                    
                # Check in frame_details_chunk
                chunk_exists = await conn.fetchval("""
                    SELECT EXISTS(SELECT 1 FROM metadata.frame_details_chunk WHERE reference_id = $1)
                """, reference_id)
                
                return chunk_exists
                
        except Exception as e:
            logger.error(f"Error checking reference_id {reference_id} in metadata: {str(e)}")
            return False

    async def check_reference_id_in_embeddings(self, reference_id: str) -> bool:
        """
        Check if a reference_id exists in the embeddings schema.
        
        Args:
            reference_id: Reference ID to check
            
        Returns:
            bool: True if reference_id exists, False otherwise
        """
        if not await self._ensure_connected():
            return False
            
        try:
            async with self.connection_pool.acquire() as conn:
                exists = await conn.fetchval("""
                    SELECT EXISTS(SELECT 1 FROM embeddings.multimodal_embeddings WHERE reference_id = $1)
                """, reference_id)
                
                return exists
                
        except Exception as e:
            logger.error(f"Error checking reference_id {reference_id} in embeddings: {str(e)}")
            return False
    
    async def get_metadata_by_reference_id(self, reference_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a reference_id from the appropriate table.
        
        Args:
            reference_id: Reference ID to get metadata for
            
        Returns:
            Dict or None: Metadata if found, None otherwise
        """
        if not await self._ensure_connected():
            return None
            
        try:
            async with self.connection_pool.acquire() as conn:
                # First check if it's a frame reference_id
                frame_metadata = await conn.fetchrow("""
                    SELECT f.frame_name, f.folder_name, f.google_drive_url, 
                           fdf.metadata, fdf.description, fdf.summary
                    FROM metadata.frame_details_full fdf
                    JOIN content.frames f ON fdf.frame_id = f.id
                    WHERE fdf.reference_id = $1
                """, reference_id)
                
                if frame_metadata:
                    # Convert to dictionary
                    result = {
                        "type": "frame",
                        "reference_id": reference_id,
                        "frame_name": frame_metadata["frame_name"],
                        "folder_name": frame_metadata["folder_name"],
                        "google_drive_url": frame_metadata["google_drive_url"]
                    }
                    
                    # Add optional fields if they exist
                    if frame_metadata["description"]:
                        result["description"] = frame_metadata["description"]
                    if frame_metadata["summary"]:
                        result["summary"] = frame_metadata["summary"]
                    if frame_metadata["metadata"]:
                        result["metadata"] = frame_metadata["metadata"]
                        
                    return result
                
                # If not a frame, check if it's a chunk reference_id
                chunk_metadata = await conn.fetchrow("""
                    SELECT c.chunk_text, c.chunk_sequence_id, 
                           fdc.metadata, f.folder_name, f.frame_name
                    FROM metadata.frame_details_chunk fdc
                    JOIN content.chunks c ON fdc.chunk_id = c.id
                    JOIN content.frames f ON c.frame_id = f.id
                    WHERE fdc.reference_id = $1
                """, reference_id)
                
                if chunk_metadata:
                    # Convert to dictionary
                    result = {
                        "type": "chunk",
                        "reference_id": reference_id,
                        "chunk_sequence_id": chunk_metadata["chunk_sequence_id"],
                        "chunk_text": chunk_metadata["chunk_text"],
                        "frame_name": chunk_metadata["frame_name"],
                        "folder_name": chunk_metadata["folder_name"]
                    }
                    
                    # Add metadata if it exists
                    if chunk_metadata["metadata"]:
                        result["metadata"] = chunk_metadata["metadata"]
                        
                    return result
                
                # If not found in either table
                return None
                
        except Exception as e:
            logger.error(f"Error getting metadata for reference_id {reference_id}: {str(e)}")
            return None

    async def search_embeddings(
        self, 
        embedding: List[float],
        reference_type: str = None,
        similarity_threshold: float = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for similar embeddings.
        
        Args:
            embedding: Query embedding vector
            reference_type: Optional filter by reference type ('frame' or 'chunk')
            similarity_threshold: Minimum similarity threshold (default from env)
            limit: Maximum number of results to return
            
        Returns:
            List of dictionaries with search results
        """
        if not await self._ensure_connected():
            return []
        
        # Use default threshold if not provided
        if similarity_threshold is None:
            similarity_threshold = self.embedding_distance_threshold
            
        try:
            async with self.connection_pool.acquire() as conn:
                # Build query based on parameters
                query = """
                    SELECT 
                        e.reference_id,
                        e.reference_type,
                        e.model_name,
                        1 - (e.embedding <=> $1) as similarity
                    FROM embeddings.multimodal_embeddings e
                    WHERE 1 - (e.embedding <=> $1) > $2
                """
                
                params = [embedding, similarity_threshold]
                
                # Add reference_type filter if provided
                if reference_type:
                    query += " AND e.reference_type = $3"
                    params.append(reference_type)
                
                # Add ordering and limit
                query += " ORDER BY similarity DESC LIMIT $" + str(len(params) + 1)
                params.append(limit)
                
                # Execute query
                rows = await conn.fetch(query, *params)
                
                # Format results
                results = []
                for row in rows:
                    result = {
                        "reference_id": row["reference_id"],
                        "reference_type": row["reference_type"],
                        "model_name": row["model_name"],
                        "similarity": row["similarity"]
                    }
                    results.append(result)
                
                return results
            
        except Exception as e:
            logger.error(f"Error searching embeddings: {str(e)}")
            return []
    
    async def get_all_frames_with_embeddings(self) -> List[Dict[str, Any]]:
        """
        Get all frames with their embeddings.
        
        Returns:
            List of dictionaries with frame data
        """
        if not await self._ensure_connected():
            return []
            
        try:
            async with self.connection_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        f.id as frame_id,
                        f.frame_name,
                        f.folder_name,
                        fdf.reference_id,
                        fe.embedding_id,
                        fe.model_name
                    FROM content.frames f
                    JOIN metadata.frame_details_full fdf ON f.id = fdf.frame_id
                    LEFT JOIN metadata.frame_embeddings fe ON f.id = fe.frame_id
                    ORDER BY f.id
                """)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting all frames with embeddings: {str(e)}")
            return []

    async def get_all_chunks_with_embeddings(self) -> List[Dict[str, Any]]:
        """
        Get all chunks with their embeddings.
        
        Returns:
            List of dictionaries with chunk data
        """
        if not await self._ensure_connected():
            return []
            
        try:
            async with self.connection_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        c.id as chunk_id,
                        c.frame_id,
                        c.chunk_sequence_id,
                        LEFT(c.chunk_text, 100) as chunk_text_preview,
                        fdc.reference_id,
                        ce.embedding_id,
                        ce.model_name
                    FROM content.chunks c
                    JOIN metadata.frame_details_chunk fdc ON c.id = fdc.chunk_id
                    LEFT JOIN metadata.chunk_embeddings ce ON c.id = ce.chunk_id
                    ORDER BY c.frame_id, c.chunk_sequence_id
                """)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Error getting all chunks with embeddings: {str(e)}")
            return [] 