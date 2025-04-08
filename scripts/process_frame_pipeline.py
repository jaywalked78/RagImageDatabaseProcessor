#!/usr/bin/env python3
"""
End-to-End Frame Processing Pipeline

This script demonstrates the complete pipeline for processing frames:
1. Get frame information from Airtable
2. Locate the frame file on local drive
3. Perform OCR on the image
4. Process OCR data using Gemini LLM with API key rotation
5. Store structured data in both Airtable and PostgreSQL
6. Create hybrid embeddings (chunked metadata with OCR data)

Usage:
  python process_frame_pipeline.py --frame-id FRAME_ID [options]

Options:
  --frame-id ID            Frame ID to process
  --storage-dir DIR        Directory to store results (default: all_frame_embeddings)
  --batch-size N           Number of frames to process in each batch (default: 5)
  --dry-run                Run without making actual Airtable/DB updates
  --verbose                Enable verbose logging
"""

import os
import sys
import time
import json
import argparse
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import concurrent.futures
import traceback
import google.generativeai as genai
from api_key_rotation import ApiKeyRotator, GeminiKeyRotator

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import custom modules
from api_key_rotation import get_next_gemini_key, mark_gemini_key_error, mark_gemini_key_success
# Import OCR data processor for saving chunks
from scripts.ocr_data_processor import OCRDataProcessor

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai package not installed. Gemini features will be disabled.")
    print("Install with: pip install google-generativeai")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_STORAGE_DIR = "all_frame_embeddings"
DEFAULT_MODEL = "gemini-2.0-flash-thinking-exp"
DEFAULT_BATCH_SIZE = 5
MAX_CONCURRENT_PROCESSES = 3  # Maximum number of concurrent processes

class MasterLogger:
    """Handles detailed logging of the OCR processing pipeline."""
    
    def __init__(self, storage_dir: str):
        self.storage_dir = storage_dir
        self.logs_dir = Path(f"{storage_dir}/logs")
        self.master_log_dir = Path(f"{storage_dir}/logs/master_logs")
        
        # Create log directories
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.master_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for this run
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Create master log file
        self.master_log_file = Path(f"{self.master_log_dir}/master_log_{self.timestamp}.jsonl")
        
        logger.info(f"Master logging initialized: {self.master_log_file}")
    
    def log_ocr_processing(self, frame_id: str, entry_type: str, data: Dict[str, Any]) -> None:
        """
        Log OCR processing steps to the master log file.
        
        Args:
            frame_id: The ID of the frame being processed
            entry_type: Type of log entry (raw_ocr, gemini_response, parsed_data, etc.)
            data: The data to log
        """
        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "frame_id": frame_id,
                "entry_type": entry_type,
                "data": data
            }
            
            # Append to the master log file (JSONL format - one JSON object per line)
            with open(self.master_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Error writing to master log: {str(e)}")
            traceback.print_exc()
    
    def log_frame_processing_start(self, frame_id: str) -> None:
        """Log the start of frame processing."""
        self.log_ocr_processing(frame_id, "processing_start", {
            "message": f"Started processing frame {frame_id}",
            "timestamp": datetime.now().isoformat()
        })
    
    def log_frame_processing_complete(self, frame_id: str, status: str, 
                                     elapsed_time: float, details: Dict[str, Any]) -> None:
        """Log the completion of frame processing."""
        self.log_ocr_processing(frame_id, "processing_complete", {
            "message": f"Completed processing frame {frame_id}",
            "status": status,
            "elapsed_time_seconds": elapsed_time,
            "details": details
        })
    
    def log_raw_ocr(self, frame_id: str, ocr_text: str, file_path: str) -> None:
        """Log the raw OCR text extracted from the frame."""
        self.log_ocr_processing(frame_id, "raw_ocr", {
            "ocr_text": ocr_text,
            "file_path": str(file_path),
            "char_count": len(ocr_text),
            "word_count": len(ocr_text.split()) if ocr_text else 0,
            "line_count": len(ocr_text.splitlines()) if ocr_text else 0
        })
    
    def log_gemini_request(self, frame_id: str, prompt: str, model: str) -> None:
        """Log the prompt sent to Gemini API."""
        self.log_ocr_processing(frame_id, "gemini_request", {
            "prompt": prompt,
            "model": model,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_gemini_response(self, frame_id: str, response_text: str, 
                           model: str, elapsed_time: float) -> None:
        """Log the response received from Gemini API."""
        self.log_ocr_processing(frame_id, "gemini_response", {
            "response_text": response_text,
            "model": model,
            "elapsed_time_seconds": elapsed_time,
            "response_length": len(response_text)
        })
    
    def log_parsed_data(self, frame_id: str, structured_data: Dict[str, Any], 
                       parsing_issues: Optional[str] = None) -> None:
        """Log the parsed structured data extracted from Gemini's response."""
        self.log_ocr_processing(frame_id, "parsed_data", {
            "structured_data": structured_data,
            "parsing_issues": parsing_issues
        })
    
    def log_csv_save(self, frame_id: str, csv_type: str, file_path: str, 
                    row_count: int, fields: List[str]) -> None:
        """Log details about CSV data being saved."""
        self.log_ocr_processing(frame_id, "csv_save", {
            "csv_type": csv_type,
            "file_path": str(file_path),
            "row_count": row_count,
            "fields": fields
        })
    
    def log_error(self, frame_id: str, error_type: str, error_message: str, 
                 traceback_str: str) -> None:
        """Log error details during processing."""
        self.log_ocr_processing(frame_id, "error", {
            "error_type": error_type,
            "error_message": error_message,
            "traceback": traceback_str
        })

class FrameProcessor:
    """Process frames through the complete pipeline."""
    
    def __init__(self, options):
        """Initialize the frame processor with options."""
        self.options = options
        self.storage_dir = options.storage_dir
        self.dry_run = options.dry_run
        self.verbose = options.verbose
        self.batch_size = options.batch_size
        self.processed_count = 0
        self.error_count = 0
        
        # Set up storage directories
        self.setup_directories()
        
        # Set up CSV files for storing results
        self.setup_csv_files()
        
        # Set up Gemini if available
        self.setup_gemini()
        
        # Initialize master logger
        self.master_logger = MasterLogger(self.storage_dir)
        
        # Set up regular log file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = f"{self.storage_dir}/logs/pipeline_{timestamp}.log"
        
        logger.info(f"Initialized Frame Processor with storage dir: {self.storage_dir}")
        logger.info(f"Log file: {self.log_file}")
        if self.dry_run:
            logger.info("Running in DRY RUN mode - no actual updates will be made")
        
        # Initialize API key rotation if available
        self.gemini_key_rotator = None
        if hasattr(options, 'gemini_api_keys') and options.gemini_api_keys:
            self.gemini_key_rotator = GeminiKeyRotator(options.gemini_api_keys.split(','))
            logger.info(f"Initialized Gemini API key rotation with {len(options.gemini_api_keys.split(','))} keys")
        else:
            # Try to get API keys from environment
            gemini_keys = []
            for i in range(1, 6):  # Check for GEMINI_API_KEY_1 through GEMINI_API_KEY_5
                key_name = f"GEMINI_API_KEY_{i}"
                if key_name in os.environ and os.environ[key_name]:
                    gemini_keys.append(os.environ[key_name])
            
            # If no numbered keys found, try the main GEMINI_API_KEY
            if not gemini_keys and "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"]:
                gemini_keys.append(os.environ["GEMINI_API_KEY"])
            # If still no keys, try GOOGLE_API_KEY as fallback
            elif not gemini_keys and "GOOGLE_API_KEY" in os.environ and os.environ["GOOGLE_API_KEY"]:
                gemini_keys.append(os.environ["GOOGLE_API_KEY"])
            
            if gemini_keys:
                self.gemini_key_rotator = GeminiKeyRotator(gemini_keys)
                logger.info(f"Initialized Gemini API key rotation with {len(gemini_keys)} keys from environment")
            else:
                logger.warning("No Gemini API keys found. OCR processing with Gemini will be disabled.")
    
    def setup_directories(self):
        """Set up necessary directories for storage."""
        # Main directories
        os.makedirs(f"{self.storage_dir}/payloads/json", exist_ok=True)
        os.makedirs(f"{self.storage_dir}/payloads/csv", exist_ok=True)
        os.makedirs(f"{self.storage_dir}/payloads/ocr", exist_ok=True)
        os.makedirs(f"{self.storage_dir}/payloads/chunks", exist_ok=True)
        os.makedirs(f"{self.storage_dir}/logs", exist_ok=True)
        os.makedirs(f"{self.storage_dir}/logs/master_logs", exist_ok=True)
        
    def setup_csv_files(self):
        """Set up CSV files for storing frame and chunk data."""
        # Single frame CSV file
        self.frames_csv = Path(f"{self.storage_dir}/payloads/csv/processed_frames.csv")
        
        # Create frames CSV with header if it doesn't exist
        if not self.frames_csv.exists():
            os.makedirs(self.frames_csv.parent, exist_ok=True)
            with open(self.frames_csv, 'w', encoding='utf-8', newline='') as f:
                import csv
                writer = csv.writer(f)
                writer.writerow([
                    "frame_id", 
                    "processed_time", 
                    "frame_path", 
                    "ocr_status",
                    "ocr_structured",
                    "ocr_data",  # Full serialized JSON data
                    "topics",
                    "content_types",
                    "is_flagged",
                    "word_count",
                    "char_count",
                    "summary"
                ])
            logger.info(f"Created new single frame CSV: {self.frames_csv}")
        
        # Chunked frames CSV file
        self.chunks_csv = Path(f"{self.storage_dir}/payloads/csv/frame_chunks.csv")
        
        # Create chunks CSV with header if it doesn't exist
        if not self.chunks_csv.exists():
            os.makedirs(self.chunks_csv.parent, exist_ok=True)
            with open(self.chunks_csv, 'w', encoding='utf-8', newline='') as f:
                import csv
                writer = csv.writer(f)
                writer.writerow([
                    "frame_id",
                    "chunk_index",
                    "chunk_text",
                    "processed_time",
                    "chunk_hash",
                    "content_length",
                    "source",
                    "ocr_data",  # OCR data for this chunk
                    "has_ocr",
                    "is_flagged"
                ])
            logger.info(f"Created new chunks CSV: {self.chunks_csv}")
    
    def setup_gemini(self):
        """Set up Gemini API with our preferred model."""
        if not GEMINI_AVAILABLE:
            logger.error("Gemini API not available. Install google-generativeai package.")
            self.gemini_available = False
            return
        
        self.gemini_available = True
        
        # Get first key to initialize Gemini (will rotate keys later per request)
        api_key = get_next_gemini_key()
        genai.configure(api_key=api_key)
        
        logger.info("Gemini API initialized with rotating API keys")
        logger.info(f"Using preferred model: {DEFAULT_MODEL}")
    
    def save_to_csv(self, frame_id: str, frame_data: Dict[str, Any]) -> bool:
        """
        Save processed frame data to CSV file.
        
        Args:
            frame_id: The ID of the frame
            frame_data: Complete frame data including OCR
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Saving frame data to CSV for {frame_id}")
        
        try:
            import csv
            import json
            
            # Get OCR data if available
            ocr_data_json = ""
            topics = ""
            content_types = ""
            is_flagged = "0"
            word_count = "0"
            char_count = "0"
            summary = ""
            
            if "structured_data" in frame_data and frame_data["structured_data"]:
                structured_data = frame_data["structured_data"]
                # Serialize the OCR data to JSON string
                ocr_data_json = json.dumps(structured_data)
                
                # Extract specific fields
                topics = "|".join(structured_data.get("topics", []))
                content_types = "|".join(structured_data.get("content_types", []))
                is_flagged = "1" if structured_data.get("contains_sensitive_info", False) else "0"
                word_count = str(structured_data.get("word_count", 0))
                char_count = str(structured_data.get("char_count", 0))
                summary = structured_data.get("summary", "")
            
            # Prepare row data
            row = [
                frame_id,
                datetime.now().isoformat(),
                frame_data.get("frame_path", ""),
                frame_data.get("ocr_status", ""),
                "true" if "ocr_structured" in frame_data and frame_data["ocr_structured"] else "false",
                ocr_data_json,
                topics,
                content_types,
                is_flagged,
                word_count,
                char_count,
                summary
            ]
            
            # Get fields list for logging
            fields = [
                "frame_id", 
                "processed_time", 
                "frame_path", 
                "ocr_status",
                "ocr_structured",
                "ocr_data", 
                "topics",
                "content_types",
                "is_flagged",
                "word_count",
                "char_count",
                "summary"
            ]
            
            # Detailed logging about the data being saved
            is_flagged_bool = is_flagged == "1"
            truncated_summary = summary[:100] + "..." if len(summary) > 100 else summary
            logger.info(f"CSV OUTPUT: {self.frames_csv}")
            logger.info(f"CSV OUTPUT FIELDS: {', '.join(fields)}")
            logger.info(f"CSV DATA SUMMARY: Frame {frame_id} | OCR Status: {frame_data.get('ocr_status', '')} | Words: {word_count} | Flagged: {is_flagged_bool}")
            if topics:
                logger.info(f"CSV TOPICS: {topics}")
            if truncated_summary:
                logger.info(f"CSV SUMMARY: {truncated_summary}")
            
            # Append to CSV
            file_exists = self.frames_csv.exists()
            with open(self.frames_csv, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(row)
            
            # Log the CSV save operation
            self.master_logger.log_csv_save(
                frame_id,
                "frames_csv",
                str(self.frames_csv),
                1,  # One row added
                fields
            )
            
            logger.info(f"Successfully saved frame data to CSV for {frame_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving frame data to CSV for {frame_id}: {str(e)}")
            
            # Log the error
            self.master_logger.log_error(
                frame_id,
                "csv_save_exception",
                str(e),
                traceback.format_exc()
            )
            
            return False
    
    def process_single_frame(self, frame_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Process a single frame through the complete pipeline.
        
        Args:
            frame_id: The ID of the frame to process
            
        Returns:
            Tuple of (success, frame_data)
        """
        logger.info(f"Processing frame: {frame_id}")
        frame_data = {"frame_id": frame_id, "status": "started"}
        
        # Log the start of frame processing
        self.master_logger.log_frame_processing_start(frame_id)
        start_time = time.time()
        
        try:
            # 1. Get frame information from Airtable
            frame_info = self.get_frame_info(frame_id)
            if not frame_info:
                logger.error(f"Could not get frame info for {frame_id}")
                frame_data["status"] = "error_no_info"
                self.error_count += 1
                
                # Log completion with error
                elapsed_time = time.time() - start_time
                self.master_logger.log_frame_processing_complete(
                    frame_id,
                    "error_no_info",
                    elapsed_time,
                    {"error": "Could not get frame information"}
                )
                
                return False, frame_data
            
            frame_data.update(frame_info)
            
            # 2. Locate the frame file on local drive
            frame_path = self.find_frame_file(frame_id, frame_info)
            if not frame_path:
                logger.error(f"Could not find frame file for {frame_id}")
                frame_data["status"] = "error_no_file"
                self.error_count += 1
                
                # Log completion with error
                elapsed_time = time.time() - start_time
                self.master_logger.log_frame_processing_complete(
                    frame_id,
                    "error_no_file",
                    elapsed_time,
                    {"error": "Could not find frame file"}
                )
                
                return False, frame_data
            
            frame_data["frame_path"] = str(frame_path)
            
            # 3. Process OCR if needed
            ocr_status, ocr_data = self.process_ocr(frame_id, frame_path)
            frame_data["ocr_status"] = ocr_status
            
            if ocr_status == "error":
                frame_data["status"] = "error_ocr_failed"
                self.error_count += 1
                
                # Log completion with error
                elapsed_time = time.time() - start_time
                self.master_logger.log_frame_processing_complete(
                    frame_id,
                    "error_ocr_failed",
                    elapsed_time,
                    {"error": "OCR processing failed"}
                )
                
                return False, frame_data
            
            # 4. Process OCR data with Gemini if available
            if ocr_status == "done" and self.gemini_available:
                structured_data = self.process_ocr_with_gemini(frame_id, ocr_data)
                frame_data["ocr_structured"] = True if structured_data else False
                frame_data["structured_data"] = structured_data
            
            # 5. Save to single frame CSV
            csv_status = self.save_to_csv(frame_id, frame_data)
            frame_data["csv_status"] = csv_status
            
            # 6. Store data in database
            if not self.dry_run:
                db_status = self.store_in_database(frame_id, frame_data)
                frame_data["db_status"] = db_status
            
            # 7. Create metadata chunks with OCR data
            chunks_status = self.create_chunks(frame_id, frame_path, frame_data)
            frame_data["chunks_status"] = chunks_status
            
            # 8. Update Airtable with results
            if not self.dry_run:
                airtable_status = self.update_airtable(frame_id, frame_data)
                frame_data["airtable_status"] = airtable_status
            
            # Mark as complete
            frame_data["status"] = "completed"
            self.processed_count += 1
            
            # Log completion with success
            elapsed_time = time.time() - start_time
            self.master_logger.log_frame_processing_complete(
                frame_id,
                "completed",
                elapsed_time,
                {
                    "ocr_status": ocr_status,
                    "ocr_structured": frame_data.get("ocr_structured", False),
                    "csv_status": csv_status,
                    "chunks_status": chunks_status
                }
            )
            
            return True, frame_data
            
        except Exception as e:
            logger.error(f"Error processing frame {frame_id}: {str(e)}")
            
            # Log the error
            self.master_logger.log_error(
                frame_id,
                "processing_exception",
                str(e),
                traceback.format_exc()
            )
            
            frame_data["status"] = "error_exception"
            frame_data["error"] = str(e)
            self.error_count += 1
            
            # Log completion with error
            elapsed_time = time.time() - start_time
            self.master_logger.log_frame_processing_complete(
                frame_id,
                "error_exception",
                elapsed_time,
                {"error": str(e)}
            )
            
            return False, frame_data
    
    def get_frame_info(self, frame_id: str) -> Optional[Dict[str, Any]]:
        """
        Get frame information from Airtable.
        
        Args:
            frame_id: The ID of the frame
            
        Returns:
            Dictionary of frame information or None if not found
        """
        # In a real implementation, this would query Airtable
        # For this demo, we'll return fake data
        logger.info(f"Getting frame info for {frame_id}")
        
        if self.dry_run:
            # Return mock data
            return {
                "frame_id": frame_id,
                "frame_number": 123,
                "folder_name": "test_folder",
                "file_name": f"{frame_id}.jpg",
                "timestamp": "2023-01-01_12-34-56",
                "metadata": {
                    "Summary": "Test frame for processing",
                    "ActionsDetected": "Typing code",
                    "StageOfWork": "Development",
                    "TechnicalDetails": "Python script development"
                }
            }
        
        # This would be a real Airtable API call in production
        logger.warning("Not implemented: This would query Airtable in production")
        return None
    
    def find_frame_file(self, frame_id: str, frame_info: Dict[str, Any]) -> Optional[Path]:
        """
        Find the actual frame file on the local drive.
        
        Args:
            frame_id: The ID of the frame
            frame_info: Frame information from Airtable
            
        Returns:
            Path to the frame file or None if not found
        """
        # In a real implementation, this would search for the file
        # For this demo, we'll use a placeholder path
        logger.info(f"Finding frame file for {frame_id}")
        
        if self.dry_run:
            # Return a mock path that doesn't have to exist
            mock_path = Path(f"{self.storage_dir}/test_frames/{frame_id}.jpg")
            os.makedirs(mock_path.parent, exist_ok=True)
            # Create an empty file for testing
            mock_path.touch()
            return mock_path
        
        # This would do a real search in production
        logger.warning("Not implemented: This would find the actual file in production")
        return None
    
    def process_ocr(self, frame_id: str, frame_path: Path) -> Tuple[str, Optional[str]]:
        """
        Process OCR on the frame image if needed.
        
        Args:
            frame_id: The ID of the frame
            frame_path: Path to the frame image file
            
        Returns:
            Tuple of (status, ocr_text)
        """
        logger.info(f"Processing OCR for {frame_id}")
        
        # Check if OCR already exists
        ocr_file = Path(f"{self.storage_dir}/payloads/ocr/{frame_id}.txt")
        if ocr_file.exists():
            logger.info(f"OCR already exists for {frame_id}")
            with open(ocr_file, 'r', encoding='utf-8') as f:
                ocr_text = f.read()
            
            # Log the raw OCR data
            self.master_logger.log_raw_ocr(frame_id, ocr_text, str(ocr_file))
            
            return "done", ocr_text
        
        # For dry run, create a mock OCR file
        if self.dry_run:
            mock_ocr_text = (
                "This is a sample OCR text from a screen recording.\n"
                "It shows some code editing in VSCode.\n"
                "def process_data(input_file):\n"
                "    with open(input_file, 'r') as f:\n"
                "        data = json.load(f)\n"
                "    return process_items(data)\n\n"
                "# API Keys visible in the terminal:\n"
                "GOOGLE_API_KEY=AIzaSyCyGJsEqISKbVgNwBh_imanae-Nxsu-7JU\n"
                "https://docs.google.com/spreadsheets/d/1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q8R9/edit"
            )
            os.makedirs(ocr_file.parent, exist_ok=True)
            with open(ocr_file, 'w', encoding='utf-8') as f:
                f.write(mock_ocr_text)
            logger.info(f"Created mock OCR file for {frame_id}")
            
            # Log the raw OCR data
            self.master_logger.log_raw_ocr(frame_id, mock_ocr_text, str(ocr_file))
            
            return "done", mock_ocr_text
        
        # In production, run Tesseract OCR
        try:
            # Check if tesseract is installed
            result = subprocess.run(["which", "tesseract"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Tesseract OCR not installed. Install with: sudo apt-get install tesseract-ocr")
                
                # Log the error
                self.master_logger.log_error(
                    frame_id, 
                    "ocr_failed", 
                    "Tesseract OCR not installed",
                    "Tesseract OCR not found in PATH"
                )
                
                return "error", None
            
            # Run tesseract OCR
            output_file = f"{self.storage_dir}/payloads/ocr/{frame_id}"
            command = ["tesseract", str(frame_path), output_file]
            subprocess.run(command, check=True)
            
            # Read the output file
            ocr_file = Path(f"{output_file}.txt")
            if ocr_file.exists():
                with open(ocr_file, 'r', encoding='utf-8') as f:
                    ocr_text = f.read()
                logger.info(f"OCR successfully completed for {frame_id}")
                
                # Log the raw OCR data
                self.master_logger.log_raw_ocr(frame_id, ocr_text, str(ocr_file))
                
                return "done", ocr_text
            else:
                logger.error(f"OCR failed for {frame_id}: output file not created")
                
                # Log the error
                self.master_logger.log_error(
                    frame_id, 
                    "ocr_failed", 
                    "Output file not created",
                    f"Tesseract completed but no output file was found at {ocr_file}"
                )
                
                return "error", None
                
        except Exception as e:
            logger.error(f"Error running OCR for {frame_id}: {str(e)}")
            
            # Log the error
            self.master_logger.log_error(
                frame_id, 
                "ocr_exception",
                str(e),
                traceback.format_exc()
            )
            
            return "error", None
    
    def process_ocr_with_gemini(self, frame_id: str, ocr_text: str) -> Optional[Dict[str, Any]]:
        """
        Process OCR text with Gemini to extract structured data.
        
        Args:
            frame_id: The ID of the frame
            ocr_text: The OCR text to process
            
        Returns:
            Dictionary of structured data or None if processing failed
        """
        logger.info(f"Processing OCR data with Gemini for {frame_id}")
        
        if not self.gemini_available:
            logger.warning("Gemini API not available, skipping OCR processing")
            
            # Log the issue
            self.master_logger.log_error(
                frame_id,
                "gemini_unavailable",
                "Gemini API not available",
                "The Gemini API is not available. Install google-generativeai package."
            )
            
            return None
        
        # Check if structured data already exists
        structured_file = Path(f"{self.storage_dir}/payloads/ocr/{frame_id}_structured.json")
        if structured_file.exists():
            logger.info(f"Structured OCR data already exists for {frame_id}")
            try:
                with open(structured_file, 'r', encoding='utf-8') as f:
                    structured_data = json.load(f)
                    
                # Log the parsed data
                self.master_logger.log_parsed_data(
                    frame_id,
                    structured_data,
                    "Loaded from existing file"
                )
                
                return structured_data
            except Exception as e:
                logger.error(f"Error reading existing structured data: {str(e)}")
                
                # Log the error
                self.master_logger.log_error(
                    frame_id,
                    "load_structured_failed",
                    str(e),
                    traceback.format_exc()
                )
        
        # Process with Gemini using API key rotation
        api_key = get_next_gemini_key()
        genai.configure(api_key=api_key)
        
        try:
            # Generate prompt
            prompt = f"""
            Analyze the following OCR text extracted from a screenshot or image.
            Categorize the content, extract structured information, and identify any sensitive information.
            
            OCR TEXT:
            {ocr_text}
            
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
                "paragraphs": ["paragraph1", "paragraph2"],
                "contains_sensitive_info": true|false,
                "sensitive_info_explanation": "Explanation if sensitive info detected",
                "summary": "Brief summary of content",
                "word_count": 123,
                "char_count": 456
            }}
            ```
            
            Pay special attention to API keys, access tokens, and other credentials that may be visible.
            """
            
            # Log the Gemini request
            self.master_logger.log_gemini_request(
                frame_id,
                prompt,
                DEFAULT_MODEL
            )
            
            # Call Gemini (using the Flash model with thinking capability)
            start_time = time.time()
            response = genai.GenerativeModel(DEFAULT_MODEL).generate_content(prompt)
            elapsed_time = time.time() - start_time
            
            # Process the response
            response_text = response.text
            
            # Log the Gemini response
            self.master_logger.log_gemini_response(
                frame_id,
                response_text,
                DEFAULT_MODEL,
                elapsed_time
            )
            
            # Mark the API key as successful
            mark_gemini_key_success(api_key)
            
            # Try to parse JSON from the response
            structured_data = None
            parsing_issues = None
            
            try:
                # Try to find JSON content within the response
                json_content = response_text
                # If the response has markdown code blocks, extract the JSON
                if "```json" in response_text:
                    json_content = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    json_content = response_text.split("```")[1].split("```")[0].strip()
                
                # Parse the JSON content
                structured_data = json.loads(json_content)
                
                # Add raw text to the structured data
                structured_data["raw_text"] = ocr_text
                
                # Save to file
                os.makedirs(structured_file.parent, exist_ok=True)
                with open(structured_file, 'w', encoding='utf-8') as f:
                    json.dump(structured_data, f, indent=2)
                
                logger.info(f"Successfully processed OCR data with Gemini for {frame_id}")
                
                # Log the parsed data
                self.master_logger.log_parsed_data(frame_id, structured_data)
                
                return structured_data
                
            except (json.JSONDecodeError, IndexError) as e:
                logger.warning(f"Could not parse JSON from Gemini response: {e}")
                parsing_issues = f"JSON parsing error: {str(e)}"
                
                # Create a basic structure even if parsing failed
                structured_data = {
                    "raw_text": ocr_text,
                    "content_types": [],
                    "topics": [],
                    "paragraphs": ocr_text.split("\n\n"),
                    "contains_sensitive_info": "api key" in ocr_text.lower() or "password" in ocr_text.lower(),
                    "word_count": len(ocr_text.split()),
                    "char_count": len(ocr_text),
                    "parsing_error": str(e)
                }
                
                # Save to file
                os.makedirs(structured_file.parent, exist_ok=True)
                with open(structured_file, 'w', encoding='utf-8') as f:
                    json.dump(structured_data, f, indent=2)
                
                logger.info(f"Saved basic structured data for {frame_id} after parsing error")
                
                # Log the parsed data with issues
                self.master_logger.log_parsed_data(
                    frame_id, 
                    structured_data,
                    parsing_issues
                )
                
                return structured_data
                
        except Exception as e:
            logger.error(f"Error processing with Gemini for {frame_id}: {str(e)}")
            
            # Log the error
            self.master_logger.log_error(
                frame_id,
                "gemini_exception",
                str(e),
                traceback.format_exc()
            )
            
            # Mark the API key as having an error
            mark_gemini_key_error(api_key)
            return None
    
    def store_in_database(self, frame_id: str, frame_data: Dict[str, Any]) -> str:
        """
        Store frame data in PostgreSQL database.
        
        Args:
            frame_id: The ID of the frame
            frame_data: Complete frame data including OCR
            
        Returns:
            Status string
        """
        logger.info(f"Storing data in database for {frame_id}")
        
        # This would be a real database operation in production
        logger.warning("Not implemented: This would store data in PostgreSQL in production")
        return "simulated"
    
    def create_chunks(self, frame_id: str, frame_path: Path, frame_data: Dict[str, Any]) -> str:
        """
        Create metadata chunks with OCR data.
        
        Args:
            frame_id: The ID of the frame
            frame_path: Path to the frame image file
            frame_data: Complete frame data including OCR
            
        Returns:
            Status string
        """
        logger.info(f"Creating chunks for {frame_id}")
        
        # Create the metadata file
        metadata_file = Path(f"{self.storage_dir}/payloads/json/{frame_id}_metadata.json")
        os.makedirs(metadata_file.parent, exist_ok=True)
        
        # Create a basic metadata structure
        metadata = {
            "FrameID": frame_id,
            "FramePath": str(frame_path),
            "ProcessedAt": datetime.now().isoformat()
        }
        
        # Add any metadata from frame_data
        if "metadata" in frame_data:
            metadata.update(frame_data["metadata"])
        
        # Save the metadata
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Create the OCR file if available
        ocr_file = None
        structured_data = None
        if "structured_data" in frame_data and frame_data["structured_data"]:
            structured_data = frame_data["structured_data"]
            ocr_structured_file = Path(f"{self.storage_dir}/payloads/ocr/{frame_id}_structured.json")
            
            if not ocr_structured_file.exists():
                # Save the structured data
                os.makedirs(ocr_structured_file.parent, exist_ok=True)
                with open(ocr_structured_file, 'w', encoding='utf-8') as f:
                    json.dump(structured_data, f, indent=2)
            
            ocr_file = ocr_structured_file
            
            # Also directly save the OCR chunks to CSV
            try:
                # Create a minimal OCRDataProcessor to use its save_ocr_chunks_to_csv method
                class MinimalOptions:
                    """Minimal options class to pass to OCRDataProcessor"""
                    def __init__(self):
                        self.verbose = False
                        self.input_dir = "."  # Default input directory
                        self.csv_file = "all_frame_embeddings/payloads/csv/frame_chunks.csv"
                        self.display_data = False
                        self.use_gemini = True  # Always use Gemini in this context
                        self.dry_run = True
                        self.batch_size = 10
                        self.update_airtable = False
                        self.flagged_only = False
                        self.gemini_api_key = os.environ.get("GOOGLE_API_KEY", "")  # Get from environment
                
                ocr_processor = OCRDataProcessor(MinimalOptions())
                chunks_csv = Path(f"{self.storage_dir}/payloads/csv/frame_chunks.csv")
                ocr_processor.save_ocr_chunks_to_csv(frame_id, structured_data, str(chunks_csv))
                logger.info(f"Saved OCR chunks directly to CSV for {frame_id}")
            except Exception as e:
                logger.error(f"Error saving OCR chunks directly to CSV: {e}")
                logger.debug(traceback.format_exc())
        
        # Generate command to run the chunking script
        chunk_dir = Path(f"{self.storage_dir}/payloads/chunks/{frame_id}")
        os.makedirs(chunk_dir, exist_ok=True)
        
        cmd = [
            "python", "scripts/chunk_metadata.py",
            "--input-file", str(metadata_file),
            "--output-dir", str(chunk_dir),
            "--frame-id", frame_id,
            "--frame-path", str(frame_path)
        ]
        
        if ocr_file and ocr_file.exists():
            cmd.extend(["--ocr-file", str(ocr_file)])
        
        # Run the chunking process
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Error creating chunks for {frame_id}: {result.stderr}")
                return "error"
            
            logger.info(f"Successfully created chunks for {frame_id}")
            return "done"
            
        except Exception as e:
            logger.error(f"Exception creating chunks for {frame_id}: {str(e)}")
            return "error"
    
    def update_airtable(self, frame_id: str, frame_data: Dict[str, Any]) -> str:
        """
        Update Airtable with processed data.
        
        Args:
            frame_id: The ID of the frame
            frame_data: Complete frame data including OCR and database status
            
        Returns:
            Status string
        """
        logger.info(f"Updating Airtable for {frame_id}")
        
        # This would be a real Airtable update in production
        logger.warning("Not implemented: This would update Airtable in production")
        return "simulated"
    
    def process_frames(self, frame_ids: List[str]) -> Dict[str, Any]:
        """
        Process multiple frames, potentially in parallel.
        
        Args:
            frame_ids: List of frame IDs to process
            
        Returns:
            Summary dictionary
        """
        start_time = time.time()
        logger.info(f"Starting to process {len(frame_ids)} frames")
        
        results = {}
        
        # Process in batches
        for i in range(0, len(frame_ids), self.batch_size):
            batch = frame_ids[i:i+self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(frame_ids)-1)//self.batch_size + 1} with {len(batch)} frames")
            
            # Process batch in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_PROCESSES) as executor:
                future_to_frame = {executor.submit(self.process_single_frame, frame_id): frame_id for frame_id in batch}
                
                for future in concurrent.futures.as_completed(future_to_frame):
                    frame_id = future_to_frame[future]
                    try:
                        success, frame_data = future.result()
                        results[frame_id] = frame_data
                    except Exception as e:
                        logger.error(f"Unhandled exception processing {frame_id}: {str(e)}")
                        traceback.print_exc()
                        results[frame_id] = {"frame_id": frame_id, "status": "error_unhandled", "error": str(e)}
                        self.error_count += 1
            
            # Log progress after each batch
            elapsed = time.time() - start_time
            frames_per_second = (i + len(batch)) / elapsed if elapsed > 0 else float('inf')
            logger.info(f"Processed {i + len(batch)}/{len(frame_ids)} frames "
                       f"({(i + len(batch))/len(frame_ids)*100:.1f}%) - "
                       f"Speed: {frames_per_second:.2f} frames/sec")
        
        # Generate summary
        elapsed = time.time() - start_time
        summary = {
            "total_frames": len(frame_ids),
            "processed_frames": self.processed_count,
            "error_frames": self.error_count,
            "elapsed_time": elapsed,
            "frames_per_second": len(frame_ids) / elapsed if elapsed > 0 else float('inf')
        }
        
        logger.info(f"Processing complete: {summary['processed_frames']} processed, {summary['error_frames']} errors")
        logger.info(f"Total time: {elapsed:.2f} seconds, Speed: {summary['frames_per_second']:.2f} frames/sec")
        
        # Save results
        results_file = Path(f"{self.storage_dir}/logs/results_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json")
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({"summary": summary, "results": results}, f, indent=2)
        
        logger.info(f"Results saved to {results_file}")
        
        return summary

def main():
    parser = argparse.ArgumentParser(description="Process frames through the complete pipeline")
    parser.add_argument("--frame-id", help="Single frame ID to process")
    parser.add_argument("--frame-ids-file", help="File containing frame IDs to process (one per line)")
    parser.add_argument("--storage-dir", default=DEFAULT_STORAGE_DIR, help=f"Storage directory (default: {DEFAULT_STORAGE_DIR})")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help=f"Batch size for processing (default: {DEFAULT_BATCH_SIZE})")
    parser.add_argument("--dry-run", action="store_true", help="Run without making actual Airtable/DB updates")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set log level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get frames to process
    frame_ids = []
    if args.frame_id:
        frame_ids.append(args.frame_id)
    elif args.frame_ids_file:
        try:
            with open(args.frame_ids_file, 'r') as f:
                frame_ids = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logger.error(f"Error reading frame IDs file: {str(e)}")
            return 1
    else:
        # For testing, use some mock frame IDs
        frame_ids = [f"test_frame_{i}" for i in range(1, 4)]
        logger.info(f"No frame IDs specified, using test frames: {frame_ids}")
    
    # Initialize processor
    processor = FrameProcessor(args)
    
    # Process frames
    processor.process_frames(frame_ids)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 