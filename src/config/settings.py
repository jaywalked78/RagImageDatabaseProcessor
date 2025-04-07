"""
Configuration settings for the application.
Loads settings from environment variables.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

# --- Base Paths --- 
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
TEMP_DIR = os.environ.get('TEMP_DIR', os.path.join(BASE_DIR, 'temp')) # Allow overriding temp dir
CREDENTIALS_DIR = os.path.join(BASE_DIR, 'credentials')

# --- Core App Settings --- 
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
HOST = os.environ.get('HOST', '0.0.0.0')
PORT = int(os.environ.get('PORT', '8000'))
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# --- Database Settings --- 
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DATABASE_URL = os.environ.get('DATABASE_URL') # Allow direct URL override
# Supabase Specific (if using Supabase client)
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# --- API Keys & Credentials --- 
# Voyage AI (Embedding Model)
VOYAGE_API_KEY = os.environ.get('VOYAGE_API_KEY')
EMBEDDING_MODEL_NAME = os.environ.get('EMBEDDING_MODEL_NAME', 'voyage-multimodal-3')
EMBEDDING_DIM = int(os.environ.get('EMBEDDING_DIM', '1024'))

# LLM (Metadata Processing)
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
# ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY') # Keep if needed as alternative
LLM_MODEL_NAME = os.environ.get('LLM_MODEL_NAME', 'gemini-1.5-pro-latest') # Default to Gemini

# Airtable
AIRTABLE_PERSONAL_ACCESS_TOKEN = os.environ.get('AIRTABLE_PERSONAL_ACCESS_TOKEN')
AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.environ.get('AIRTABLE_TABLE_NAME', 'Frames')

# Google Drive
GOOGLE_SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or os.path.join(CREDENTIALS_DIR, 'credentials.json')
# GOOGLE_DRIVE_CLIENT_ID = os.environ.get('GOOGLE_DRIVE_CLIENT_ID') # Removed
# GOOGLE_DRIVE_CLIENT_SECRET = os.environ.get('GOOGLE_DRIVE_CLIENT_SECRET') # Removed
# GOOGLE_DRIVE_REFRESH_TOKEN = os.environ.get('GOOGLE_DRIVE_REFRESH_TOKEN') # Removed

# --- Airtable Field Mappings --- 
# These *must* match the names in your Airtable base
DRIVE_FILE_ID_FIELD = os.environ.get('DRIVE_FILE_ID_FIELD', 'Frame ID')
FRAME_FILENAME_FIELD = os.environ.get('FRAME_FILENAME_FIELD', 'FrameFilename')
FRAME_NUMBER_FIELD = os.environ.get('FRAME_NUMBER_FIELD', 'FrameNumber')
VIDEO_ID_FIELD = os.environ.get('VIDEO_ID_FIELD', 'VideoID')
TIMESTAMP_FIELD = os.environ.get('TIMESTAMP_FIELD', 'Timestamp')
TITLE_FIELD = os.environ.get('TITLE_FIELD', 'FolderName')
PROCESSED_FIELD = os.environ.get('PROCESSED_FIELD', 'Processed')

# --- Processing Settings --- 
FRAME_BASE_DIR = os.environ.get('FRAME_BASE_DIR')  
BATCH_SIZE = int(os.environ.get('BATCH_SIZE', '10')) 
MAX_WORKERS = int(os.environ.get('MAX_WORKERS', '4')) 
SIMILARITY_THRESHOLD = float(os.environ.get('SIMILARITY_THRESHOLD', '0.75'))
CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', '500'))
CHUNK_OVERLAP = int(os.environ.get('CHUNK_OVERLAP', '50'))

# --- Optional Settings --- 
# API Security
JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_EXPIRE_MINUTES = int(os.environ.get('JWT_EXPIRE_MINUTES', '60'))
API_KEY = os.environ.get('API_KEY')
# Webhooks
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET')

# --- Test Settings --- 
TEST_FRAME_RELATIVE_PATH = os.environ.get('TEST_FRAME_RELATIVE_PATH')

# --- Create Directories --- 
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(CREDENTIALS_DIR, exist_ok=True)

# --- Configuration Validation --- 
class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass

def get_db_config() -> Dict[str, Any]:
    """Returns database connection details, preferring explicit vars over URL parsing."""
    if DB_HOST and DB_NAME and DB_USER and DB_PASSWORD:
        return {
            'host': DB_HOST,
            'port': DB_PORT,
            'dbname': DB_NAME,
            'user': DB_USER,
            'password': DB_PASSWORD
        }
    elif DATABASE_URL:
        # Basic parsing, might need refinement for complex URLs
        from urllib.parse import urlparse
        parsed = urlparse(DATABASE_URL)
        return {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'dbname': parsed.path[1:] if parsed.path else None,
            'user': parsed.username,
            'password': parsed.password
        }
    raise ConfigError("Database configuration incomplete. Set DB_HOST/NAME/USER/PASSWORD or DATABASE_URL.")

DB_CONFIG = get_db_config()

def verify_config() -> Dict[str, bool]:
    """
    Verify that required configuration settings are available.
    Returns a dictionary of configuration keys with boolean values indicating if they are valid.
    """
    db_ok = all(DB_CONFIG.values()) # Check if parsed config is complete
    voyage_ok = bool(VOYAGE_API_KEY)
    airtable_ok = all([AIRTABLE_PERSONAL_ACCESS_TOKEN, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME])
    gdrive_creds_ok = os.path.exists(GOOGLE_SERVICE_ACCOUNT_FILE)
    # LLM key check depends on which one is chosen
    llm_ok = bool(GOOGLE_API_KEY) # Check for Google API Key now
    
    config_status = {
        "db_connection": db_ok,
        "voyage_api": voyage_ok,
        "llm_api": llm_ok,
        "airtable": airtable_ok,
        "google_drive_credentials": gdrive_creds_ok
    }
    
    # Check FRAME_BASE_DIR only if it's explicitly set (might not be needed if using Drive only)
    if FRAME_BASE_DIR:
         config_status["frame_base_dir"] = os.path.isdir(FRAME_BASE_DIR)

    return config_status

def debug_config(include_secrets: bool = False) -> Dict[str, Any]:
    """Return a dictionary of configuration settings for debugging."""
    def mask_value(key: str, value: Optional[str]) -> str:
        if not value:
            return "Not Set"
        if include_secrets:
            return value
        if any(secret_key in key.lower() for secret_key in ['password', 'key', 'secret', 'token']):
            return f"{value[:4]}{'*' * 8}{value[-4:]}" if len(value) > 12 else '********'
        return value

    config = {
        "App": {
            "DEBUG": DEBUG,
            "HOST": HOST,
            "PORT": PORT,
            "LOG_LEVEL": LOG_LEVEL,
        },
        "Database": {
            "USING_URL": bool(DATABASE_URL) and not all([DB_HOST, DB_NAME, DB_USER]),
            "URL": mask_value("DATABASE_URL", DATABASE_URL),
            "HOST": DB_HOST,
            "PORT": DB_PORT,
            "NAME": DB_NAME,
            "USER": DB_USER,
            "PASSWORD": mask_value("password", DB_PASSWORD),
            "SUPABASE_URL": SUPABASE_URL, 
            "SUPABASE_KEY": mask_value("key", SUPABASE_KEY),
        },
        "APIs": {
            "VOYAGE_API_KEY": mask_value("key", VOYAGE_API_KEY),
            "EMBEDDING_MODEL": EMBEDDING_MODEL_NAME,
            "EMBEDDING_DIM": EMBEDDING_DIM,
            "GOOGLE_API_KEY": mask_value("key", GOOGLE_API_KEY),
            # "ANTHROPIC_API_KEY": mask_value("key", ANTHROPIC_API_KEY),
            "LLM_MODEL": LLM_MODEL_NAME,
            "AIRTABLE_PAT": mask_value("token", AIRTABLE_PERSONAL_ACCESS_TOKEN),
            "AIRTABLE_BASE_ID": AIRTABLE_BASE_ID,
            "AIRTABLE_TABLE_NAME": AIRTABLE_TABLE_NAME,
            "GDRIVE_SERVICE_ACCOUNT_FILE": GOOGLE_SERVICE_ACCOUNT_FILE,
            # "GDRIVE_CLIENT_ID": GOOGLE_DRIVE_CLIENT_ID, # Removed
            # "GDRIVE_CLIENT_SECRET": mask_value("secret", GOOGLE_DRIVE_CLIENT_SECRET), # Removed
            # "GDRIVE_REFRESH_TOKEN": mask_value("token", GOOGLE_DRIVE_REFRESH_TOKEN), # Removed
        },
        "AirtableFields": {
            "DRIVE_FILE_ID_FIELD": DRIVE_FILE_ID_FIELD,
            "FRAME_FILENAME_FIELD": FRAME_FILENAME_FIELD,
            "FRAME_NUMBER_FIELD": FRAME_NUMBER_FIELD,
            "VIDEO_ID_FIELD": VIDEO_ID_FIELD,
            "TIMESTAMP_FIELD": TIMESTAMP_FIELD,
            "TITLE_FIELD": TITLE_FIELD,
            "PROCESSED_FIELD": PROCESSED_FIELD,
        },
        "Processing": {
            "FRAME_BASE_DIR": FRAME_BASE_DIR,
            "BATCH_SIZE": BATCH_SIZE,
            "MAX_WORKERS": MAX_WORKERS,
            "SIMILARITY_THRESHOLD": SIMILARITY_THRESHOLD,
            "CHUNK_SIZE": CHUNK_SIZE,
            "CHUNK_OVERLAP": CHUNK_OVERLAP,
        },
        "Paths": {
            "BASE_DIR": str(BASE_DIR),
            "LOGS_DIR": LOGS_DIR,
            "TEMP_DIR": TEMP_DIR,
            "CREDENTIALS_DIR": CREDENTIALS_DIR
        },
        "Security (Optional)": {
             "JWT_SECRET": mask_value("secret", JWT_SECRET),
             "JWT_EXPIRE_MINUTES": JWT_EXPIRE_MINUTES,
             "API_KEY": mask_value("key", API_KEY),
        },
        "Webhooks (Optional)": {
            "URL": WEBHOOK_URL,
            "SECRET": mask_value("secret", WEBHOOK_SECRET),
        }
    }
    return config 