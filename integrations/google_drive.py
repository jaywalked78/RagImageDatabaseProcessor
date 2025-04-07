"""
Google Drive integration for TheLogicLoom application.
Handles authentication and file operations with Google Drive API.
"""

import os
import io
import logging
import tempfile
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

import backoff
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from tenacity import retry, stop_after_attempt, wait_exponential

# Get a logger for this module
logger = logging.getLogger("logicLoom")

# Service account credentials path
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'service-account.json')

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


class GoogleDriveClient:
    """Client for Google Drive operations using service account authentication."""
    
    def __init__(self):
        """Initialize the Google Drive client with service account credentials."""
        try:
            # Load credentials from service account file
            if not os.path.exists(SERVICE_ACCOUNT_FILE):
                logger.error(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
                raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")
            
            self.credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES
            )
            self.service = build('drive', 'v3', credentials=self.credentials)
            logger.info("Google Drive client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive client: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @backoff.on_exception(backoff.expo, HttpError, max_tries=3)
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific file by ID.
        
        Args:
            file_id: The Google Drive file ID
            
        Returns:
            Dict containing file metadata
        """
        try:
            file_metadata = self.service.files().get(
                fileId=file_id, 
                fields='id,name,mimeType,size,thumbnailLink,webViewLink'
            ).execute()
            logger.debug(f"Retrieved metadata for file: {file_id}")
            return file_metadata
        except HttpError as error:
            logger.error(f"Error retrieving file metadata for {file_id}: {error}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @backoff.on_exception(backoff.expo, HttpError, max_tries=3)
    def download_file(self, file_id: str, output_path: Optional[str] = None) -> str:
        """
        Download a file from Google Drive.
        
        Args:
            file_id: The Google Drive file ID
            output_path: Optional path to save the file. If None, a temporary file is created.
            
        Returns:
            Path to the downloaded file
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            # If no output path provided, create a temporary file
            if not output_path:
                temp_dir = tempfile.gettempdir()
                file_metadata = self.get_file_metadata(file_id)
                file_name = file_metadata.get('name', f"file_{file_id}")
                output_path = os.path.join(temp_dir, file_name)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Download the file
            with io.FileIO(output_path, 'wb') as file_handle:
                downloader = MediaIoBaseDownload(file_handle, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
            
            logger.info(f"File {file_id} downloaded successfully to {output_path}")
            return output_path
        except HttpError as error:
            logger.error(f"Error downloading file {file_id}: {error}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @backoff.on_exception(backoff.expo, HttpError, max_tries=3)
    def download_file_to_memory(self, file_id: str) -> Tuple[bytes, str]:
        """
        Download a file from Google Drive directly to memory.
        
        Args:
            file_id: The Google Drive file ID
            
        Returns:
            Tuple of (file_bytes, file_mime_type)
        """
        try:
            # Get file metadata to get the MIME type
            file_metadata = self.get_file_metadata(file_id)
            mime_type = file_metadata.get('mimeType', 'application/octet-stream')
            
            # Download the file
            request = self.service.files().get_media(fileId=file_id)
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            
            file_buffer.seek(0)
            logger.info(f"File {file_id} downloaded successfully to memory")
            return file_buffer.read(), mime_type
        except HttpError as error:
            logger.error(f"Error downloading file {file_id} to memory: {error}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @backoff.on_exception(backoff.expo, HttpError, max_tries=3)
    def list_files(self, query: str = None, page_size: int = 100) -> List[Dict[str, Any]]:
        """
        List files in Google Drive with optional query.
        
        Args:
            query: Optional query string (https://developers.google.com/drive/api/guides/search-files)
            page_size: Number of files to return per page
            
        Returns:
            List of file metadata dictionaries
        """
        try:
            results = []
            page_token = None
            
            while True:
                response = self.service.files().list(
                    q=query,
                    pageSize=page_size,
                    fields='nextPageToken, files(id, name, mimeType, size, thumbnailLink, webViewLink)',
                    pageToken=page_token
                ).execute()
                
                files = response.get('files', [])
                results.extend(files)
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            logger.info(f"Listed {len(results)} files from Google Drive")
            return results
        except HttpError as error:
            logger.error(f"Error listing files: {error}")
            raise 