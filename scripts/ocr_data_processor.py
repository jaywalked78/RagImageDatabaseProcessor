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
            
            if not (options.base_id and options.table_name and options.api_key):
                logger.error("Airtable base ID, table name, and API key are required")
                sys.exit(1)
            
            try:
                self.airtable = Table(options.api_key, options.base_id, options.table_name)
                logger.info(f"Connected to Airtable: {options.base_id}/{options.table_name}")
                logger.info(f"Airtable rate limiting enabled: {AIRTABLE_RATE_LIMIT_SLEEP}s between requests")
            except Exception as e:
                logger.error(f"Failed to connect to Airtable: {e}")
                traceback.print_exc()
                sys.exit(1)
                
        # Initialize Gemini if requested
        if self.use_gemini:
            if not GEMINI_AVAILABLE:
                logger.error("Cannot use Gemini: google-generativeai package not installed")
                sys.exit(1)
                
            if not options.gemini_api_key:
                logger.error("Gemini API key is required when using --use-gemini")
                sys.exit(1)
                
            try:
                genai.configure(api_key=options.gemini_api_key)
                # Set up the model
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("Connected to Google Gemini API")
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
    
    def categorize_with_gemini(self, text):
        """Use Gemini API to categorize text content"""
        try:
            # Generate prompt for Gemini
            prompt = f"""
            Analyze the following OCR text extracted from a screenshot or image.
            Categorize the content, extract structured information, and identify any sensitive information.
            
            OCR TEXT:
            {text}
            """
            
            # Call Gemini with function calling
            response = self.gemini_model.generate_content(
                contents=prompt,
                tools=self.gemini_tools,
                tool_choice={"type": "function", "function": {"name": "categorize_content"}}
            )
            
            # Extract the function calling result
            function_call = response.candidates[0].content.parts[0].function_call
            result = json.loads(function_call.args["categorize_content"])
            
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
                "char_count": len(text)
            }
            
            # Additional processing for Google Sheets with API keys
            sheets_urls = [url for url in categorized_data["urls"] if 'docs.google.com/spreadsheets' in url or 'sheets.google.com' in url]
            if sheets_urls and categorized_data["is_flagged"]:
                categorized_data["google_sheets_info"] = {
                    "is_google_sheets": True,
                    "sheets_urls": sheets_urls,
                    "contains_api_keys": True,
                    "is_sensitive": True
                }
            else:
                categorized_data["google_sheets_info"] = {
                    "is_google_sheets": bool(sheets_urls),
                    "sheets_urls": sheets_urls,
                    "contains_api_keys": False,
                    "is_sensitive": False
                }
            
            return categorized_data
            
        except Exception as e:
            logger.error(f"Error using Gemini for categorization: {e}")
            traceback.print_exc()
            return None
    
    def categorize_content(self, text):
        """Categorize OCR content into structured data using either Gemini or rule-based approach"""
        if self.use_gemini:
            gemini_result = self.categorize_with_gemini(text)
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
            return True
        
        # Apply rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_airtable_request_time
        
        if time_since_last_request < AIRTABLE_RATE_LIMIT_SLEEP:
            sleep_time = AIRTABLE_RATE_LIMIT_SLEEP - time_since_last_request
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
            
            if time_since_last_request < AIRTABLE_RATE_LIMIT_SLEEP:
                sleep_time = AIRTABLE_RATE_LIMIT_SLEEP - time_since_last_request
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
    
    def process_ocr_file(self, ocr_file_path, frame_id):
        """Process a single OCR text file"""
        try:
            with open(ocr_file_path, 'r', encoding='utf-8') as f:
                ocr_text = f.read()
            
            # Skip empty or nearly empty OCR results
            if len(ocr_text.strip()) < 10:
                logger.info(f"Skipping {ocr_file_path}: Not enough text content")
                return None
            
            # Categorize and structure the OCR data
            categorized_data = self.categorize_content(ocr_text)
            
            # Flag if this contains sensitive information
            is_flagged = categorized_data["is_flagged"]
            if is_flagged:
                flag_reason = categorized_data.get("sensitive_explanation", "Contains sensitive information")
                logger.warning(f"FLAGGED: {ocr_file_path} - {flag_reason}")
                self.flagged_count += 1
            
            # Format for Airtable
            airtable_data = self.format_for_airtable(categorized_data)
            
            # Save structured data to JSON for reference
            output_json = ocr_file_path.parent / f"{ocr_file_path.stem}_structured.json"
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(categorized_data, f, indent=2)
            
            return airtable_data
            
        except Exception as e:
            logger.error(f"Error processing {ocr_file_path}: {e}")
            traceback.print_exc()
            self.error_count += 1
            return None
    
    def update_csv_with_flags(self, frame_data):
        """Update the CSV file with flagged information"""
        try:
            # Read the CSV file
            rows = []
            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.reader(f)
                header = next(reader)
                
                # Check if we need to add a "flagged" column
                if "flagged" not in header:
                    header.append("flagged")
                
                # Process rows
                for row in reader:
                    # Check if this is the row for our frame
                    if row[3] == frame_data["frame_id"]:  # Assuming frame_id is in column 4 (index 3)
                        # Extend row if needed
                        while len(row) < len(header):
                            row.append("")
                        
                        # Set flagged status
                        flag_index = header.index("flagged")
                        row[flag_index] = "1" if frame_data["is_flagged"] else "0"
                    
                    rows.append(row)
            
            # Write back to the CSV
            with open(self.csv_file, 'w', newline='') as f:
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
        logger.info(f"Reading frame information from {self.csv_file}")
        logger.info(f"Using Gemini API for enhanced analysis: {self.use_gemini}")
        
        start_time = time.time()
        
        # Read CSV to get frame IDs and statuses
        frames_data = []
        try:
            with open(self.csv_file, 'r', newline='') as f:
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
                    logger.error(f"Could not find 'frame_id' column in {self.csv_file}")
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
                
                # Update CSV with flagged status
                self.update_csv_with_flags(frame_data)
                
                # Update Airtable if requested
                if self.options.update_airtable:
                    record_id = self.find_airtable_record_by_frame_id(frame_id)
                    if record_id:
                        self.update_airtable_record(record_id, airtable_data)
                    else:
                        logger.warning(f"No Airtable record found for frame {frame_id}")
                
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