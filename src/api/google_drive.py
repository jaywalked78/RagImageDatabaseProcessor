#!/usr/bin/env python3
"""
Google Drive downloader utility for fetching frames for processing.
This module handles authentication and downloading files from a Google Drive folder.
"""

import os
import io
import logging
import tempfile
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
import pickle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("drive_downloader")

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveDownloader:
    """Class to handle downloading files from Google Drive."""
    
    def __init__(self, credentials_path=None, token_path=None):
        """Initialize the downloader with OAuth credentials.
        
        Args:
            credentials_path: Path to credentials JSON file (OAuth or service account)
            token_path: Path to token pickle file for OAuth
        """
        self.credentials_path = credentials_path or os.environ.get('GOOGLE_CREDENTIALS_PATH')
        self.token_path = token_path or os.environ.get('GOOGLE_TOKEN_PATH', 'token.pickle')
        self.drive_service = None
        
        if not self.credentials_path:
            logger.warning("No credentials path provided. Set GOOGLE_CREDENTIALS_PATH in environment.")
        
    def authenticate(self):
        """Authenticate with Google Drive API."""
        creds = None
        
        # Try loading saved token for OAuth flow
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Check if credentials need refresh
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                creds = None
                logger.warning("Token refresh failed, will need to reauthenticate")
        
        # If no valid credentials, try service account or OAuth flow
        if not creds and self.credentials_path:
            if '.json' in self.credentials_path:
                try:
                    # Try service account first
                    creds = service_account.Credentials.from_service_account_file(
                        self.credentials_path, scopes=SCOPES)
                    logger.info("Authenticated using service account")
                except ValueError:
                    # Fall back to OAuth flow
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                    logger.info("Authenticated using OAuth flow")
                    
                    # Save credentials for next run
                    with open(self.token_path, 'wb') as token:
                        pickle.dump(creds, token)
            else:
                logger.error("Invalid credentials file format. Must be JSON.")
                return False
        
        if not creds:
            logger.error("Failed to authenticate with Google Drive")
            return False
        
        # Build the Drive API service
        self.drive_service = build('drive', 'v3', credentials=creds)
        logger.info("Successfully authenticated with Google Drive")
        return True
    
    def list_files(self, folder_id, file_filter=None):
        """List files in a Google Drive folder.
        
        Args:
            folder_id: ID of the Google Drive folder
            file_filter: Optional filter string (e.g., "name contains 'frame_'")
            
        Returns:
            List of file dictionaries with id, name, and mimeType
        """
        if not self.drive_service:
            if not self.authenticate():
                return []
        
        try:
            query = f"'{folder_id}' in parents and trashed = false"
            if file_filter:
                query += f" and {file_filter}"
            
            results = self.drive_service.files().list(
                q=query,
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType, size)"
            ).execute()
            
            files = results.get('files', [])
            next_page_token = results.get('nextPageToken')
            
            # Handle pagination
            while next_page_token:
                results = self.drive_service.files().list(
                    q=query,
                    pageSize=1000,
                    fields="nextPageToken, files(id, name, mimeType, size)",
                    pageToken=next_page_token
                ).execute()
                files.extend(results.get('files', []))
                next_page_token = results.get('nextPageToken')
            
            logger.info(f"Found {len(files)} files in folder {folder_id}")
            return files
            
        except Exception as e:
            logger.error(f"Error listing files from Google Drive: {e}")
            return []
    
    def download_file(self, file_id, destination_path):
        """Download a single file from Google Drive.
        
        Args:
            file_id: Google Drive file ID
            destination_path: Path where the file should be saved
            
        Returns:
            bool: True if download was successful
        """
        if not self.drive_service:
            if not self.authenticate():
                return False
        
        try:
            # Create request to download file
            request = self.drive_service.files().get_media(fileId=file_id)
            
            # Stream the file to disk
            with open(destination_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    logger.debug(f"Download progress: {int(status.progress() * 100)}%")
            
            logger.info(f"Downloaded file to {destination_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            return False
    
    def download_files(self, folder_id, destination_dir, file_pattern=None, limit=None):
        """Download files from a Google Drive folder.
        
        Args:
            folder_id: Google Drive folder ID
            destination_dir: Directory to save downloaded files
            file_pattern: Optional filter pattern (e.g., "name contains 'frame_'")
            limit: Maximum number of files to download
            
        Returns:
            list: Paths to downloaded files
        """
        # Create destination directory if it doesn't exist
        os.makedirs(destination_dir, exist_ok=True)
        
        # List files in the folder
        files = self.list_files(folder_id, file_pattern)
        
        if not files:
            logger.warning(f"No files found in folder {folder_id} matching pattern")
            return []
        
        # Limit number of files if specified
        if limit:
            files = files[:limit]
            logger.info(f"Limiting download to {limit} files")
        
        # Download each file
        downloaded_paths = []
        for i, file in enumerate(files):
            file_name = file['name']
            file_id = file['id']
            file_path = os.path.join(destination_dir, file_name)
            
            logger.info(f"Downloading file {i+1}/{len(files)}: {file_name}")
            if self.download_file(file_id, file_path):
                downloaded_paths.append(file_path)
        
        logger.info(f"Downloaded {len(downloaded_paths)} files to {destination_dir}")
        return downloaded_paths
    
    def download_frames_to_temp(self, folder_id, file_pattern=None, limit=None):
        """Download frames to a temporary directory.
        
        Args:
            folder_id: Google Drive folder ID
            file_pattern: Optional filter pattern (e.g., "name contains 'frame_'")
            limit: Maximum number of files to download
            
        Returns:
            tuple: (temp_dir, list of downloaded file paths)
        """
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="frame_downloader_")
        logger.info(f"Created temporary directory: {temp_dir}")
        
        # Download files
        files = self.download_files(folder_id, temp_dir, file_pattern, limit)
        
        return temp_dir, files

def main():
    """Command line interface for the downloader."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Download files from Google Drive')
    parser.add_argument('folder_id', help='Google Drive folder ID')
    parser.add_argument('--destination', '-d', default='downloaded_frames', 
                        help='Destination directory for downloaded files')
    parser.add_argument('--credentials', '-c', help='Path to Google API credentials JSON file')
    parser.add_argument('--pattern', '-p', help='Filter pattern, e.g., "name contains \'frame_\'"')
    parser.add_argument('--limit', '-l', type=int, help='Maximum number of files to download')
    
    args = parser.parse_args()
    
    # Create and configure the downloader
    downloader = GoogleDriveDownloader(credentials_path=args.credentials)
    
    # Download files
    downloaded_files = downloader.download_files(
        args.folder_id, 
        args.destination, 
        args.pattern,
        args.limit
    )
    
    print(f"Downloaded {len(downloaded_files)} files to {args.destination}")

if __name__ == '__main__':
    main() 