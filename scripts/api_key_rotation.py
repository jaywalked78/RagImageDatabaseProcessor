#!/usr/bin/env python3
"""
API Key Rotation Module

This module provides tools for rotating between multiple API keys to handle
rate limits better and distribute load across multiple keys.

Features:
- Key rotation for Google Gemini, OpenAI, and other APIs
- Rate limit tracking and cooldown periods
- Error tracking for each key
- Automatic fallback to working keys

Usage:
    from api_key_rotation import GeminiKeyRotator
    
    # Initialize with a list of API keys
    rotator = GeminiKeyRotator(['key1', 'key2', 'key3'])
    
    # Get the next available key
    api_key = rotator.get_next_key()
    
    # Mark success or failure
    rotator.mark_success(api_key)
    rotator.mark_error(api_key, error_type="rate_limit")
"""

import os
import time
import random
import logging
from typing import List, Dict, Optional, Any
from threading import Lock

# Configure logging
logger = logging.getLogger(__name__)

class ApiKeyRotator:
    """
    Base class for API key rotation strategies.
    Handles rotation between multiple API keys, tracking
    errors and rate limits.
    """
    
    def __init__(self, api_keys: List[str]):
        """
        Initialize the API key rotator.
        
        Args:
            api_keys: List of API keys to rotate between
        """
        self.api_keys = api_keys
        self.key_index = 0
        self.key_stats = {}
        self.lock = Lock()
        
        # Initialize stats for each key
        for key in self.api_keys:
            self.key_stats[key] = {
                'use_count': 0,
                'error_count': 0,
                'last_used': 0,
                'cooldown_until': 0,
                'is_valid': True
            }
        
        logger.info(f"Initialized ApiKeyRotator with {len(api_keys)} keys")
    
    def get_next_key(self) -> Optional[str]:
        """
        Get the next available API key, respecting cooldown periods.
        
        Returns:
            An API key string or None if no keys are available
        """
        with self.lock:
            now = time.time()
            
            # First pass: try to find a key that's not in cooldown
            for _ in range(len(self.api_keys)):
                self.key_index = (self.key_index + 1) % len(self.api_keys)
                key = self.api_keys[self.key_index]
                stats = self.key_stats[key]
                
                # Skip invalid keys
                if not stats['is_valid']:
                    continue
                
                # Check if key is in cooldown
                if stats['cooldown_until'] <= now:
                    stats['last_used'] = now
                    stats['use_count'] += 1
                    return key
            
            # Second pass: find the key with the shortest cooldown
            min_cooldown = float('inf')
            best_key = None
            
            for key in self.api_keys:
                stats = self.key_stats[key]
                if not stats['is_valid']:
                    continue
                
                cooldown = stats['cooldown_until'] - now
                if cooldown < min_cooldown:
                    min_cooldown = cooldown
                    best_key = key
            
            if best_key:
                logger.info(f"All keys in cooldown. Using key with shortest wait time ({min_cooldown:.2f}s)")
                time.sleep(min_cooldown + 0.1)  # Wait for cooldown plus a small buffer
                
                # Update stats for the key
                self.key_stats[best_key]['last_used'] = time.time()
                self.key_stats[best_key]['use_count'] += 1
                return best_key
            
            logger.error("No valid API keys available")
            return None
    
    def mark_success(self, api_key: str) -> None:
        """
        Mark a successful API call with the given key.
        
        Args:
            api_key: The API key used for the successful call
        """
        with self.lock:
            if api_key in self.key_stats:
                self.key_stats[api_key]['last_success'] = time.time()
    
    def mark_error(self, api_key: str, error_type: str = "unknown") -> None:
        """
        Mark an error for the given API key.
        
        Args:
            api_key: The API key that encountered an error
            error_type: Type of error encountered (e.g., "rate_limit", "auth", "server")
        """
        with self.lock:
            if api_key not in self.key_stats:
                return
            
            stats = self.key_stats[api_key]
            stats['error_count'] += 1
            
            # Handle different error types
            if error_type == "rate_limit":
                cooldown = self._get_rate_limit_cooldown()
                stats['cooldown_until'] = time.time() + cooldown
                logger.warning(f"API key rate limited. Cooling down for {cooldown}s")
            elif error_type == "auth":
                # Authentication errors mean the key is invalid
                stats['is_valid'] = False
                logger.error(f"API key authentication failed. Marking as invalid.")
            elif error_type == "server":
                # Server errors get a short cooldown
                stats['cooldown_until'] = time.time() + 5
                logger.warning(f"Server error encountered. Short cooldown applied.")
            else:
                # Unknown errors get a moderate cooldown
                stats['cooldown_until'] = time.time() + 10
                logger.warning(f"Unknown error type: {error_type}. Moderate cooldown applied.")
    
    def _get_rate_limit_cooldown(self) -> float:
        """
        Calculate cooldown period for rate-limited keys.
        Override in subclasses for API-specific behavior.
        
        Returns:
            Cooldown period in seconds
        """
        return 60  # Default 1 minute cooldown
    
    def get_key_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for all keys.
        
        Returns:
            Dictionary of key stats
        """
        with self.lock:
            # Create a copy to avoid threading issues
            return {k: v.copy() for k, v in self.key_stats.items()}


class GeminiKeyRotator(ApiKeyRotator):
    """
    API key rotator specific to Google's Gemini API.
    Implements Gemini-specific rate limit handling.
    """
    
    def __init__(self, api_keys: List[str]):
        """
        Initialize the Gemini API key rotator.
        
        Args:
            api_keys: List of Gemini API keys
        """
        super().__init__(api_keys)
        
        # Gemini-specific settings
        self.rate_limit = int(os.environ.get("GEMINI_RATE_LIMIT", "60"))  # Requests per minute
        self.cooldown_period = int(os.environ.get("GEMINI_COOLDOWN_PERIOD", "60"))  # Seconds
        
        logger.info(f"Initialized GeminiKeyRotator with rate limit of {self.rate_limit} RPM")
    
    def _get_rate_limit_cooldown(self) -> float:
        """
        Calculate cooldown period for rate-limited Gemini API keys.
        
        Returns:
            Cooldown period in seconds
        """
        # Use the configured cooldown period with a small random factor
        return self.cooldown_period + random.uniform(0, 5)


# Global functions for backwards compatibility and simple usage
_gemini_rotator = None
_gemini_rotator_lock = Lock()

def initialize_gemini_key_rotation(api_keys: List[str]) -> None:
    """
    Initialize the global Gemini key rotator.
    
    Args:
        api_keys: List of Gemini API keys
    """
    global _gemini_rotator
    with _gemini_rotator_lock:
        _gemini_rotator = GeminiKeyRotator(api_keys)

def get_next_gemini_key() -> Optional[str]:
    """
    Get the next available Gemini API key.
    
    Returns:
        A Gemini API key or None if no keys are available
    """
    global _gemini_rotator
    
    # Initialize with environment variables if not already initialized
    if _gemini_rotator is None:
        with _gemini_rotator_lock:
            if _gemini_rotator is None:
                # Try to get keys from environment
                gemini_keys = []
                
                # First check for numbered keys
                for i in range(1, 6):
                    key_name = f"GEMINI_API_KEY_{i}"
                    if key_name in os.environ and os.environ[key_name]:
                        gemini_keys.append(os.environ[key_name])
                
                # If no numbered keys, try the generic key
                if not gemini_keys and "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"]:
                    gemini_keys.append(os.environ["GEMINI_API_KEY"])
                
                # If still no keys, try GOOGLE_API_KEY as fallback
                if not gemini_keys and "GOOGLE_API_KEY" in os.environ and os.environ["GOOGLE_API_KEY"]:
                    gemini_keys.append(os.environ["GOOGLE_API_KEY"])
                
                if gemini_keys:
                    _gemini_rotator = GeminiKeyRotator(gemini_keys)
                    logger.info(f"Auto-initialized GeminiKeyRotator with {len(gemini_keys)} keys")
                else:
                    logger.warning("No Gemini API keys available in environment variables")
                    return None
    
    return _gemini_rotator.get_next_key()

def mark_gemini_key_success(api_key: str) -> None:
    """
    Mark a successful API call for a Gemini key.
    
    Args:
        api_key: The Gemini API key used for the successful call
    """
    if _gemini_rotator:
        _gemini_rotator.mark_success(api_key)

def mark_gemini_key_error(api_key: str, error_type: str = "unknown") -> None:
    """
    Mark an error for a Gemini API key.
    
    Args:
        api_key: The Gemini API key that encountered an error
        error_type: Type of error encountered
    """
    if _gemini_rotator:
        _gemini_rotator.mark_error(api_key, error_type)

def get_gemini_key_stats() -> Dict[str, Dict[str, Any]]:
    """
    Get statistics for all Gemini API keys.
    
    Returns:
        Dictionary of key stats or empty dict if not initialized
    """
    if _gemini_rotator:
        return _gemini_rotator.get_key_stats()
    return {}

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize with the default keys
    rotator = GeminiKeyRotator()
    
    # Simulate API calls
    for i in range(20):
        key = rotator.get_next_key()
        print(f"Using API key: ...{key[-4:]}")
        
        # Simulate some errors
        if i % 7 == 0:
            print(f"Simulating error with key ...{key[-4:]}")
            rotator.mark_error(key)
        else:
            rotator.mark_success(key)
        
        time.sleep(0.1)  # Simulate some work 