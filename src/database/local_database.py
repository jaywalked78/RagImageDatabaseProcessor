#!/usr/bin/env python3
"""
Local database module for storing frame data and metadata.
This allows us to minimize external API calls by storing all necessary data locally.
"""

import os
import json
import sqlite3
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union

import numpy as np
from dotenv import load_dotenv

# Import Google Drive downloader if available
try:
    from google_drive_downloader import GoogleDriveDownloader
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("local_database")

# Load environment variables
load_dotenv()

class LocalDatabase:
    """Manages a local SQLite database for frame data and metadata."""
    
    def __init__(self, db_path: str = "frames_local.db", init_db: bool = True):
        """Initialize the local database.
        
        Args:
            db_path: Path to SQLite database file
            init_db: Whether to initialize the database schema
        """
        self.db_path = db_path
        self.conn = None
        
        # Connect to database
        self._connect()
        
        # Initialize schema if needed
        if init_db:
            self._init_schema()
    
    def _connect(self):
        """Connect to the SQLite database."""
        self.conn = sqlite3.connect(self.db_path)
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        # Use Row factory for dictionary-like access
        self.conn.row_factory = sqlite3.Row
        logger.info(f"Connected to local database: {self.db_path}")
    
    def _init_schema(self):
        """Initialize the database schema."""
        cursor = self.conn.cursor()
        
        # Create folders table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_id TEXT NOT NULL,
            folder_path TEXT NOT NULL,
            folder_name TEXT,
            source TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(folder_id, source)
        )
        ''')
        
        # Create frames table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS frames (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            frame_id TEXT NOT NULL,
            folder_id INTEGER NOT NULL,
            frame_name TEXT NOT NULL,
            frame_path TEXT NOT NULL,
            local_path TEXT,
            airtable_record_id TEXT,
            google_drive_url TEXT,
            downloaded BOOLEAN DEFAULT FALSE,
            processed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(frame_id, folder_id),
            FOREIGN KEY(folder_id) REFERENCES folders(id)
        )
        ''')
        
        # Create metadata table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            frame_id INTEGER NOT NULL,
            metadata_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(frame_id) REFERENCES frames(id)
        )
        ''')
        
        # Create chunks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            frame_id INTEGER NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(frame_id, chunk_index),
            FOREIGN KEY(frame_id) REFERENCES frames(id)
        )
        ''')
        
        # Create embeddings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk_id INTEGER NOT NULL,
            model TEXT NOT NULL,
            embedding BLOB NOT NULL,
            embedding_id TEXT,
            uploaded_to_postgres BOOLEAN DEFAULT FALSE,
            uploaded_to_webhook BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(chunk_id, model),
            FOREIGN KEY(chunk_id) REFERENCES chunks(id)
        )
        ''')
        
        self.conn.commit()
        logger.info("Database schema initialized")
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def add_folder(self, folder_id: str, folder_path: str, source: str, folder_name: Optional[str] = None) -> int:
        """Add a folder to the database.
        
        Args:
            folder_id: Unique identifier for the folder (e.g., Google Drive folder ID)
            folder_path: Path to the folder
            source: Source of the folder (e.g., 'google_drive', 'local')
            folder_name: Name of the folder (optional)
            
        Returns:
            int: ID of the inserted folder
        """
        cursor = self.conn.cursor()
        
        # Extract folder name from path if not provided
        if not folder_name:
            folder_name = os.path.basename(folder_path.rstrip('/'))
        
        try:
            cursor.execute('''
            INSERT INTO folders (folder_id, folder_path, folder_name, source)
            VALUES (?, ?, ?, ?)
            ''', (folder_id, folder_path, folder_name, source))
            self.conn.commit()
            logger.info(f"Added folder: {folder_name} ({source})")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Folder already exists, get its ID
            cursor.execute('''
            SELECT id FROM folders
            WHERE folder_id = ? AND source = ?
            ''', (folder_id, source))
            result = cursor.fetchone()
            return result['id'] if result else None
    
    def add_frame(self, frame_id: str, folder_id: int, frame_name: str, frame_path: str, 
                  local_path: Optional[str] = None, airtable_record_id: Optional[str] = None,
                  google_drive_url: Optional[str] = None) -> int:
        """Add a frame to the database.
        
        Args:
            frame_id: Unique identifier for the frame (e.g., Google Drive file ID)
            folder_id: ID of the parent folder in the database
            frame_name: Name of the frame file
            frame_path: Path to the frame within its source
            local_path: Local path to the frame file if downloaded
            airtable_record_id: Airtable record ID if available
            google_drive_url: Google Drive URL for this frame (optional)
            
        Returns:
            int: ID of the inserted frame
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO frames (frame_id, folder_id, frame_name, frame_path, local_path, airtable_record_id, google_drive_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (frame_id, folder_id, frame_name, frame_path, local_path, airtable_record_id, google_drive_url))
            self.conn.commit()
            logger.debug(f"Added frame: {frame_name}")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Frame already exists, get its ID
            cursor.execute('''
            SELECT id FROM frames
            WHERE frame_id = ? AND folder_id = ?
            ''', (frame_id, folder_id))
            result = cursor.fetchone()
            return result['id'] if result else None
    
    def update_frame_local_path(self, frame_id: int, local_path: str) -> bool:
        """Update the local path of a frame.
        
        Args:
            frame_id: ID of the frame in the database
            local_path: Local path to the frame file
            
        Returns:
            bool: True if the update was successful
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
        UPDATE frames
        SET local_path = ?, downloaded = TRUE
        WHERE id = ?
        ''', (local_path, frame_id))
        self.conn.commit()
        
        return cursor.rowcount > 0
    
    def mark_frame_processed(self, frame_id: int) -> bool:
        """Mark a frame as processed.
        
        Args:
            frame_id: ID of the frame in the database
            
        Returns:
            bool: True if the update was successful
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
        UPDATE frames
        SET processed = TRUE
        WHERE id = ?
        ''', (frame_id, ))
        self.conn.commit()
        
        return cursor.rowcount > 0
    
    def add_metadata(self, frame_id: int, metadata_type: str, content: str) -> int:
        """Add metadata for a frame.
        
        Args:
            frame_id: ID of the frame in the database
            metadata_type: Type of metadata (e.g., 'airtable', 'ocr')
            content: Content of the metadata (typically JSON string)
            
        Returns:
            int: ID of the inserted metadata
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
        INSERT INTO metadata (frame_id, metadata_type, content)
        VALUES (?, ?, ?)
        ''', (frame_id, metadata_type, content))
        self.conn.commit()
        
        return cursor.lastrowid
    
    def add_chunk(self, frame_id: int, chunk_index: int, content: str) -> int:
        """Add a text chunk for a frame.
        
        Args:
            frame_id: ID of the frame in the database
            chunk_index: Index of the chunk
            content: Text content of the chunk
            
        Returns:
            int: ID of the inserted chunk
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO chunks (frame_id, chunk_index, content)
            VALUES (?, ?, ?)
            ''', (frame_id, chunk_index, content))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Chunk already exists, get its ID
            cursor.execute('''
            SELECT id FROM chunks
            WHERE frame_id = ? AND chunk_index = ?
            ''', (frame_id, chunk_index))
            result = cursor.fetchone()
            return result['id'] if result else None
    
    def add_embedding(self, chunk_id: int, model: str, embedding: np.ndarray, embedding_id: Optional[str] = None) -> int:
        """Add an embedding for a chunk.
        
        Args:
            chunk_id: ID of the chunk in the database
            model: Name of the embedding model
            embedding: Embedding vector
            embedding_id: ID of the embedding in external systems (optional)
            
        Returns:
            int: ID of the inserted embedding
        """
        cursor = self.conn.cursor()
        
        # Convert numpy array to binary blob
        embedding_blob = embedding.tobytes()
        
        try:
            cursor.execute('''
            INSERT INTO embeddings (chunk_id, model, embedding, embedding_id)
            VALUES (?, ?, ?, ?)
            ''', (chunk_id, model, embedding_blob, embedding_id))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Embedding already exists, get its ID
            cursor.execute('''
            SELECT id FROM embeddings
            WHERE chunk_id = ? AND model = ?
            ''', (chunk_id, model))
            result = cursor.fetchone()
            return result['id'] if result else None
    
    def mark_embedding_uploaded(self, embedding_id: int, destination: str) -> bool:
        """Mark an embedding as uploaded to a destination.
        
        Args:
            embedding_id: ID of the embedding in the database
            destination: Destination ('postgres' or 'webhook')
            
        Returns:
            bool: True if the update was successful
        """
        cursor = self.conn.cursor()
        
        if destination == 'postgres':
            field = 'uploaded_to_postgres'
        elif destination == 'webhook':
            field = 'uploaded_to_webhook'
        else:
            logger.error(f"Unknown destination: {destination}")
            return False
        
        cursor.execute(f'''
        UPDATE embeddings
        SET {field} = TRUE
        WHERE id = ?
        ''', (embedding_id, ))
        self.conn.commit()
        
        return cursor.rowcount > 0
    
    def get_frame_by_path(self, frame_path: str) -> Dict[str, Any]:
        """Get a frame by its path.
        
        Args:
            frame_path: Path to the frame
            
        Returns:
            dict: Frame data or None if not found
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
        SELECT * FROM frames
        WHERE frame_path = ? OR local_path = ?
        ''', (frame_path, frame_path))
        
        result = cursor.fetchone()
        if result:
            return dict(result)
        return None
    
    def get_frame_by_id(self, frame_id: int) -> Dict[str, Any]:
        """Get a frame by its ID.
        
        Args:
            frame_id: ID of the frame in the database
            
        Returns:
            dict: Frame data or None if not found
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
        SELECT * FROM frames
        WHERE id = ?
        ''', (frame_id, ))
        
        result = cursor.fetchone()
        if result:
            return dict(result)
        return None
    
    def get_metadata_for_frame(self, frame_id: int, metadata_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get metadata for a frame.
        
        Args:
            frame_id: ID of the frame in the database
            metadata_type: Type of metadata to retrieve (optional)
            
        Returns:
            list: List of metadata dictionaries
        """
        cursor = self.conn.cursor()
        
        if metadata_type:
            cursor.execute('''
            SELECT * FROM metadata
            WHERE frame_id = ? AND metadata_type = ?
            ''', (frame_id, metadata_type))
        else:
            cursor.execute('''
            SELECT * FROM metadata
            WHERE frame_id = ?
            ''', (frame_id, ))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_chunks_for_frame(self, frame_id: int) -> List[Dict[str, Any]]:
        """Get chunks for a frame.
        
        Args:
            frame_id: ID of the frame in the database
            
        Returns:
            list: List of chunk dictionaries
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
        SELECT * FROM chunks
        WHERE frame_id = ?
        ORDER BY chunk_index
        ''', (frame_id, ))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_embeddings_for_chunk(self, chunk_id: int, model: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get embeddings for a chunk.
        
        Args:
            chunk_id: ID of the chunk in the database
            model: Model name to filter by (optional)
            
        Returns:
            list: List of embedding dictionaries
        """
        cursor = self.conn.cursor()
        
        if model:
            cursor.execute('''
            SELECT * FROM embeddings
            WHERE chunk_id = ? AND model = ?
            ''', (chunk_id, model))
        else:
            cursor.execute('''
            SELECT * FROM embeddings
            WHERE chunk_id = ?
            ''', (chunk_id, ))
        
        results = cursor.fetchall()
        embeddings = []
        
        for row in results:
            row_dict = dict(row)
            # Convert binary blob back to numpy array
            embedding_blob = row_dict['embedding']
            row_dict['embedding'] = np.frombuffer(embedding_blob, dtype=np.float32)
            embeddings.append(row_dict)
        
        return embeddings
    
    def get_pending_uploads(self, destination: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get embeddings pending upload to a destination.
        
        Args:
            destination: Destination ('postgres' or 'webhook')
            limit: Maximum number of embeddings to retrieve (optional)
            
        Returns:
            list: List of embedding dictionaries with related chunk and frame info
        """
        cursor = self.conn.cursor()
        
        if destination == 'postgres':
            field = 'e.uploaded_to_postgres = FALSE'
        elif destination == 'webhook':
            field = 'e.uploaded_to_webhook = FALSE'
        else:
            logger.error(f"Unknown destination: {destination}")
            return []
        
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f'''
        SELECT e.id as embedding_id, e.model, e.embedding, c.id as chunk_id, c.content as chunk_content, 
               c.chunk_index, f.id as frame_id, f.frame_name, f.frame_path, f.airtable_record_id, f.google_drive_url,
               fo.folder_path, fo.folder_name
        FROM embeddings e
        JOIN chunks c ON e.chunk_id = c.id
        JOIN frames f ON c.frame_id = f.id
        JOIN folders fo ON f.folder_id = fo.id
        WHERE {field}
        {limit_clause}
        '''
        
        cursor.execute(query)
        results = cursor.fetchall()
        pending = []
        
        for row in results:
            row_dict = dict(row)
            # Convert binary blob back to numpy array
            embedding_blob = row_dict['embedding']
            row_dict['embedding'] = np.frombuffer(embedding_blob, dtype=np.float32)
            pending.append(row_dict)
        
        return pending
    
    def get_unprocessed_frames(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get frames that haven't been processed yet.
        
        Args:
            limit: Maximum number of frames to retrieve (optional)
            
        Returns:
            list: List of frame dictionaries
        """
        cursor = self.conn.cursor()
        
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        cursor.execute(f'''
        SELECT f.*, fo.folder_path, fo.folder_name, fo.source
        FROM frames f
        JOIN folders fo ON f.folder_id = fo.id
        WHERE f.processed = FALSE AND f.downloaded = TRUE
        {limit_clause}
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_undownloaded_frames(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get frames that haven't been downloaded yet.
        
        Args:
            limit: Maximum number of frames to retrieve (optional)
            
        Returns:
            list: List of frame dictionaries
        """
        cursor = self.conn.cursor()
        
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        cursor.execute(f'''
        SELECT f.*, fo.folder_path, fo.folder_name, fo.source, fo.folder_id as source_folder_id
        FROM frames f
        JOIN folders fo ON f.folder_id = fo.id
        WHERE f.downloaded = FALSE
        {limit_clause}
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def load_airtable_metadata(self, airtable_data: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Load metadata from Airtable.
        
        Args:
            airtable_data: List of Airtable records
            
        Returns:
            tuple: (number of folders added, number of frames added)
        """
        folders_added = 0
        frames_added = 0
        
        for record in airtable_data:
            record_id = record['id']
            fields = record.get('fields', {})
            
            # Extract folder information
            folder_path = fields.get('folderPath', '')
            folder_name = os.path.basename(folder_path.rstrip('/')) if folder_path else 'Unknown'
            folder_id = f"airtable_{folder_name}"
            
            # Add folder
            folder_db_id = self.add_folder(folder_id, folder_path, 'airtable', folder_name)
            if folder_db_id:
                folders_added += 1
            
            # Extract frame information
            frame_name = fields.get('Name', '')
            if not frame_name:
                continue
                
            frame_path = os.path.join(folder_path, frame_name) if folder_path else frame_name
            frame_id = f"airtable_{record_id}"
            
            # Add frame
            frame_db_id = self.add_frame(frame_id, folder_db_id, frame_name, frame_path, 
                                        airtable_record_id=record_id)
            if frame_db_id:
                frames_added += 1
                
                # Add metadata
                self.add_metadata(frame_db_id, 'airtable', json.dumps(fields))
        
        logger.info(f"Loaded {frames_added} frames and {folders_added} folders from Airtable")
        return folders_added, frames_added
    
    def load_google_drive_folder(self, folder_id: str, credentials_path: Optional[str] = None,
                               download_dir: Optional[str] = None, 
                               file_pattern: Optional[str] = None) -> Tuple[int, int, str]:
        """Load frames from a Google Drive folder.
        
        Args:
            folder_id: Google Drive folder ID
            credentials_path: Path to Google API credentials (optional)
            download_dir: Directory to download frames to (optional)
            file_pattern: Pattern to filter files by (optional)
            
        Returns:
            tuple: (number of frames added, number of frames downloaded, download directory)
        """
        if not GOOGLE_DRIVE_AVAILABLE:
            logger.error("Google Drive integration not available")
            return 0, 0, None
        
        # Create Google Drive downloader
        downloader = GoogleDriveDownloader(credentials_path=credentials_path)
        
        # Prepare filter pattern for Google Drive
        drive_filter = None
        if file_pattern:
            drive_filter = f"name contains '{file_pattern}'"
        
        # List files in folder
        files = downloader.list_files(folder_id, drive_filter)
        
        if not files:
            logger.warning(f"No files found in Google Drive folder {folder_id}")
            return 0, 0, None
        
        # Create download directory if needed
        if download_dir:
            os.makedirs(download_dir, exist_ok=True)
        else:
            download_dir = tempfile.mkdtemp(prefix="frame_downloader_")
        
        # Add folder to database
        folder_name = f"google_drive_{folder_id}"
        folder_path = f"google_drive/{folder_id}"
        folder_db_id = self.add_folder(folder_id, folder_path, 'google_drive', folder_name)
        
        frames_added = 0
        frames_downloaded = 0
        
        # Add frames to database
        for file in files:
            file_id = file['id']
            file_name = file['name']
            file_path = f"{folder_path}/{file_name}"
            
            # Add frame to database
            frame_db_id = self.add_frame(file_id, folder_db_id, file_name, file_path)
            
            if frame_db_id:
                frames_added += 1
        
        logger.info(f"Added {frames_added} frames from Google Drive folder {folder_id}")
        return frames_added, frames_downloaded, download_dir
    
    def download_pending_frames(self, credentials_path: Optional[str] = None, 
                              download_dir: Optional[str] = None,
                              limit: Optional[int] = None) -> int:
        """Download frames that haven't been downloaded yet.
        
        Args:
            credentials_path: Path to Google API credentials (optional)
            download_dir: Directory to download frames to (optional)
            limit: Maximum number of frames to download (optional)
            
        Returns:
            int: Number of frames downloaded
        """
        if not GOOGLE_DRIVE_AVAILABLE:
            logger.error("Google Drive integration not available")
            return 0
        
        # Create download directory if needed
        if download_dir:
            os.makedirs(download_dir, exist_ok=True)
        else:
            download_dir = tempfile.mkdtemp(prefix="frame_downloader_")
        
        # Get undownloaded frames
        frames = self.get_undownloaded_frames(limit)
        
        if not frames:
            logger.info("No frames pending download")
            return 0
        
        # Create Google Drive downloader
        downloader = GoogleDriveDownloader(credentials_path=credentials_path)
        
        frames_downloaded = 0
        
        # Group frames by source
        google_drive_frames = [f for f in frames if f['source'] == 'google_drive']
        
        # Download Google Drive frames
        for frame in google_drive_frames:
            frame_id = frame['frame_id']  # This is the Google Drive file ID
            frame_name = frame['frame_name']
            frame_db_id = frame['id']
            
            # Download file
            local_path = os.path.join(download_dir, frame_name)
            if downloader.download_file(frame_id, local_path):
                # Update frame with local path
                self.update_frame_local_path(frame_db_id, local_path)
                frames_downloaded += 1
        
        logger.info(f"Downloaded {frames_downloaded} frames to {download_dir}")
        return frames_downloaded

# Usage example
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Local database management for frame processing')
    parser.add_argument('--db-path', default='frames_local.db', help='Path to local database file')
    parser.add_argument('--drive-folder', help='Google Drive folder ID to load frames from')
    parser.add_argument('--credentials', help='Path to Google API credentials')
    parser.add_argument('--download-dir', help='Directory to download frames to')
    parser.add_argument('--download-limit', type=int, help='Maximum number of frames to download')
    parser.add_argument('--pattern', help='Pattern to filter files by')
    
    args = parser.parse_args()
    
    # Create database
    db = LocalDatabase(db_path=args.db_path)
    
    try:
        # Load frames from Google Drive folder if specified
        if args.drive_folder:
            frames_added, frames_downloaded, download_dir = db.load_google_drive_folder(
                args.drive_folder,
                credentials_path=args.credentials,
                download_dir=args.download_dir,
                file_pattern=args.pattern
            )
            
            print(f"Added {frames_added} frames from Google Drive folder {args.drive_folder}")
            
            # Download pending frames
            if args.download_limit:
                frames_downloaded = db.download_pending_frames(
                    credentials_path=args.credentials,
                    download_dir=download_dir or args.download_dir,
                    limit=args.download_limit
                )
                print(f"Downloaded {frames_downloaded} frames")
        
        # List unprocessed frames
        unprocessed = db.get_unprocessed_frames()
        print(f"Found {len(unprocessed)} unprocessed frames ready for embedding")
        
    finally:
        # Close database connection
        db.close() 