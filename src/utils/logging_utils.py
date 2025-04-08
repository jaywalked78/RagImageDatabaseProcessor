"""
Logging configuration for TheLogicLoom Vector Search API.
This allows for fine-grained control over how logs are formatted and where they're sent.
"""

import os
import logging.config
from logging import LogRecord
import time
import sys
from typing import Dict, Any

# Get log level from environment variable, default to INFO
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Define custom formatter with colors for console output
class ColoredFormatter(logging.Formatter):
    """Logging colored formatter that adds colors to logs based on level."""
    
    # ANSI escape sequences for colors
    COLORS = {
        'DEBUG': '\033[94m',      # Blue
        'INFO': '\033[92m',       # Green
        'WARNING': '\033[93m',    # Yellow
        'ERROR': '\033[91m',      # Red
        'CRITICAL': '\033[91m\033[1m',  # Bold Red
        'RESET': '\033[0m',       # Reset
    }
    
    def format(self, record: LogRecord) -> str:
        """Format the log record with colors."""
        # Create a copy of the record to avoid modifying the original
        record_copy = logging.makeLogRecord(record.__dict__)
        
        # Add color to the level name if terminal supports colors
        if hasattr(self, 'COLORS') and record_copy.levelname in self.COLORS:
            level_color = self.COLORS[record_copy.levelname]
            reset = self.COLORS['RESET']
            
            # Apply color to level name and message separately
            record_copy.levelname = f"{level_color}{record_copy.levelname}{reset}"
            record_copy.msg = f"{level_color}{record_copy.msg}{reset}"
            
        # Format the record with the parent formatter
        return super().format(record_copy)

# Define logging configuration
LOGGING_CONFIG: Dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'colored': {
            '()': ColoredFormatter,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': LOG_LEVEL,
            'formatter': 'colored' if sys.stdout.isatty() else 'standard',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': LOG_LEVEL,
            'formatter': 'detailed',
            'filename': 'output/logs/logicLoom.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8',
        },
        'errors_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'output/logs/logicLoom_errors.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8',
        },
    },
    'loggers': {
        'logicLoom': {
            'level': LOG_LEVEL,
            'handlers': ['console', 'file', 'errors_file'],
            'propagate': False,
        },
        'uvicorn': {
            'level': LOG_LEVEL,
            'handlers': ['console', 'file'],
            'propagate': False,
        },
        'uvicorn.access': {
            'level': LOG_LEVEL,
            'handlers': ['console', 'file'],
            'propagate': False,
        },
    },
    'root': {
        'level': LOG_LEVEL,
        'handlers': ['console', 'file', 'errors_file'],
    },
}

def configure_logging():
    """Configure logging based on the predefined configuration."""
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger("logicLoom")
    logger.info(f"Logging initialized with level: {LOG_LEVEL}")
    return logger 