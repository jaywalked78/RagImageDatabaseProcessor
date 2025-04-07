#!/usr/bin/env python3
"""
Utility functions for processing metadata from various sources.
"""

import logging
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger("utils.metadata")

def process_metadata_text(metadata: Dict[str, Any]) -> str:
    """Process Airtable metadata fields into a text representation.
    
    Args:
        metadata: Dictionary of metadata fields from Airtable
        
    Returns:
        str: Text representation of the metadata
    """
    if not metadata:
        return ""
    
    # Build text representation of metadata
    lines = []
    
    # Add title if available
    if "Name" in metadata:
        lines.append(f"Frame: {metadata['Name']}")
    
    # Add folder path if available
    if "folderPath" in metadata:
        lines.append(f"Folder: {metadata['folderPath']}")
    
    # Add URL if available
    if "URL" in metadata:
        lines.append(f"URL: {metadata['URL']}")
    
    # Add frame number if available
    if "frameNumber" in metadata and metadata["frameNumber"]:
        lines.append(f"Frame Number: {metadata['frameNumber']}")
    
    # Add description if available
    if "Description" in metadata and metadata["Description"]:
        lines.append(f"Description: {metadata['Description']}")
    
    # Add notes if available
    if "Notes" in metadata and metadata["Notes"]:
        lines.append(f"Notes: {metadata['Notes']}")
    
    # Add tags if available
    if "Tags" in metadata and metadata["Tags"]:
        if isinstance(metadata["Tags"], list):
            tags_text = ", ".join(metadata["Tags"])
            lines.append(f"Tags: {tags_text}")
        else:
            lines.append(f"Tags: {metadata['Tags']}")
    
    # Add custom fields
    for key, value in metadata.items():
        if key not in ["Name", "folderPath", "URL", "frameNumber", "Description", "Notes", "Tags"] and value:
            # Skip empty values and already processed fields
            if not value or value == "":
                continue
                
            # Format value based on type
            if isinstance(value, list):
                formatted_value = ", ".join(str(v) for v in value)
            else:
                formatted_value = str(value)
                
            lines.append(f"{key}: {formatted_value}")
    
    return "\n".join(lines)

def extract_keywords(metadata: Dict[str, Any]) -> List[str]:
    """Extract keywords from metadata fields.
    
    Args:
        metadata: Dictionary of metadata fields
        
    Returns:
        list: List of keywords extracted from the metadata
    """
    keywords = []
    
    # Extract tags if available
    if "Tags" in metadata and metadata["Tags"]:
        if isinstance(metadata["Tags"], list):
            keywords.extend(metadata["Tags"])
        else:
            keywords.append(metadata["Tags"])
    
    # Extract keywords from description if available
    if "Description" in metadata and metadata["Description"]:
        # Split description into words and add as keywords
        description_words = metadata["Description"].split()
        for word in description_words:
            # Only add words longer than 3 characters
            if len(word) > 3 and word.lower() not in [k.lower() for k in keywords]:
                keywords.append(word)
    
    # Extract keywords from notes if available
    if "Notes" in metadata and metadata["Notes"]:
        # Split notes into words and add as keywords
        notes_words = metadata["Notes"].split()
        for word in notes_words:
            # Only add words longer than 3 characters
            if len(word) > 3 and word.lower() not in [k.lower() for k in keywords]:
                keywords.append(word)
    
    return keywords

def find_image_url(metadata: Dict[str, Any]) -> Optional[str]:
    """Find the image URL in metadata.
    
    Args:
        metadata: Dictionary of metadata fields
        
    Returns:
        str or None: Image URL if found, None otherwise
    """
    # Check for URL field
    if "URL" in metadata and metadata["URL"]:
        return metadata["URL"]
    
    # Check for Google Drive URL
    if "GoogleDriveURL" in metadata and metadata["GoogleDriveURL"]:
        return metadata["GoogleDriveURL"]
    
    # Check for Image URL
    if "ImageURL" in metadata and metadata["ImageURL"]:
        return metadata["ImageURL"]
    
    # Check for Attachment field
    if "Attachment" in metadata and metadata["Attachment"]:
        # Attachment field is usually a list of objects with URL property
        if isinstance(metadata["Attachment"], list) and metadata["Attachment"]:
            if isinstance(metadata["Attachment"][0], dict) and "url" in metadata["Attachment"][0]:
                return metadata["Attachment"][0]["url"]
    
    return None 