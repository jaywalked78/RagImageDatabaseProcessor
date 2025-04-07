"""
Google Drive client for accessing files and folders.
Handles authentication, search, and file download operations.
"""

import os
import io
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# Get a logger for this module
logger = logging.getLogger("logicLoom.integrations.google_drive")

class GoogleDriveClient:
    """Client for interacting with the Google Drive API."""
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize the Google Drive client.
        
        Args:
            credentials_path: Path to the service account credentials JSON file.
                             If None, will use GOOGLE_APPLICATION_CREDENTIALS environment variable
                             or default to 'credentials/credentials.json'.
        """
        try:
            # Get credentials path
            if credentials_path is None:
                credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                
            if credentials_path is None:
                credentials_path = 'credentials/credentials.json'
                
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Google Drive credentials file not found at: {credentials_path}")
                
            # Create credentials
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_path, 
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            
            # Build the Google Drive service
            self.service = build('drive', 'v3', credentials=self.credentials)
            logger.info("Google Drive client initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Google Drive client: {str(e)}")
            raise
    
    def find_folder(self, folder_name: str) -> List[Dict[str, Any]]:
        """
        Find folders with the given name in Google Drive.
        
        Args:
            folder_name: Name of the folder to find
            
        Returns:
            List of folder information dictionaries
        """
        try:
            query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
            response = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, createdTime, mimeType, parents)'
            ).execute()
            
            items = response.get('files', [])
            logger.info(f"Found {len(items)} folders with name '{folder_name}'")
            return items
        except HttpError as e:
            logger.error(f"Google Drive API error searching for folder '{folder_name}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error finding folder '{folder_name}': {str(e)}")
            raise
    
    def list_folder_contents(self, folder_id: str, 
                            order_by: str = 'name', 
                            max_results: int = 100,
                            query_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List the contents of a Google Drive folder.
        
        Args:
            folder_id: ID of the folder to list
            order_by: Field to order results by ('name', 'createdTime', etc.)
            max_results: Maximum number of results to return
            query_filter: Additional query filter to apply (e.g., "mimeType contains 'image/'")
            
        Returns:
            List of file information dictionaries
        """
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            if query_filter:
                query += f" and {query_filter}"
                
            response = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, createdTime, modifiedTime, size, imageMediaMetadata)',
                orderBy=order_by,
                pageSize=min(max_results, 1000)  # API limit is 1000
            ).execute()
            
            items = response.get('files', [])
            logger.info(f"Found {len(items)} items in folder {folder_id}")
            return items
        except HttpError as e:
            logger.error(f"Google Drive API error listing folder {folder_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error listing folder {folder_id}: {str(e)}")
            raise
    
    def download_file(self, file_id: str, output_path: str) -> str:
        """
        Download a file from Google Drive to a local path.
        
        Args:
            file_id: ID of the file to download
            output_path: Local path where the file should be saved
            
        Returns:
            Path to the downloaded file
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Get the file
            request = self.service.files().get_media(fileId=file_id)
            
            # Download to file
            with open(output_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            
            logger.info(f"Downloaded file {file_id} to {output_path}")
            return output_path
        except HttpError as e:
            logger.error(f"Google Drive API error downloading file {file_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {str(e)}")
            raise
    
    def download_file_to_memory(self, file_id: str) -> Tuple[bytes, str]:
        """
        Download a file from Google Drive into memory.
        
        Args:
            file_id: ID of the file to download
            
        Returns:
            Tuple of (file_bytes, mime_type)
        """
        try:
            # Get file metadata to determine mime type
            file_metadata = self.service.files().get(fileId=file_id, fields='mimeType').execute()
            mime_type = file_metadata.get('mimeType', 'application/octet-stream')
            
            # Get the file content
            request = self.service.files().get_media(fileId=file_id)
            file_bytes = io.BytesIO()
            
            # Download to memory
            downloader = MediaIoBaseDownload(file_bytes, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            logger.info(f"Downloaded file {file_id} to memory ({len(file_bytes.getvalue())} bytes)")
            return file_bytes.getvalue(), mime_type
        except HttpError as e:
            logger.error(f"Google Drive API error downloading file {file_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {str(e)}")
            raise
    
    def find_files_by_name(self, file_name: str, 
                          folder_id: Optional[str] = None,
                          mime_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find files with a specific name.
        
        Args:
            file_name: Name of the file to find
            folder_id: Optional parent folder ID to search within
            mime_type: Optional MIME type to filter by
            
        Returns:
            List of file information dictionaries
        """
        try:
            query = f"name='{file_name}' and trashed=false"
            
            if folder_id:
                query += f" and '{folder_id}' in parents"
                
            if mime_type:
                query += f" and mimeType='{mime_type}'"
                
            response = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, parents, createdTime, modifiedTime)'
            ).execute()
            
            items = response.get('files', [])
            logger.info(f"Found {len(items)} files with name '{file_name}'")
            return items
        except HttpError as e:
            logger.error(f"Google Drive API error searching for file '{file_name}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error finding file '{file_name}': {str(e)}")
            raise 