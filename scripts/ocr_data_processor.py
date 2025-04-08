#!/usr/bin/env python
"""
OCR Data Processor Script

This script processes OCR data from text files, categorizes the content,
extracts meaningful information (URLs, keys, etc.), and updates Airtable
with the structured data.

Features:
- Parses OCR text to identify content types (URLs, tables, text blocks, etc.)
- Uses Gemini API for advanced content categorization and extraction
- Detects sensitive information like API keys and credentials
- Updates Airtable with structured OCR data in the "OCRData" column
- Flags sensitive content in Airtable in the "Flagged" column

Usage:
  python ocr_data_processor.py [options]

Options:
  --input-dir DIR       Directory containing OCR text files (default: ocr_results)
  --csv-file FILE       CSV file with processed frames data (default: processed_frames.csv)
  --update-airtable     Update Airtable with processed OCR data
  --base-id ID          Airtable base ID (required for Airtable updates)
  --table-name NAME     Airtable table name (required for Airtable updates)
  --api-key KEY         Airtable API key (required for Airtable updates)
  --batch-size N        Number of records to process in each batch (default: 100)
  --dry-run             Don't update Airtable, just show what would be updated
  --use-gemini          Use Google's Gemini API for enhanced text analysis
  --gemini-api-key KEY  API key for Google Gemini (required when using --use-gemini)
  --display-data        Display the formatted data, even without Airtable connection
"""

import os
import re
import csv
import json
import argparse
import time
import hashlib
from pathlib import Path
from datetime import datetime
import logging
import sys
import traceback
from urllib.parse import urlparse

# Try importing Airtable API library
try:
    from pyairtable import Api, Base, Table
    AIRTABLE_AVAILABLE = True
except ImportError:
    AIRTABLE_AVAILABLE = False
    print("Warning: pyairtable package not found. Airtable updates not available.")
    print("Install with: pip install pyairtable")

# Try importing Google's Gemini API
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: Google Generative AI package not found. Gemini API not available.")
    print("Install with: pip install google-generativeai")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("ocr_data_processor.log")
    ]
)
logger = logging.getLogger(__name__)

# Airtable rate limiting constants
AIRTABLE_RATE_LIMIT_PER_SECOND = 5  # Maximum of 5 requests per second
AIRTABLE_RATE_LIMIT_SLEEP = 0.25  # Sleep 250ms between requests (allows ~4 req/sec)

class OCRDataProcessor:
    """Class to process OCR data, categorize it, and update Airtable"""
    
    def __init__(self, options):
        self.options = options
        self.input_dir = Path(options.input_dir)
        self.csv_file = Path(options.csv_file)
        self.processed_count = 0
        self.flagged_count = 0
        self.error_count = 0
        self.use_gemini = options.use_gemini
        self.last_airtable_request_time = 0
        
        # Set up storage structure
        self.setup_storage_structure()
        
        # Get master logger if provided
        self.master_logger = getattr(options, 'master_logger', None)
        
        # URL regex pattern for detecting URLs in OCR text
        self.url_pattern = re.compile(
            r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?[-\w%&=.]*)?'
        )
        
        # API key detection patterns
        self.api_key_patterns = [
            # General API key pattern (alphanumeric with possible symbols, length > 20)
            re.compile(r'(?:api[_-]?key|apikey|key|token)["\s:=]+([a-zA-Z0-9_\-\.]{20,})'),
            # Google API key pattern
            re.compile(r'AIza[0-9A-Za-z\-_]{35}'),
            # AWS access key pattern
            re.compile(r'AKIA[0-9A-Z]{16}'),
            # Generic secret/private key indicators
            re.compile(r'(?:secret|private)[_-]?key["\s:=]+([a-zA-Z0-9_\-\.]{20,})'),
        ]
        
        # Initialize Airtable connection if updating
        if options.update_airtable:
            if not AIRTABLE_AVAILABLE:
                logger.error("Cannot update Airtable: pyairtable package not installed")
                sys.exit(1)
            
            # Try different ways to get Airtable credentials
            api_key = options.api_key
            if not api_key:
                api_key = os.environ.get("AIRTABLE_API_KEY", "")
            
            base_id = options.base_id
            if not base_id:
                base_id = os.environ.get("AIRTABLE_BASE_ID", "")
            
            table_name = options.table_name
            if not table_name:
                table_name = os.environ.get("AIRTABLE_TABLE_NAME", "")
            
            if not (base_id and table_name and api_key):
                logger.error("Airtable base ID, table name, and API key are required")
                sys.exit(1)
            
            try:
                self.airtable = Table(api_key, base_id, table_name)
                logger.info(f"Connected to Airtable: {base_id}/{table_name}")
                
                # Get rate limiting from env or use default
                self.rate_limit_sleep = float(os.environ.get("AIRTABLE_RATE_LIMIT_SLEEP", AIRTABLE_RATE_LIMIT_SLEEP))
                logger.info(f"Airtable rate limiting enabled: {self.rate_limit_sleep}s between requests")
            except Exception as e:
                logger.error(f"Failed to connect to Airtable: {e}")
                traceback.print_exc()
                sys.exit(1)
                
        # Initialize Gemini if requested
        if self.use_gemini:
            if not GEMINI_AVAILABLE:
                logger.error("Cannot use Gemini: google-generativeai package not installed")
                sys.exit(1)
                
            # Try different ways to get Gemini API key
            gemini_api_key = options.gemini_api_key
            if not gemini_api_key:
                # Try environment variables in order of preference
                gemini_api_key = (
                    os.environ.get("GEMINI_API_KEY", "") or
                    os.environ.get("GEMINI_API_KEY_1", "") or
                    os.environ.get("GOOGLE_API_KEY", "")
                )
            
            if not gemini_api_key:
                logger.error("Gemini API key is required when using --use-gemini")
                sys.exit(1)
                
            try:
                # Configure the API
                genai.configure(api_key=gemini_api_key)
                
                # Define the preferred model order (from newest to oldest)
                preferred_models = [
                    "gemini-2.5-pro-preview-03-25",  # Latest Gemini 2.5 Pro Preview
                    "gemini-2.5-pro-exp-03-25",      # Experimental version
                    "gemini-2.0-flash",              # Gemini 2.0 Flash
                    "gemini-2.0-flash-001",          # Stable version
                    "gemini-1.5-pro",                # Fallback to 1.5 if needed
                    "gemini-pro"                     # Legacy fallback
                ]
                
                # Use environment variable model name if available
                env_model = os.environ.get("LLM_MODEL_NAME", "")
                if env_model:
                    preferred_models.insert(0, env_model)
                
                # Try to use the latest client approach
                if hasattr(genai, 'Client'):
                    self.gemini_client = genai.Client()
                    logger.info("Connected to Google Gemini API using new client")
                    self.use_new_client = True
                    
                    # Try each model in order until one works
                    self.gemini_model_name = None
                    for model in preferred_models:
                        try:
                            # Test if the model is available by generating a simple response
                            response = self.gemini_client.generate_content(
                                model=model,
                                contents="Hello"
                            )
                            if response:
                                self.gemini_model_name = model
                                logger.info(f"Successfully connected to Gemini model: {model}")
                                break
                        except Exception as model_error:
                            logger.debug(f"Model {model} not available: {str(model_error)}")
                            continue
                    
                    if not self.gemini_model_name:
                        # If none of the preferred models work, list available models
                        available_models = []
                        try:
                            models = self.gemini_client.list_models()
                            for m in models:
                                if 'generateContent' in getattr(m, 'supported_generation_methods', []):
                                    available_models.append(m.name)
                                    logger.info(f"Available Gemini model: {m.name}")
                            
                            if available_models:
                                self.gemini_model_name = available_models[0]
                                logger.info(f"Using available model: {self.gemini_model_name}")
                            else:
                                raise Exception("No compatible Gemini models found")
                        except Exception as e:
                            logger.error(f"Failed to find usable Gemini models: {str(e)}")
                            raise
                else:
                    # Fallback to legacy GenerativeModel approach
                    self.use_new_client = False
                    
                    # List available models for debugging
                    try:
                        for m in genai.list_models():
                            if 'generateContent' in m.supported_generation_methods:
                                logger.info(f"Available Gemini model: {m.name}")
                    except Exception as e:
                        logger.warning(f"Could not list Gemini models: {e}")
                    
                    # Try preferred models in order
                    self.gemini_model = None
                    for model_name in preferred_models:
                        try:
                            self.gemini_model = genai.GenerativeModel(model_name)
                            # Test the model with a simple request
                            test_response = self.gemini_model.generate_content("Hello")
                            if test_response:
                                logger.info(f"Connected to Google Gemini API using model: {model_name}")
                                break
                        except Exception as model_error:
                            logger.debug(f"Could not use model {model_name}: {str(model_error)}")
                            self.gemini_model = None
                            continue
                    
                    # If none of the preferred models worked, fall back to default
                    if not self.gemini_model:
                        try:
                            self.gemini_model = genai.GenerativeModel("gemini-pro")
                            logger.info("Connected to Google Gemini API using fallback model: gemini-pro")
                        except Exception as fallback_error:
                            logger.error(f"Could not use any Gemini model: {str(fallback_error)}")
                            raise

            except Exception as e:
                logger.error(f"Failed to initialize Gemini API: {e}")
                traceback.print_exc()
                sys.exit(1)
                
            # Define function calling schema for Gemini
            self.gemini_tools = [
                {
                    "name": "categorize_content",
                    "description": "Categorize and structure the content from OCR text",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content_types": {
                                "type": "array",
                                "description": "List of content types identified in the text",
                                "items": {
                                    "type": "string",
                                    "enum": ["paragraph", "table", "list", "heading", "code", "api_key", "credentials", "url", "contact_info", "date_time"]
                                }
                            },
                            "topics": {
                                "type": "array",
                                "description": "Main topics or subject matter identified in the text",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "entities": {
                                "type": "array",
                                "description": "Named entities found in the text (people, organizations, products, etc.)",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "text": {"type": "string"},
                                        "type": {"type": "string", "enum": ["person", "organization", "location", "product", "other"]}
                                    }
                                }
                            },
                            "urls": {
                                "type": "array",
                                "description": "URLs extracted from the text",
                                "items": {"type": "string"}
                            },
                            "tables": {
                                "type": "array",
                                "description": "Tables extracted from the text, represented as arrays of rows",
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                }
                            },
                            "paragraphs": {
                                "type": "array",
                                "description": "Text paragraphs extracted from the content",
                                "items": {"type": "string"}
                            },
                            "contains_sensitive_info": {
                                "type": "boolean",
                                "description": "Whether the text contains sensitive information like API keys, passwords, etc."
                            },
                            "sensitive_info_explanation": {
                                "type": "string",
                                "description": "Explanation of what sensitive information was detected, if any"
                            },
                            "summary": {
                                "type": "string",
                                "description": "A brief summary of the content"
                            }
                        },
                        "required": ["content_types", "topics", "urls", "paragraphs", "contains_sensitive_info"]
                    }
                }
            ]
    
    def setup_storage_structure(self):
        """Set up structured storage directories for outputs"""
        storage_dir = os.environ.get("STORAGE_DIR", "all_frame_embeddings")
        self.storage_dir = Path(storage_dir)
        
        # Create main directory structure
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Create payloads directories
        self.payloads_dir = self.storage_dir / "payloads"
        os.makedirs(self.payloads_dir, exist_ok=True)
        
        # Create CSV directory
        self.csv_dir = self.payloads_dir / "csv"
        os.makedirs(self.csv_dir, exist_ok=True)
        
        # Create OCR directory
        self.ocr_dir = self.payloads_dir / "ocr"
        os.makedirs(self.ocr_dir, exist_ok=True)
        
        # Create structured OCR directory
        self.structured_ocr_dir = self.payloads_dir / "ocr_structured"
        os.makedirs(self.structured_ocr_dir, exist_ok=True)
        
        # Create JSON directory
        self.json_dir = self.payloads_dir / "json"
        os.makedirs(self.json_dir, exist_ok=True)
        
        # Create chunks directory
        self.chunks_dir = self.payloads_dir / "chunks"
        os.makedirs(self.chunks_dir, exist_ok=True)
        
        # Create logs directory
        self.logs_dir = self.storage_dir / "logs"
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Master logs directory
        self.master_logs_dir = self.logs_dir / "master_logs"
        os.makedirs(self.master_logs_dir, exist_ok=True)
        
        # Special purpose directories
        os.makedirs(self.storage_dir / "airtable", exist_ok=True)
        os.makedirs(self.storage_dir / "database", exist_ok=True)
        
        # Standard CSV file locations
        self.frames_csv_path = self.csv_dir / "processed_frames.csv"
        self.chunks_csv_path = self.csv_dir / "frame_chunks.csv"
        self.ocr_structured_csv_path = self.csv_dir / "ocr_structured_data.csv"
        
        # Set up CSV headers if files don't exist
        self._setup_csv_headers()
        
        logger.info(f"Set up structured storage in {self.storage_dir}")
        
    def _setup_csv_headers(self):
        """Set up CSV files with headers if they don't exist"""
        import csv
        
        # Processed frames CSV
        if not self.frames_csv_path.exists():
            with open(self.frames_csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "frame_id", 
                    "processed_time",
                    "frame_path",
                    "ocr_status",
                    "ocr_structured",
                    "flagged",
                    "topics",
                    "content_types",
                    "word_count",
                    "char_count",
                    "summary",
                    "api_keys_detected",
                    "ocr_processed_at"
                ])
        
        # Chunks CSV
        if not self.chunks_csv_path.exists():
            with open(self.chunks_csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "frame_id",
                    "chunk_index",
                    "chunk_text",
                    "processed_time",
                    "chunk_hash",
                    "content_length",
                    "source",
                    "ocr_data",
                    "has_ocr",
                    "is_flagged"
                ])
        
        # OCR structured data CSV
        if not self.ocr_structured_csv_path.exists():
            with open(self.ocr_structured_csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "frame_id", 
                    "raw_text_length", 
                    "topics", 
                    "content_types", 
                    "urls", 
                    "paragraphs_count", 
                    "is_flagged", 
                    "sensitive_explanation", 
                    "word_count", 
                    "char_count", 
                    "summary",
                    "processed_at"
                ])
    
    def detect_urls(self, text):
        """Extract URLs from OCR text"""
        return self.url_pattern.findall(text)
    
    def detect_api_keys(self, text):
        """Detect potential API keys in OCR text"""
        detected_keys = []
        for pattern in self.api_key_patterns:
            matches = pattern.findall(text)
            if matches:
                # Add only unique matches
                detected_keys.extend([m for m in matches if m not in detected_keys])
        return detected_keys
    
    def detect_google_sheets(self, text, urls):
        """Detect if text contains Google Sheets with potential API keys"""
        # Check if any Google Sheets URLs exist
        sheets_urls = [url for url in urls if 'docs.google.com/spreadsheets' in url or 'sheets.google.com' in url]
        
        # If we have Google Sheets URLs and potential API keys, flag it
        api_keys = self.detect_api_keys(text)
        
        is_sensitive = bool(sheets_urls and api_keys)
        
        return {
            "is_google_sheets": bool(sheets_urls),
            "sheets_urls": sheets_urls,
            "contains_api_keys": bool(api_keys),
            "api_keys": api_keys,
            "is_sensitive": is_sensitive
        }
    
    def extract_tables(self, text):
        """Extract potential table structures from OCR text"""
        lines = text.split('\n')
        potential_tables = []
        current_table = []
        
        # Simple heuristic: consecutive lines with similar structure of whitespace or separators
        # might be tables
        for line in lines:
            # Skip empty lines
            if not line.strip():
                if current_table:
                    if len(current_table) > 2:  # At least 3 rows to be a table
                        potential_tables.append(current_table.copy())
                    current_table = []
                continue
            
            # Check if line has table-like structure (multiple spaces or common separators)
            if re.search(r'\s{2,}', line) or re.search(r'[\|\t,;]', line):
                current_table.append(line)
            else:
                if current_table:
                    if len(current_table) > 2:  # At least 3 rows to be a table
                        potential_tables.append(current_table.copy())
                    current_table = []
        
        # Don't forget the last table if we ended on one
        if current_table and len(current_table) > 2:
            potential_tables.append(current_table)
        
        return potential_tables
    
    def categorize_with_gemini(self, text, frame_id=None):
        """Use Gemini API to categorize text content"""
        try:
            # Generate prompt for Gemini with explicit JSON output request
            prompt = f"""
            Analyze the following OCR text extracted from a screenshot or image.
            Categorize the content, extract structured information, and identify any sensitive information.
            
            OCR TEXT:
            {text}
            
            Return your analysis in the following JSON format:
            ```json
            {{
                "content_types": ["paragraph", "table", "list", "heading", "code", "api_key", "credentials", "url", "contact_info", "date_time"],
                "topics": ["topic1", "topic2"],
                "entities": [
                    {{"text": "entity1", "type": "person|organization|location|product|other"}},
                    {{"text": "entity2", "type": "person|organization|location|product|other"}}
                ],
                "urls": ["url1", "url2"],
                "tables": [
                    ["row1col1", "row1col2"],
                    ["row2col1", "row2col2"]
                ],
                "paragraphs": ["paragraph1", "paragraph2"],
                "contains_sensitive_info": true|false,
                "sensitive_info_explanation": "Explanation if sensitive info detected",
                "summary": "Brief summary of content"
            }}
            ```
            
            Pay special attention to API keys, access tokens, and other credentials that may be visible.
            API keys often follow patterns like:
            - Google API keys: starting with 'AIza'
            - AWS keys: starting with 'AKIA'
            - Stripe keys: starting with 'sk_test_' or 'pk_test_'
            
            If there are Google Sheets containing API keys, this is a serious security issue that should be flagged.
            
            Include only the fields that are relevant to the text. For content_types, include only the types that are present in the text.
            """
            
            # Log the Gemini request if master logger is available
            if self.master_logger and frame_id:
                model_name = self.gemini_model_name if hasattr(self, 'gemini_model_name') else "gemini-pro" 
                self.master_logger.log_gemini_request(frame_id, prompt, model_name)
            
            # Start time for logging
            start_time = time.time()
            
            # Call Gemini with either new client or legacy approach
            if hasattr(self, 'use_new_client') and self.use_new_client:
                # New client approach
                try:
                    response = self.gemini_client.generate_content(
                        model=self.gemini_model_name,
                        contents=prompt
                    )
                    response_text = response.text
                except Exception as e:
                    logger.warning(f"Failed with model {self.gemini_model_name}: {e}, trying fallback...")
                    # Try a more reliable fallback model
                    fallback_model = "gemini-pro"
                    response = self.gemini_client.generate_content(
                        model=fallback_model,
                        contents=prompt
                    )
                    response_text = response.text
            else:
                # Legacy approach
                response = self.gemini_model.generate_content(contents=prompt)
                response_text = response.text
            
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            
            # Log the Gemini response if master logger is available
            if self.master_logger and frame_id:
                model_name = self.gemini_model_name if hasattr(self, 'gemini_model_name') else "gemini-pro"
                self.master_logger.log_gemini_response(frame_id, response_text, model_name, elapsed_time)
            
            # Process the text as JSON
            try:
                # Try to find JSON content within the response
                json_content = response_text
                parsing_issues = None
                
                # If the response has markdown code blocks, extract the JSON
                if "```json" in response_text:
                    json_content = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    json_content = response_text.split("```")[1].split("```")[0].strip()
                
                # Parse the JSON content
                result = json.loads(json_content)
            except (json.JSONDecodeError, IndexError) as e:
                logger.warning(f"Could not parse JSON from Gemini response: {e}. Trying manual parsing.")
                parsing_issues = f"JSON parsing error: {str(e)}"
                
                # Fallback to manual parsing of the response text
                result = {
                    "content_types": [],
                    "topics": [],
                    "urls": self.detect_urls(text),
                    "paragraphs": [p.strip() for p in text.split('\n\n') if p.strip()],
                    "contains_sensitive_info": "api key" in response_text.lower() or "sensitive" in response_text.lower(),
                    "sensitive_info_explanation": "Potential sensitive information detected"
                }
                
                # Try to extract content types
                if "table" in response_text.lower():
                    result["content_types"].append("table")
                if "list" in response_text.lower():
                    result["content_types"].append("list")
                if "paragraph" in response_text.lower():
                    result["content_types"].append("paragraph")
                if "api key" in response_text.lower():
                    result["content_types"].append("api_key")
                if "url" in response_text.lower() or "http" in response_text.lower():
                    result["content_types"].append("url")
            
            # Enhanced API key detection
            api_keys = self.detect_api_keys(text)
            if api_keys and "api_key" not in result.get("content_types", []):
                result.setdefault("content_types", []).append("api_key")
                # Make sure we flag it as sensitive
                result["contains_sensitive_info"] = True
                result["sensitive_info_explanation"] = result.get("sensitive_info_explanation", "") + f"\nDetected API keys: {', '.join(api_keys[:3])}" + ("..." if len(api_keys) > 3 else "")
            
            # Process the Gemini result into our format
            categorized_data = {
                "urls": result.get("urls", []),
                "tables": result.get("tables", []),
                "paragraphs": result.get("paragraphs", []),
                "topics": result.get("topics", []),
                "entities": result.get("entities", []),
                "content_types": result.get("content_types", []),
                "is_flagged": result.get("contains_sensitive_info", False),
                "sensitive_explanation": result.get("sensitive_info_explanation", ""),
                "summary": result.get("summary", ""),
                "word_count": len(text.split()),
                "char_count": len(text),
                "api_keys_detected": bool(api_keys),
                "detected_api_keys": api_keys[:5] if api_keys else []  # Store up to 5 detected keys
            }
            
            # Additional processing for Google Sheets with API keys
            sheets_urls = [url for url in categorized_data["urls"] if 'docs.google.com/spreadsheets' in url or 'sheets.google.com' in url]
            if sheets_urls:
                categorized_data["google_sheets_info"] = {
                    "is_google_sheets": True,
                    "sheets_urls": sheets_urls,
                    "contains_api_keys": bool(api_keys),
                    "is_sensitive": bool(sheets_urls and api_keys)
                }
                
                # If we have both Google Sheets and API keys, make sure it's flagged
                if api_keys and not categorized_data["is_flagged"]:
                    categorized_data["is_flagged"] = True
                    categorized_data["sensitive_explanation"] = categorized_data.get("sensitive_explanation", "") + "\nAPI keys potentially exposed in Google Sheets."
            else:
                categorized_data["google_sheets_info"] = {
                    "is_google_sheets": False,
                    "sheets_urls": [],
                    "contains_api_keys": False,
                    "is_sensitive": False
                }
            
            # Log the parsed data if master logger is available
            if self.master_logger and frame_id:
                self.master_logger.log_parsed_data(frame_id, categorized_data, parsing_issues)
            
            return categorized_data
            
        except Exception as e:
            logger.error(f"Error using Gemini for categorization: {e}")
            traceback.print_exc()
            
            # Log the error if master logger is available
            if self.master_logger and frame_id:
                self.master_logger.log_error(
                    frame_id,
                    "gemini_categorization_error",
                    str(e),
                    traceback.format_exc()
                )
            
            return None
    
    def categorize_content(self, text, frame_id=None):
        """Categorize OCR content into structured data using either Gemini or rule-based approach"""
        if self.use_gemini:
            gemini_result = self.categorize_with_gemini(text, frame_id)
            if gemini_result:
                return gemini_result
                
        # Fallback to rule-based categorization if Gemini fails or is not enabled
        urls = self.detect_urls(text)
        tables = self.extract_tables(text)
        google_sheets_info = self.detect_google_sheets(text, urls)
        
        # Extract text blocks (paragraphs)
        paragraphs = []
        current_paragraph = []
        
        for line in text.split('\n'):
            if line.strip():
                current_paragraph.append(line)
            elif current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
        
        # Don't forget the last paragraph
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))
        
        # Create structured data
        categorized_data = {
            "urls": urls,
            "tables": tables,
            "paragraphs": paragraphs,
            "google_sheets_info": google_sheets_info,
            "is_flagged": google_sheets_info["is_sensitive"],
            "word_count": len(text.split()),
            "char_count": len(text),
            "topics": [],
            "entities": [],
            "content_types": ["paragraph"] if paragraphs else [],
            "sensitive_explanation": "Contains Google Sheets with API keys" if google_sheets_info["is_sensitive"] else "",
            "summary": paragraphs[0][:100] + "..." if paragraphs else "No meaningful content"
        }
        
        if tables:
            categorized_data["content_types"].append("table")
        if urls:
            categorized_data["content_types"].append("url")
            
        # Log the parsed data if master logger is available
        if self.master_logger and frame_id:
            self.master_logger.log_parsed_data(
                frame_id, 
                categorized_data, 
                "Generated using rule-based categorization (no Gemini)"
            )
        
        return categorized_data
    
    def format_for_airtable(self, categorized_data):
        """Format categorized data for Airtable"""
        # Create a formatted string for the OCRData column
        formatted_parts = []
        
        # Add summary if available
        if "summary" in categorized_data and categorized_data["summary"]:
            formatted_parts.append("Summary:\n" + categorized_data["summary"])
            
        # Add topics if available
        if "topics" in categorized_data and categorized_data["topics"]:
            formatted_parts.append("Topics:\n" + ", ".join(categorized_data["topics"]))
        
        # Add URLs if found
        if categorized_data["urls"]:
            formatted_parts.append("URLs:\n" + "\n".join(categorized_data["urls"]))
        
        # Add tables if found
        if categorized_data["tables"]:
            table_sections = []
            for i, table in enumerate(categorized_data["tables"], 1):
                if isinstance(table, list) and all(isinstance(row, str) for row in table):
                    # Standard format from rule-based approach
                    table_sections.append(f"Table {i}:\n" + "\n".join(table))
                elif isinstance(table, list) and isinstance(table[0], list):
                    # Nested list format from Gemini
                    table_sections.append(f"Table {i}:\n" + "\n".join([" | ".join(row) for row in table]))
            formatted_parts.append("Tables:\n" + "\n\n".join(table_sections))
        
        # Add entities if available
        if "entities" in categorized_data and categorized_data["entities"]:
            entities_text = []
            for entity in categorized_data["entities"]:
                if isinstance(entity, dict) and "text" in entity and "type" in entity:
                    entities_text.append(f"{entity['text']} ({entity['type']})")
                elif isinstance(entity, str):
                    entities_text.append(entity)
            if entities_text:
                formatted_parts.append("Entities:\n" + ", ".join(entities_text))
        
        # Add paragraphs if found
        if categorized_data["paragraphs"]:
            formatted_parts.append("Text Content:\n" + "\n\n".join(categorized_data["paragraphs"]))
        
        # Add sensitivity explanation if flagged
        if categorized_data["is_flagged"] and "sensitive_explanation" in categorized_data and categorized_data["sensitive_explanation"]:
            formatted_parts.append("⚠️ SENSITIVE CONTENT ALERT ⚠️\n" + categorized_data["sensitive_explanation"])
        
        # Join all parts with separators
        formatted_text = "\n\n---\n\n".join(formatted_parts) if formatted_parts else "No meaningful content detected"
        
        # Prepare Airtable record
        airtable_data = {
            "OCRData": formatted_text,
            "Flagged": categorized_data["is_flagged"],
            "OCRWordCount": categorized_data["word_count"],
            "OCRCharCount": categorized_data["char_count"],
            "OCRContainsURLs": bool(categorized_data["urls"]),
            "OCRContainsTables": bool(categorized_data["tables"]),
            "OCRLastUpdated": datetime.now().isoformat()
        }
        
        # Add topics if available
        if "topics" in categorized_data and categorized_data["topics"]:
            airtable_data["OCRTopics"] = ", ".join(categorized_data["topics"])
            
        # Add content types if available
        if "content_types" in categorized_data and categorized_data["content_types"]:
            airtable_data["OCRContentTypes"] = ", ".join(categorized_data["content_types"])
        
        return airtable_data
    
    def update_airtable_record(self, record_id, ocr_data):
        """Update a single Airtable record with OCR data"""
        if self.options.dry_run:
            logger.info(f"DRY RUN: Would update Airtable record {record_id} with OCR data")
            # Print the data that would be sent to Airtable
            logger.info("OCR Data for Airtable:")
            for key, value in ocr_data.items():
                if key == "OCRData":
                    # Truncate long text for display
                    display_value = value[:500] + "..." if len(value) > 500 else value
                    logger.info(f"  {key}: \n{display_value}")
                else:
                    logger.info(f"  {key}: {value}")
            return True
        
        # Apply rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_airtable_request_time
        
        if time_since_last_request < self.rate_limit_sleep:
            sleep_time = self.rate_limit_sleep - time_since_last_request
            logger.debug(f"Rate limiting: Sleeping for {sleep_time:.3f}s")
            time.sleep(sleep_time)
        
        try:
            self.airtable.update(record_id, ocr_data)
            self.last_airtable_request_time = time.time()
            logger.info(f"Updated Airtable record {record_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update Airtable record {record_id}: {e}")
            return False
    
    def find_airtable_record_by_frame_id(self, frame_id):
        """Find Airtable record ID by frame ID"""
        try:
            # Apply rate limiting
            current_time = time.time()
            time_since_last_request = current_time - self.last_airtable_request_time
            
            if time_since_last_request < self.rate_limit_sleep:
                sleep_time = self.rate_limit_sleep - time_since_last_request
                logger.debug(f"Rate limiting: Sleeping for {sleep_time:.3f}s")
                time.sleep(sleep_time)
            
            # This assumes there's a field in Airtable called "FrameID" that matches our frame_id
            records = self.airtable.all(formula=f"{{FrameID}}='{frame_id}'")
            self.last_airtable_request_time = time.time()
            
            if records:
                return records[0]["id"]
            return None
        except Exception as e:
            logger.error(f"Error searching for record with frame_id {frame_id}: {e}")
            return None
    
    def save_ocr_chunks_to_csv(self, frame_id: str, ocr_structured: dict, csv_file_path: str = None) -> bool:
        """
        Save OCR data for chunks to CSV file.
        
        Args:
            frame_id: ID of the frame
            ocr_structured: Structured OCR data
            csv_file_path: Path to the chunks CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import csv
            import os
            import json
            import hashlib
            from datetime import datetime
            from pathlib import Path
            
            # Determine CSV file path if not provided
            if not csv_file_path:
                # Try to find it in the standard location
                storage_dir = os.environ.get("STORAGE_DIR", "all_frame_embeddings")
                csv_file_path = os.path.join(storage_dir, "payloads", "csv", "frame_chunks.csv")
            
            csv_file = Path(csv_file_path)
            
            # Ensure parent directory exists
            csv_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists
            file_exists = csv_file.exists()
            
            # Extract paragraphs from OCR data to create chunks
            paragraphs = ocr_structured.get("paragraphs", [])
            if not paragraphs and "raw_text" in ocr_structured:
                # If no paragraphs but raw text exists, split by newlines
                paragraphs = [p for p in ocr_structured["raw_text"].split("\n\n") if p.strip()]
            
            # If no paragraphs, create a single chunk with all raw text
            if not paragraphs and "raw_text" in ocr_structured:
                paragraphs = [ocr_structured["raw_text"]]
            
            # If still no paragraphs, we can't create chunks
            if not paragraphs:
                logger.warning(f"No text content found for chunking in OCR data for {frame_id}")
                return False
            
            # Open CSV in append mode
            with open(csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                
                # Write header if new file
                if not file_exists:
                    writer.writerow([
                        "frame_id",
                        "chunk_index",
                        "chunk_text",
                        "processed_time",
                        "chunk_hash",
                        "content_length",
                        "source",
                        "ocr_data",
                        "has_ocr",
                        "is_flagged"
                    ])
                
                # Serialize the complete OCR data
                ocr_data_json = json.dumps(ocr_structured)
                
                # Get flagged status
                is_flagged = "1" if ocr_structured.get("contains_sensitive_info", False) else "0"
                
                # Write each paragraph as a chunk
                timestamp = datetime.now().isoformat()
                for i, paragraph in enumerate(paragraphs):
                    # Create hash
                    chunk_hash = hashlib.md5(paragraph.encode()).hexdigest()
                    
                    writer.writerow([
                        frame_id,                 # frame_id
                        i,                        # chunk_index
                        paragraph,                # chunk_text (full text content)
                        timestamp,                # processed_time
                        chunk_hash,               # chunk_hash
                        len(paragraph),           # content_length
                        "ocr_only",               # source
                        ocr_data_json,            # ocr_data (complete structured data)
                        "true",                   # has_ocr
                        is_flagged                # is_flagged
                    ])
            
            logger.info(f"Added {len(paragraphs)} OCR chunks to CSV for frame {frame_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving OCR chunks to CSV: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def process_ocr_file(self, ocr_file_path, frame_id):
        """Process a single OCR text file"""
        try:
            # Log start of OCR processing if master logger is available
            if self.master_logger:
                self.master_logger.log_ocr_processing(frame_id, "ocr_processing_start", {
                    "file_path": str(ocr_file_path),
                    "timestamp": datetime.now().isoformat()
                })
            
            with open(ocr_file_path, 'r', encoding='utf-8') as f:
                ocr_text = f.read()
            
            # Skip empty or nearly empty OCR results
            if len(ocr_text.strip()) < 10:
                logger.info(f"Skipping {ocr_file_path}: Not enough text content")
                
                # Log the issue if master logger is available
                if self.master_logger:
                    self.master_logger.log_ocr_processing(frame_id, "ocr_skipped", {
                        "reason": "Not enough text content",
                        "text_length": len(ocr_text.strip())
                    })
                
                return None
            
            # Log the raw OCR data if master logger is available
            if self.master_logger:
                self.master_logger.log_raw_ocr(frame_id, ocr_text, str(ocr_file_path))
            
            # Categorize and structure the OCR data
            categorized_data = self.categorize_content(ocr_text, frame_id)
            
            # Add raw text to the structured data for storage
            categorized_data["raw_text"] = ocr_text
            
            # Flag if this contains sensitive information
            is_flagged = categorized_data["is_flagged"]
            if is_flagged:
                flag_reason = categorized_data.get("sensitive_explanation", "Contains sensitive information")
                logger.warning(f"FLAGGED: {ocr_file_path} - {flag_reason}")
                self.flagged_count += 1
                
                # Log flagged content if master logger is available
                if self.master_logger:
                    self.master_logger.log_ocr_processing(frame_id, "content_flagged", {
                        "reason": flag_reason,
                        "detected_api_keys": categorized_data.get("detected_api_keys", []),
                        "is_google_sheets": categorized_data.get("google_sheets_info", {}).get("is_google_sheets", False)
                    })
            
            # Format for Airtable
            airtable_data = self.format_for_airtable(categorized_data)
            
            # Save structured data to JSON for reference
            output_json = self.structured_ocr_dir / f"{frame_id}_structured.json"
            os.makedirs(output_json.parent, exist_ok=True)
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(categorized_data, f, indent=2)
            
            # Save OCR chunks to CSV for text search
            self.save_ocr_chunks_to_csv(frame_id, categorized_data, str(self.chunks_csv_path))
            
            # Log successful OCR processing if master logger is available
            if self.master_logger:
                self.master_logger.log_ocr_processing(frame_id, "ocr_processing_complete", {
                    "output_json": str(output_json),
                    "is_flagged": is_flagged,
                    "word_count": categorized_data["word_count"],
                    "char_count": categorized_data["char_count"],
                    "topics": categorized_data.get("topics", []),
                    "content_types": categorized_data.get("content_types", [])
                })
            
            return airtable_data
            
        except Exception as e:
            logger.error(f"Error processing {ocr_file_path}: {e}")
            traceback.print_exc()
            self.error_count += 1
            
            # Log the error if master logger is available
            if self.master_logger:
                self.master_logger.log_error(
                    frame_id,
                    "ocr_processing_error",
                    str(e),
                    traceback.format_exc()
                )
            
            return None
    
    def update_csv_with_flags(self, frame_data):
        """Update the CSV file with flagged information"""
        try:
            # Read the CSV file
            rows = []
            with open(self.frames_csv_path, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader)
                
                # Check if we need to add columns
                columns_to_add = []
                if "flagged" not in header:
                    columns_to_add.append("flagged")
                if "api_keys_detected" not in header:
                    columns_to_add.append("api_keys_detected")
                if "ocr_processed_at" not in header:
                    columns_to_add.append("ocr_processed_at")
                
                if columns_to_add:
                    for col in columns_to_add:
                        header.append(col)
                
                # Process rows
                for row in reader:
                    # Check if this is the row for our frame
                    if len(row) > 2 and row[2] == frame_data["frame_id"]:  # Assuming frame_id is in column 3 (index 2)
                        # Extend row if needed
                        while len(row) < len(header):
                            row.append("")
                        
                        # Set flagged status
                        flag_index = header.index("flagged")
                        row[flag_index] = "1" if frame_data["is_flagged"] else "0"
                        
                        # Set API keys detected status if column exists
                        if "api_keys_detected" in header:
                            api_keys_index = header.index("api_keys_detected")
                            row[api_keys_index] = "1" if frame_data.get("api_keys_detected", False) else "0"
                        
                        # Update processed timestamp
                        if "ocr_processed_at" in header:
                            timestamp_index = header.index("ocr_processed_at")
                            row[timestamp_index] = datetime.now().isoformat()
                    
                    rows.append(row)
            
            # Write back to the CSV
            with open(self.frames_csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
            
            logger.info(f"Updated CSV file with flag for frame {frame_data['frame_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating CSV: {e}")
            traceback.print_exc()
            return False
    
    def process_all_frames(self):
        """Process all OCR text files and update Airtable"""
        logger.info(f"Starting OCR data processing from {self.input_dir}")
        logger.info(f"Reading frame information from {self.frames_csv_path}")
        logger.info(f"Using Gemini API for enhanced analysis: {self.use_gemini}")
        
        start_time = time.time()
        
        # Read CSV to get frame IDs and statuses
        frames_data = []
        try:
            with open(self.frames_csv_path, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader)
                
                # Find relevant column indices
                frame_id_idx = None
                ocr_status_idx = None
                
                for i, col in enumerate(header):
                    if col == "frame_id":
                        frame_id_idx = i
                    elif col == "ocr_status":
                        ocr_status_idx = i
                
                if frame_id_idx is None:
                    logger.error(f"Could not find 'frame_id' column in {self.frames_csv_path}")
                    return False
                
                # Process rows
                for row in reader:
                    if len(row) <= frame_id_idx:
                        continue
                    
                    frame_id = row[frame_id_idx]
                    ocr_status = row[ocr_status_idx] if ocr_status_idx is not None and len(row) > ocr_status_idx else None
                    
                    if frame_id and (ocr_status == "done" or ocr_status_idx is None):
                        frames_data.append({
                            "frame_id": frame_id,
                            "ocr_file": self.input_dir / f"{frame_id}.txt",
                            "is_flagged": False  # Will be updated during processing
                        })
        
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            traceback.print_exc()
            return False
        
        logger.info(f"Found {len(frames_data)} frames with OCR data to process")
        
        # Process each frame in batches
        batch_size = self.options.batch_size
        for i in range(0, len(frames_data), batch_size):
            batch = frames_data[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(frames_data)-1)//batch_size + 1} ({len(batch)} frames)")
            
            for frame_data in batch:
                ocr_file = frame_data["ocr_file"]
                frame_id = frame_data["frame_id"]
                
                if not ocr_file.exists():
                    logger.warning(f"OCR file not found for frame {frame_id}: {ocr_file}")
                    continue
                
                logger.info(f"Processing OCR data for frame {frame_id}")
                
                # Process the OCR file
                airtable_data = self.process_ocr_file(ocr_file, frame_id)
                if not airtable_data:
                    continue
                
                # Update flagged status in frame_data for CSV update
                frame_data["is_flagged"] = airtable_data["Flagged"]
                
                # Save structured data to CSV for chunking integration
                with open(self.ocr_structured_csv_path, 'a', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Get the raw structured data
                    structured_json_path = self.structured_ocr_dir / f"{frame_id}_structured.json"
                    if structured_json_path.exists():
                        with open(structured_json_path, 'r', encoding='utf-8') as json_file:
                            ocr_structured = json.load(json_file)
                            
                            # Write to CSV
                            writer.writerow([
                                frame_id,
                                ocr_structured.get("raw_text", ""),
                                "|".join(ocr_structured.get("topics", [])),
                                "|".join(ocr_structured.get("content_types", [])),
                                "|".join(ocr_structured.get("urls", [])),
                                "|".join(ocr_structured.get("paragraphs", [])),
                                "1" if ocr_structured.get("is_flagged", False) else "0",
                                ocr_structured.get("sensitive_explanation", ""),
                                ocr_structured.get("word_count", 0),
                                ocr_structured.get("char_count", 0),
                                ocr_structured.get("summary", ""),
                                datetime.now().isoformat()
                            ])
                
                # Update CSV with flagged status
                self.update_csv_with_flags(frame_data)
                
                # Display data if requested and not updating Airtable
                if self.options.display_data and not self.options.update_airtable:
                    logger.info(f"Formatted data for frame {frame_id}:")
                    for key, value in airtable_data.items():
                        if key == "OCRData":
                            # Truncate long text for display
                            display_value = value[:500] + "..." if len(value) > 500 else value
                            logger.info(f"  {key}: \n{display_value}")
                        else:
                            logger.info(f"  {key}: {value}")
                
                # Update Airtable if requested
                if self.options.update_airtable:
                    record_id = self.find_airtable_record_by_frame_id(frame_id)
                    if record_id:
                        self.update_airtable_record(record_id, airtable_data)
                    else:
                        logger.warning(f"No Airtable record found for frame {frame_id}")
                        # Display the data even if record not found
                        if self.options.dry_run or self.options.display_data:
                            logger.info(f"Data that would be sent to Airtable for frame {frame_id}:")
                            for key, value in airtable_data.items():
                                if key == "OCRData":
                                    # Truncate long text for display
                                    display_value = value[:500] + "..." if len(value) > 500 else value
                                    logger.info(f"  {key}: \n{display_value}")
                                else:
                                    logger.info(f"  {key}: {value}")
                
                self.processed_count += 1
            
            # Log progress after each batch
            elapsed = time.time() - start_time
            frames_per_sec = (i + len(batch)) / elapsed if elapsed > 0 else 0
            logger.info(f"Processed {i + len(batch)}/{len(frames_data)} frames "
                       f"({(i + len(batch))/len(frames_data)*100:.1f}%) - "
                       f"{frames_per_sec:.2f} frames/sec")
        
        # Final summary
        elapsed = time.time() - start_time
        logger.info("\nOCR Data Processing Summary:")
        logger.info(f"Total frames processed: {self.processed_count}")
        logger.info(f"Frames flagged as sensitive: {self.flagged_count}")
        logger.info(f"Errors encountered: {self.error_count}")
        logger.info(f"Total processing time: {elapsed:.2f} seconds")
        logger.info(f"Average processing speed: {self.processed_count/elapsed:.2f} frames/sec if elapsed > 0 else 'N/A'")
        logger.info(f"Used Gemini API for enhanced analysis: {self.use_gemini}")
        logger.info(f"Structured OCR data saved to: {self.ocr_structured_csv_path}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Process OCR data and update Airtable')
    
    parser.add_argument('--input-dir', default='ocr_results', 
                       help='Directory containing OCR text files')
    parser.add_argument('--csv-file', default='processed_frames.csv',
                       help='CSV file with processed frames data')
    parser.add_argument('--update-airtable', action='store_true',
                       help='Update Airtable with processed OCR data')
    parser.add_argument('--base-id', help='Airtable base ID')
    parser.add_argument('--table-name', help='Airtable table name')
    parser.add_argument('--api-key', help='Airtable API key')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Number of records to process in each batch')
    parser.add_argument('--dry-run', action='store_true',
                       help="Don't update Airtable, just show what would be updated")
    parser.add_argument('--display-data', action='store_true',
                       help="Display the formatted data, even without Airtable connection")
    parser.add_argument('--use-gemini', action='store_true',
                       help='Use Google Gemini API for enhanced text analysis')
    parser.add_argument('--gemini-api-key', 
                       help='API key for Google Gemini (required when using --use-gemini)')
    
    args = parser.parse_args()
    
    # Validate args when updating Airtable
    if args.update_airtable and not (args.base_id and args.table_name and args.api_key):
        parser.error("--base-id, --table-name, and --api-key are required when using --update-airtable")
        
    # Validate Gemini API key if using Gemini
    if args.use_gemini and not args.gemini_api_key:
        parser.error("--gemini-api-key is required when using --use-gemini")
    
    processor = OCRDataProcessor(args)
    processor.process_all_frames()

if __name__ == "__main__":
    main() 