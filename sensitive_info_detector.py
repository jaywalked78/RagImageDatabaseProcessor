#!/usr/bin/env python3
"""
Sensitive information detection module for OCR-processed frame data.
Detects API keys, passwords in plain text, and payment card information.
To be integrated with LLM processing workflow.
"""

import re
import logging
import json
from typing import Dict, List, Tuple, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sensitive_detector")

# Regular expressions for sensitive information detection
# API key pattern: Alphanumeric string of 20+ chars, often with dashes or underscores
API_KEY_PATTERN = r'[A-Za-z0-9_\-]{20,}'

# Password patterns for various formats
PASSWORD_PATTERNS = [
    # Common password field patterns in .env files and configs
    r'(?i)(password|passwd|pwd|secret)[=:]\s*[^\s]+'
]

# Credit/debit card patterns
CARD_PATTERNS = [
    # 16-digit card numbers, with or without spaces/dashes
    r'(?<!\d)(?:\d{4}[\s\-]?){3}\d{4}(?!\d)'
]

# Environment variable patterns for sensitive data
ENV_PATTERNS = [
    r'(?i)(API_KEY|SECRET|TOKEN|AUTH|PASSWORD|CREDENTIAL)[=:]\s*[^\s]+',
    r'(?i)(DATABASE_URL|MONGODB_URI|POSTGRES_CONNECTION)[=:]\s*[^\s]+'
]

def detect_api_keys(text: str) -> List[str]:
    """
    Detect potential API keys in text.
    
    Args:
        text: The OCR-processed text to analyze
        
    Returns:
        List of detected API keys
    """
    if not text:
        return []
    
    # Find all matches
    matches = re.finditer(API_KEY_PATTERN, text)
    
    # Filter out common false positives (dates, UUIDs, etc.)
    filtered_matches = []
    for match in matches:
        key = match.group(0)
        # Skip if it's a UUID format (has exactly 4 hyphens in specific positions)
        if re.match(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', key.lower()):
            continue
        # Skip if it's just a long number without letters
        if re.match(r'^\d+$', key):
            continue
        # Skip if it's a very common word
        if key.lower() in ["implementation", "internationalization", "authentication"]:
            continue
        
        filtered_matches.append(key)
    
    return filtered_matches

def detect_passwords(text: str) -> List[Tuple[str, str]]:
    """
    Detect passwords in plain text.
    
    Args:
        text: The OCR-processed text to analyze
        
    Returns:
        List of tuples (pattern description, matched text)
    """
    if not text:
        return []
    
    results = []
    for pattern in PASSWORD_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            matched_text = match.group(0)
            results.append(("Password field", matched_text))
    
    return results

def detect_card_numbers(text: str) -> List[str]:
    """
    Detect credit/debit card numbers in text.
    Uses Luhn algorithm for validation to reduce false positives.
    
    Args:
        text: The OCR-processed text to analyze
        
    Returns:
        List of potential card numbers detected
    """
    if not text:
        return []
    
    results = []
    for pattern in CARD_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            card_num = re.sub(r'[\s\-]', '', match.group(0))
            # Only include if it passes Luhn validation
            if validate_card_number(card_num):
                # Mask all but last 4 digits for security
                masked = "*" * (len(card_num) - 4) + card_num[-4:]
                results.append(masked)
    
    return results

def detect_env_variables(text: str) -> List[Tuple[str, str]]:
    """
    Detect sensitive environment variables.
    
    Args:
        text: The OCR-processed text to analyze
        
    Returns:
        List of tuples (variable type, matched text)
    """
    if not text:
        return []
    
    results = []
    for pattern in ENV_PATTERNS:
        matches = re.finditer(pattern, text)
        for match in matches:
            matched_text = match.group(0)
            
            # Categorize the match
            if re.search(r'(?i)API_KEY|SECRET|TOKEN', matched_text):
                var_type = "API/Secret Key"
            elif re.search(r'(?i)DATABASE|MONGO|POSTGRES|SQL', matched_text):
                var_type = "Database Credential"
            elif re.search(r'(?i)PASSWORD|AUTH|CREDENTIAL', matched_text):
                var_type = "Password/Auth"
            else:
                var_type = "Sensitive Variable"
                
            results.append((var_type, matched_text))
    
    return results

def validate_card_number(card_number: str) -> bool:
    """
    Validate a card number using the Luhn algorithm.
    
    Args:
        card_number: Card number string (digits only)
        
    Returns:
        True if the card number passes Luhn validation
    """
    if not card_number or not card_number.isdigit():
        return False
    
    # Common card number lengths
    if len(card_number) not in [13, 15, 16, 19]:
        return False
    
    # Luhn algorithm implementation
    digits = [int(d) for d in card_number]
    checksum = 0
    is_odd_position = True
    
    for i in range(len(digits) - 1, -1, -1):
        digit = digits[i]
        if not is_odd_position:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit
        is_odd_position = not is_odd_position
    
    return checksum % 10 == 0

def scan_ocr_data(ocr_text: str) -> Dict[str, Any]:
    """
    Scan OCR data for all types of sensitive information.
    
    Args:
        ocr_text: The OCR-processed text to analyze
        
    Returns:
        Dictionary with detection results
    """
    results = {
        "contains_sensitive_info": False,
        "api_keys": [],
        "passwords": [],
        "card_numbers": [],
        "env_variables": [],
        "total_detected": 0
    }
    
    # Skip processing if text is empty
    if not ocr_text:
        return results
    
    # Detect API keys
    api_keys = detect_api_keys(ocr_text)
    if api_keys:
        results["api_keys"] = api_keys
    
    # Detect passwords
    passwords = detect_passwords(ocr_text)
    if passwords:
        results["passwords"] = passwords
    
    # Detect card numbers
    card_numbers = detect_card_numbers(ocr_text)
    if card_numbers:
        results["card_numbers"] = card_numbers
    
    # Detect environment variables
    env_vars = detect_env_variables(ocr_text)
    if env_vars:
        results["env_variables"] = env_vars
    
    # Update total count and flag
    total_detected = (
        len(api_keys) + 
        len(passwords) + 
        len(card_numbers) + 
        len(env_vars)
    )
    
    results["total_detected"] = total_detected
    results["contains_sensitive_info"] = total_detected > 0
    
    return results

def generate_llm_metadata(scan_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate metadata for LLM processing based on sensitive information scan.
    
    Args:
        scan_results: Results from scan_ocr_data function
        
    Returns:
        Dictionary with metadata for LLM processing
    """
    metadata = {
        "has_sensitive_information": scan_results["contains_sensitive_info"],
        "sensitive_info_summary": {}
    }
    
    if scan_results["contains_sensitive_info"]:
        summary = {
            "types_detected": [],
            "alert_level": "low"
        }
        
        # Build list of detected types
        if scan_results["api_keys"]:
            summary["types_detected"].append("api_keys")
        if scan_results["passwords"]:
            summary["types_detected"].append("passwords")
        if scan_results["card_numbers"]:
            summary["types_detected"].append("payment_card_data")
            # Elevate risk level for payment data
            summary["alert_level"] = "high"
        if scan_results["env_variables"]:
            summary["types_detected"].append("environment_variables")
        
        # Set alert level based on count and types
        if summary["alert_level"] != "high":
            if scan_results["total_detected"] > 3:
                summary["alert_level"] = "medium"
            if "passwords" in summary["types_detected"]:
                summary["alert_level"] = "medium"
        
        metadata["sensitive_info_summary"] = summary
    
    return metadata

def clean_sensitive_data(ocr_text: str, scan_results: Dict[str, Any]) -> str:
    """
    Create a sanitized version of OCR text with sensitive data redacted.
    
    Args:
        ocr_text: Original OCR text
        scan_results: Results from scan_ocr_data function
        
    Returns:
        Sanitized text with sensitive information redacted
    """
    if not scan_results["contains_sensitive_info"]:
        return ocr_text
    
    sanitized_text = ocr_text
    
    # Redact API keys
    for key in scan_results["api_keys"]:
        sanitized_text = sanitized_text.replace(key, "[REDACTED API KEY]")
    
    # Redact passwords
    for pwd_type, pwd_text in scan_results["passwords"]:
        # Extract the variable name and value
        match = re.match(r'(.+?)[=:]\s*(.+)', pwd_text)
        if match:
            var_name, var_value = match.groups()
            # Replace just the value part
            replacement = f"{var_name}=[REDACTED PASSWORD]"
            sanitized_text = sanitized_text.replace(pwd_text, replacement)
    
    # Redact card numbers
    for card_num in scan_results["card_numbers"]:
        # Find the original card number in the text
        unmasked = re.search(r'(?<!\d)(?:\d{4}[\s\-]?){3}\d{4}(?!\d)', sanitized_text)
        if unmasked:
            sanitized_text = sanitized_text.replace(unmasked.group(0), "[REDACTED CARD NUMBER]")
    
    # Redact env variables
    for var_type, var_text in scan_results["env_variables"]:
        # Extract the variable name and value
        match = re.match(r'(.+?)[=:]\s*(.+)', var_text)
        if match:
            var_name, var_value = match.groups()
            # Replace just the value part
            replacement = f"{var_name}=[REDACTED {var_type}]"
            sanitized_text = sanitized_text.replace(var_text, replacement)
    
    return sanitized_text

def process_frame_for_llm(frame_id: str, ocr_text: str) -> Dict[str, Any]:
    """
    Process a frame's OCR text for LLM processing.
    Scans for sensitive information, generates metadata, and creates a sanitized version.
    
    Args:
        frame_id: The ID of the frame being processed
        ocr_text: The OCR-processed text from the frame
        
    Returns:
        Dictionary with processing results
    """
    logger.info(f"Processing frame {frame_id} for sensitive information")
    
    # Scan for sensitive information
    scan_results = scan_ocr_data(ocr_text)
    
    # Generate metadata for LLM
    llm_metadata = generate_llm_metadata(scan_results)
    
    # Create sanitized version
    sanitized_text = clean_sensitive_data(ocr_text, scan_results)
    
    # Compile results
    result = {
        "frame_id": frame_id,
        "original_length": len(ocr_text) if ocr_text else 0,
        "contains_sensitive_info": scan_results["contains_sensitive_info"],
        "sanitized_text": sanitized_text,
        "llm_metadata": llm_metadata,
        "sensitive_info_count": scan_results["total_detected"],
        "sensitive_info_details": {
            "api_keys": len(scan_results["api_keys"]),
            "passwords": len(scan_results["passwords"]),
            "card_numbers": len(scan_results["card_numbers"]),
            "env_variables": len(scan_results["env_variables"])
        }
    }
    
    logger.info(f"Sensitive information scan complete for frame {frame_id}: " +
              f"Found {scan_results['total_detected']} sensitive items")
    
    return result

# Example usage
if __name__ == "__main__":
    # Test with some example OCR data
    test_data = [
        """
        # .env file
        DATABASE_URL=postgresql://user:password123@localhost:5432/mydatabase
        API_KEY=ak_1a2b3c4d5e6f7g8h9i0j
        SECRET_TOKEN=st_9384fdjsk37461
        AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
        STRIPE_SECRET_KEY=sk_test_4eC39HqLyjWDarjtT1zdp7dc
        """,
        
        """
        Payment processed successfully!
        Card: 4111 1111 1111 1111
        Expiry: 12/25
        Name: John Doe
        """,
        
        """
        DEBUG=True
        LOG_LEVEL=info
        PORT=8080
        """
    ]
    
    for i, text in enumerate(test_data):
        print(f"\n--- Example {i+1} ---")
        result = process_frame_for_llm(f"test_frame_{i+1}", text)
        print(f"Contains sensitive info: {result['contains_sensitive_info']}")
        print(f"Sensitive info count: {result['sensitive_info_count']}")
        print(f"Alert level: {result['llm_metadata']['sensitive_info_summary'].get('alert_level', 'none')}")
        print("Sanitized text:")
        print(result['sanitized_text']) 