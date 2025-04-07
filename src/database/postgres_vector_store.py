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
    
    def __init__(self, 
                connection_pool: Optional[asyncpg.pool.Pool] = None,
                host: Optional[str] = None,
                port: Optional[str] = None,
                user: Optional[str] = None,
                password: Optional[str] = None,
                database: Optional[str] = None,
                min_connections: int = 1,
                max_connections: int = 10):
        """
        Initialize the PostgreSQL vector store.
        
        Args:
            connection_pool: Existing connection pool to use
            host: Database host (default: from env var POSTGRES_HOST)
            port: Database port (default: from env var POSTGRES_PORT)
            user: Database user (default: from env var POSTGRES_USER)
            password: Database password (default: from env var POSTGRES_PASSWORD)
            database: Database name (default: from env var POSTGRES_DB)
            min_connections: Minimum number of connections in the pool
            max_connections: Maximum number of connections in the pool
        """
        # Use provided connection pool or create one
        self.pool = connection_pool
        
        # Set connection parameters
        self.host = host or os.getenv("POSTGRES_HOST")
        self.port = port or os.getenv("POSTGRES_PORT", "5432")
        self.user = user or os.getenv("POSTGRES_USER")
        self.password = password or os.getenv("POSTGRES_PASSWORD")
        self.database = database or os.getenv("POSTGRES_DB")
        
        # Initialize with empty pool, to be created when needed
        self.min_connections = min_connections
        self.max_connections = max_connections
        
        # Check connection parameters
        if not self.pool and (not self.host or not self.user or not self.password or not self.database):
            logger.warning("Incomplete PostgreSQL connection information")
        
        # Connection status
        self._connected = False
    
    async def connect(self) -> bool:
        """
        Connect to the PostgreSQL database and create a connection pool.
        
        Returns:
            Boolean indicating connection success
        """
        if self.pool:
            self._connected = True
            return True
        
        if not self.host or not self.user or not self.password or not self.database:
            logger.error("Cannot connect: Incomplete connection information")
            return False
        
        try:
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                min_size=self.min_connections,
                max_size=self.max_connections,
                command_timeout=60
            )
            
            self._connected = True
            logger.info(f"Connected to PostgreSQL at {self.host}:{self.port}")
            
            # Verify pgvector extension
            await self._verify_pgvector()
            
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            return False
    
    async def _verify_pgvector(self):
        """Verify that pgvector extension is installed."""
        if not self.pool:
            logger.error("Cannot verify pgvector: No connection pool")
            return False
        
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
                )
                
                if not result:
                    logger.error("pgvector extension is not installed")
                    return False
                
                logger.info("pgvector extension is installed")
                return True
                
        except Exception as e:
            logger.error(f"Error verifying pgvector: {e}")
            return False
    
    async def _ensure_connected(self) -> bool:
        """Ensure connection to the database is established."""
        if self._connected and self.pool:
            return True
        return await self.connect()
    
    async def store_frame(self,
                        frame_name: str,
                        folder_path: str,
                        folder_name: Optional[str] = None,
                        frame_timestamp: Optional[str] = None,
                        google_drive_url: Optional[str] = None,
                        airtable_record_id: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """
        Store frame information in the database.
        
        Args:
            frame_name: Name of the frame
            folder_path: Path to the folder containing the frame
            folder_name: Name of the folder containing the frame
            frame_timestamp: Timestamp of the frame
            google_drive_url: Google Drive URL for the frame
            airtable_record_id: Airtable record ID
            metadata: Dictionary of metadata for the frame
            
        Returns:
            Frame ID if successful, None otherwise
        """
        if not await self._ensure_connected():
            logger.error("Cannot store frame: Not connected to database")
            return None
        
        # Extract folder name from path if not provided
        if not folder_name and folder_path:
            try:
                folder_name = os.path.basename(folder_path)
            except:
                pass
        
        # Check if frame exists
        frame_id = await self._get_frame_id(frame_name, folder_path)
        
        try:
            async with self.pool.acquire() as conn:
                if frame_id:
                    # Update existing frame
                    query = """
                    UPDATE content.frames SET
                        folder_name = COALESCE($1, folder_name),
                        frame_timestamp = COALESCE($2::TIMESTAMPTZ, frame_timestamp),
                        google_drive_url = COALESCE($3, google_drive_url),
                        airtable_record_id = COALESCE($4, airtable_record_id),
                        metadata = COALESCE($5::JSONB, metadata)
                    WHERE id = $6
                    RETURNING id
                    """
                    
                    result = await conn.fetchval(
                        query,
                        folder_name,
                        frame_timestamp,
                        google_drive_url,
                        airtable_record_id,
                        json.dumps(metadata) if metadata else None,
                        frame_id
                    )
                    
                    logger.info(f"Updated frame '{frame_name}' with ID {frame_id}")
                    return frame_id
                    
                else:
                    # Insert new frame
                    query = """
                    INSERT INTO content.frames (
                        frame_name, folder_path, folder_name, frame_timestamp,
                        google_drive_url, airtable_record_id, metadata
                    ) VALUES ($1, $2, $3, $4::TIMESTAMPTZ, $5, $6, $7::JSONB)
                    RETURNING id
                    """
                    
                    frame_id = await conn.fetchval(
                        query,
                        frame_name,
                        folder_path,
                        folder_name,
                        frame_timestamp,
                        google_drive_url,
                        airtable_record_id,
                        json.dumps(metadata) if metadata else None
                    )
                    
                    logger.info(f"Inserted frame '{frame_name}' with ID {frame_id}")
                    return frame_id
                    
        except Exception as e:
            logger.error(f"Error storing frame '{frame_name}': {e}")
            return None
    
    async def _get_frame_id(self, frame_name: str, folder_path: str) -> Optional[int]:
        """
        Get frame ID by name and folder path.
        
        Args:
            frame_name: Name of the frame
            folder_path: Path to the folder containing the frame
            
        Returns:
            Frame ID if found, None otherwise
        """
        if not self.pool:
            return None
        
        try:
            async with self.pool.acquire() as conn:
                query = """
                SELECT id FROM content.frames
                WHERE frame_name = $1 AND folder_path = $2
                """
                
                return await conn.fetchval(query, frame_name, folder_path)
                
        except Exception as e:
            logger.error(f"Error getting frame ID: {e}")
            return None
    
    async def store_chunk(self,
                        frame_id: int,
                        chunk_sequence_id: int,
                        chunk_text: str) -> Optional[int]:
        """
        Store chunk information in the database.
        
        Args:
            frame_id: ID of the frame
            chunk_sequence_id: Sequence ID of the chunk
            chunk_text: Text content of the chunk
            
        Returns:
            Chunk ID if successful, None otherwise
        """
        if not await self._ensure_connected():
            logger.error("Cannot store chunk: Not connected to database")
            return None
        
        # Check if chunk exists
        chunk_id = await self._get_chunk_id(frame_id, chunk_sequence_id)
        
        try:
            async with self.pool.acquire() as conn:
                if chunk_id:
                    # Update existing chunk
                    query = """
                    UPDATE content.chunks SET
                        chunk_text = $1
                    WHERE id = $2
                    RETURNING id
                    """
                    
                    result = await conn.fetchval(query, chunk_text, chunk_id)
                    logger.info(f"Updated chunk {chunk_sequence_id} for frame {frame_id}")
                    return chunk_id
                    
                else:
                    # Insert new chunk
                    query = """
                    INSERT INTO content.chunks (
                        frame_id, chunk_sequence_id, chunk_text
                    ) VALUES ($1, $2, $3)
                    RETURNING id
                    """
                    
                    chunk_id = await conn.fetchval(query, frame_id, chunk_sequence_id, chunk_text)
                    logger.info(f"Inserted chunk {chunk_sequence_id} for frame {frame_id}")
                    return chunk_id
                    
        except Exception as e:
            logger.error(f"Error storing chunk {chunk_sequence_id} for frame {frame_id}: {e}")
            return None
    
    async def _get_chunk_id(self, frame_id: int, chunk_sequence_id: int) -> Optional[int]:
        """
        Get chunk ID by frame ID and sequence ID.
        
        Args:
            frame_id: ID of the frame
            chunk_sequence_id: Sequence ID of the chunk
            
        Returns:
            Chunk ID if found, None otherwise
        """
        if not self.pool:
            return None
        
        try:
            async with self.pool.acquire() as conn:
                query = """
                SELECT id FROM content.chunks
                WHERE frame_id = $1 AND chunk_sequence_id = $2
                """
                
                return await conn.fetchval(query, frame_id, chunk_sequence_id)
                
        except Exception as e:
            logger.error(f"Error getting chunk ID: {e}")
            return None
    
    async def store_frame_embedding(self,
                                  frame_id: int,
                                  embedding: List[float],
                                  model_name: str) -> bool:
        """
        Store a whole-frame embedding in the database.
        
        Args:
            frame_id: ID of the frame
            embedding: List of embedding values
            model_name: Name of the embedding model
            
        Returns:
            Boolean indicating success
        """
        if not await self._ensure_connected():
            logger.error("Cannot store frame embedding: Not connected to database")
            return False
        
        try:
            # Convert embedding to correct format
            embedding_str = str(embedding).replace('[', '{').replace(']', '}')
            
            # Generate a UUID for the embedding
            embedding_id = str(uuid.uuid4())
            
            async with self.pool.acquire() as conn:
                # Check if frame embedding exists for this model
                query = """
                SELECT id FROM metadata.frame_embeddings
                WHERE frame_id = $1 AND model_name = $2
                """
                
                existing_id = await conn.fetchval(query, frame_id, model_name)
                
                if existing_id:
                    # Update existing embedding
                    query = """
                    UPDATE metadata.frame_embeddings SET
                        embedding = $1::vector
                    WHERE id = $2
                    """
                    
                    await conn.execute(query, embedding_str, existing_id)
                    logger.info(f"Updated frame embedding for frame {frame_id}")
                    
                else:
                    # Insert new embedding
                    query = """
                    INSERT INTO metadata.frame_embeddings (
                        id, frame_id, embedding, model_name
                    ) VALUES ($1, $2, $3::vector, $4)
                    """
                    
                    await conn.execute(query, embedding_id, frame_id, embedding_str, model_name)
                    logger.info(f"Inserted frame embedding for frame {frame_id}")
                
                return True
                
        except Exception as e:
            logger.error(f"Error storing frame embedding for frame {frame_id}: {e}")
            return False
    
    async def store_chunk_embedding(self,
                                  chunk_id: int,
                                  embedding: List[float],
                                  model_name: str) -> bool:
        """
        Store a chunk embedding in the database.
        
        Args:
            chunk_id: ID of the chunk
            embedding: List of embedding values
            model_name: Name of the embedding model
            
        Returns:
            Boolean indicating success
        """
        if not await self._ensure_connected():
            logger.error("Cannot store chunk embedding: Not connected to database")
            return False
        
        try:
            # Convert embedding to correct format
            embedding_str = str(embedding).replace('[', '{').replace(']', '}')
            
            # Generate a UUID for the embedding
            embedding_id = str(uuid.uuid4())
            
            async with self.pool.acquire() as conn:
                # Check if chunk embedding exists for this model
                query = """
                SELECT id FROM metadata.chunk_embeddings
                WHERE chunk_id = $1 AND model_name = $2
                """
                
                existing_id = await conn.fetchval(query, chunk_id, model_name)
                
                if existing_id:
                    # Update existing embedding
                    query = """
                    UPDATE metadata.chunk_embeddings SET
                        embedding = $1::vector
                    WHERE id = $2
                    """
                    
                    await conn.execute(query, embedding_str, existing_id)
                    logger.info(f"Updated chunk embedding for chunk {chunk_id}")
                    
                else:
                    # Insert new embedding
                    query = """
                    INSERT INTO metadata.chunk_embeddings (
                        id, chunk_id, embedding, model_name
                    ) VALUES ($1, $2, $3::vector, $4)
                    """
                    
                    await conn.execute(query, embedding_id, chunk_id, embedding_str, model_name)
                    logger.info(f"Inserted chunk embedding for chunk {chunk_id}")
                
                return True
                
        except Exception as e:
            logger.error(f"Error storing chunk embedding for chunk {chunk_id}: {e}")
            return False
    
    async def process_frame_with_chunks(self,
                                      frame_name: str,
                                      folder_path: str,
                                      chunks: List[Dict[str, Any]],
                                      frame_embedding: List[float],
                                      model_name: str,
                                      folder_name: Optional[str] = None,
                                      frame_timestamp: Optional[str] = None,
                                      google_drive_url: Optional[str] = None,
                                      airtable_record_id: Optional[str] = None,
                                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Process a complete frame with chunks in one transaction.
        
        Args:
            frame_name: Name of the frame
            folder_path: Path to the folder containing the frame
            chunks: List of chunk dictionaries with text, sequence_id, and embedding
            frame_embedding: Whole-frame embedding
            model_name: Name of the embedding model
            folder_name: Name of the folder containing the frame
            frame_timestamp: Timestamp of the frame
            google_drive_url: Google Drive URL for the frame
            airtable_record_id: Airtable record ID
            metadata: Dictionary of metadata for the frame
            
        Returns:
            Boolean indicating success
        """
        if not await self._ensure_connected():
            logger.error("Cannot process frame: Not connected to database")
            return False
        
        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    # Store frame
                    frame_id = await self.store_frame(
                        frame_name=frame_name,
                        folder_path=folder_path,
                        folder_name=folder_name,
                        frame_timestamp=frame_timestamp,
                        google_drive_url=google_drive_url,
                        airtable_record_id=airtable_record_id,
                        metadata=metadata
                    )
                    
                    if not frame_id:
                        logger.error(f"Failed to store frame '{frame_name}'")
                        return False
                    
                    # Store frame embedding
                    frame_emb_success = await self.store_frame_embedding(
                        frame_id=frame_id,
                        embedding=frame_embedding,
                        model_name=model_name
                    )
                    
                    if not frame_emb_success:
                        logger.error(f"Failed to store frame embedding for '{frame_name}'")
                        return False
                    
                    # Store chunks and their embeddings
                    for chunk in chunks:
                        chunk_id = await self.store_chunk(
                            frame_id=frame_id,
                            chunk_sequence_id=chunk['sequence_id'],
                            chunk_text=chunk['text']
                        )
                        
                        if not chunk_id:
                            logger.error(f"Failed to store chunk {chunk['sequence_id']} for '{frame_name}'")
                            continue
                        
                        # Store chunk embedding
                        chunk_emb_success = await self.store_chunk_embedding(
                            chunk_id=chunk_id,
                            embedding=chunk['embedding'],
                            model_name=model_name
                        )
                        
                        if not chunk_emb_success:
                            logger.error(f"Failed to store embedding for chunk {chunk['sequence_id']} for '{frame_name}'")
                    
                    logger.info(f"Successfully processed frame '{frame_name}' with {len(chunks)} chunks")
                    return True
                    
        except Exception as e:
            logger.error(f"Error processing frame '{frame_name}': {e}")
            return False
    
    async def search_frames(self,
                          query_embedding: List[float],
                          similarity_threshold: float = 0.7,
                          limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for frames by embedding similarity.
        
        Args:
            query_embedding: Query embedding vector
            similarity_threshold: Minimum similarity threshold (0-1)
            limit: Maximum number of results
            
        Returns:
            List of dictionaries with frame information and similarity scores
        """
        if not await self._ensure_connected():
            logger.error("Cannot search frames: Not connected to database")
            return []
        
        if not query_embedding:
            logger.error("Cannot search frames: Empty query embedding")
            return []
        
        try:
            # Convert embedding to correct format
            embedding_str = str(query_embedding).replace('[', '{').replace(']', '}')
            
            async with self.pool.acquire() as conn:
                query = """
                SELECT 
                    f.id as frame_id,
                    f.frame_name,
                    f.folder_path,
                    f.folder_name,
                    f.google_drive_url,
                    f.airtable_record_id,
                    f.metadata,
                    1 - (fe.embedding <=> $1::vector) as similarity
                FROM 
                    metadata.frame_embeddings fe
                JOIN 
                    content.frames f ON fe.frame_id = f.id
                WHERE 
                    1 - (fe.embedding <=> $1::vector) > $2
                ORDER BY 
                    similarity DESC
                LIMIT $3
                """
                
                rows = await conn.fetch(query, embedding_str, similarity_threshold, limit)
                
                results = []
                for row in rows:
                    result = dict(row)
                    # Convert metadata from JSON string to dictionary
                    if result['metadata']:
                        if isinstance(result['metadata'], str):
                            result['metadata'] = json.loads(result['metadata'])
                    else:
                        result['metadata'] = {}
                    
                    results.append(result)
                
                logger.info(f"Found {len(results)} frames with similarity > {similarity_threshold}")
                return results
                
        except Exception as e:
            logger.error(f"Error searching frames: {e}")
            return []
    
    async def search_chunks(self,
                          query_embedding: List[float],
                          similarity_threshold: float = 0.7,
                          limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for chunks by embedding similarity.
        
        Args:
            query_embedding: Query embedding vector
            similarity_threshold: Minimum similarity threshold (0-1)
            limit: Maximum number of results
            
        Returns:
            List of dictionaries with chunk information and similarity scores
        """
        if not await self._ensure_connected():
            logger.error("Cannot search chunks: Not connected to database")
            return []
        
        if not query_embedding:
            logger.error("Cannot search chunks: Empty query embedding")
            return []
        
        try:
            # Convert embedding to correct format
            embedding_str = str(query_embedding).replace('[', '{').replace(']', '}')
            
            async with self.pool.acquire() as conn:
                query = """
                SELECT 
                    c.id as chunk_id,
                    c.frame_id,
                    c.chunk_sequence_id,
                    c.chunk_text,
                    f.frame_name,
                    f.folder_path,
                    f.folder_name,
                    f.google_drive_url,
                    f.airtable_record_id,
                    f.metadata,
                    1 - (ce.embedding <=> $1::vector) as similarity
                FROM 
                    metadata.chunk_embeddings ce
                JOIN 
                    content.chunks c ON ce.chunk_id = c.id
                JOIN 
                    content.frames f ON c.frame_id = f.id
                WHERE 
                    1 - (ce.embedding <=> $1::vector) > $2
                ORDER BY 
                    similarity DESC
                LIMIT $3
                """
                
                rows = await conn.fetch(query, embedding_str, similarity_threshold, limit)
                
                results = []
                for row in rows:
                    result = dict(row)
                    # Convert metadata from JSON string to dictionary
                    if result['metadata']:
                        if isinstance(result['metadata'], str):
                            result['metadata'] = json.loads(result['metadata'])
                    else:
                        result['metadata'] = {}
                    
                    results.append(result)
                
                logger.info(f"Found {len(results)} chunks with similarity > {similarity_threshold}")
                return results
                
        except Exception as e:
            logger.error(f"Error searching chunks: {e}")
            return []
    
    async def hybrid_search(self,
                          query_embedding: List[float],
                          metadata_filters: Optional[Dict[str, Any]] = None,
                          limit: int = 10,
                          similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform a hybrid search using both vector similarity and metadata filters.
        
        Args:
            query_embedding: Query embedding vector
            metadata_filters: Dictionary of metadata filters to apply
            limit: Maximum number of results
            similarity_threshold: Minimum similarity threshold (0-1)
            
        Returns:
            List of dictionaries with frame information and similarity scores
        """
        if not await self._ensure_connected():
            logger.error("Cannot perform hybrid search: Not connected to database")
            return []
        
        if not query_embedding:
            logger.error("Cannot perform hybrid search: Empty query embedding")
            return []
        
        try:
            # Convert embedding to correct format
            embedding_str = str(query_embedding).replace('[', '{').replace(']', '}')
            
            # Convert metadata filters to JSONB
            metadata_json = json.dumps(metadata_filters) if metadata_filters else None
            
            async with self.pool.acquire() as conn:
                query = """
                SELECT 
                    f.id as frame_id,
                    f.frame_name,
                    f.folder_path,
                    f.folder_name,
                    f.google_drive_url,
                    f.airtable_record_id,
                    f.metadata,
                    1 - (fe.embedding <=> $1::vector) as similarity
                FROM 
                    metadata.frame_embeddings fe
                JOIN 
                    content.frames f ON fe.frame_id = f.id
                WHERE 
                    1 - (fe.embedding <=> $1::vector) > $3
                    AND ($2::jsonb IS NULL OR f.metadata @> $2::jsonb)
                ORDER BY 
                    similarity DESC
                LIMIT $4
                """
                
                rows = await conn.fetch(query, embedding_str, metadata_json, similarity_threshold, limit)
                
                results = []
                for row in rows:
                    result = dict(row)
                    # Convert metadata from JSON string to dictionary
                    if result['metadata']:
                        if isinstance(result['metadata'], str):
                            result['metadata'] = json.loads(result['metadata'])
                    else:
                        result['metadata'] = {}
                    
                    results.append(result)
                
                logger.info(f"Found {len(results)} frames with hybrid search")
                return results
                
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    def reciprocal_rank_fusion(self, results_lists: List[List[Dict[str, Any]]], k: int = 60) -> List[Dict[str, Any]]:
        """
        Apply Reciprocal Rank Fusion to merge multiple result lists.
        
        Args:
            results_lists: List of result lists to fuse
            k: Constant in RRF formula (typically 60)
            
        Returns:
            List of merged and reranked results
        """
        if not results_lists:
            return []
        
        # Initialize fusion scores dictionary
        fusion_scores = {}
        
        # Process each result list
        for results in results_lists:
            for rank, result in enumerate(results):
                # Get document ID (using frame_id or other unique identifier)
                doc_id = result.get('frame_id') or result.get('id')
                if not doc_id:
                    continue
                
                # Initialize score if not already present
                if doc_id not in fusion_scores:
                    fusion_scores[doc_id] = 0
                
                # Update score with RRF formula
                fusion_scores[doc_id] += 1.0 / (k + rank)
        
        # If no results were found
        if not fusion_scores:
            return []
        
        # Sort documents by fusion score
        reranked_doc_ids = sorted(fusion_scores.items(), key=lambda item: item[1], reverse=True)
        
        # Create a map of result documents for easy lookup
        all_docs = {}
        for results in results_lists:
            for result in results:
                doc_id = result.get('frame_id') or result.get('id')
                if doc_id and doc_id not in all_docs:
                    all_docs[doc_id] = result
        
        # Create final list of merged results
        merged_results = []
        for doc_id, fusion_score in reranked_doc_ids:
            if doc_id in all_docs:
                result = all_docs[doc_id].copy()
                result['fusion_score'] = fusion_score
                merged_results.append(result)
        
        return merged_results
    
    async def query_expansion_search(self,
                                  query_embedding: List[float],
                                  variation_embeddings: List[List[float]],
                                  metadata_filters: Optional[Dict[str, Any]] = None,
                                  limit: int = 10,
                                  similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform a search with query expansion and result fusion.
        
        Args:
            query_embedding: Primary query embedding vector
            variation_embeddings: List of variation embedding vectors
            metadata_filters: Dictionary of metadata filters to apply
            limit: Maximum number of results per query
            similarity_threshold: Minimum similarity threshold (0-1)
            
        Returns:
            List of merged and reranked results
        """
        if not await self._ensure_connected():
            logger.error("Cannot perform search with query expansion: Not connected to database")
            return []
        
        if not query_embedding:
            logger.error("Cannot perform search with query expansion: Empty query embedding")
            return []
        
        try:
            # Perform primary search with metadata filters
            primary_results = await self.hybrid_search(
                query_embedding=query_embedding,
                metadata_filters=metadata_filters,
                limit=limit,
                similarity_threshold=similarity_threshold
            )
            
            # Perform searches for variation embeddings (without metadata filters)
            variation_results = []
            for variation_embedding in variation_embeddings:
                results = await self.search_frames(
                    query_embedding=variation_embedding,
                    similarity_threshold=similarity_threshold,
                    limit=limit
                )
                variation_results.append(results)
            
            # Combine all results
            all_results = [primary_results] + variation_results
            
            # Apply Reciprocal Rank Fusion to merge and rerank results
            merged_results = self.reciprocal_rank_fusion(all_results)
            
            logger.info(f"Found {len(merged_results)} frames with query expansion search")
            return merged_results
            
        except Exception as e:
            logger.error(f"Error in query expansion search: {e}")
            return []
    
    def close(self):
        """Close the connection pool."""
        if self.pool:
            asyncio.create_task(self.pool.close())
            logger.info("PostgreSQL connection pool closed")
            self._connected = False 