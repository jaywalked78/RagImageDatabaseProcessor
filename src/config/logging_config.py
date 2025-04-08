"""
Logging configuration for the application.
"""

import os
import logging
import logging.handlers
from pathlib import Path

def configure_logging(log_level=None, log_file=None):
    """
    Configure logging for the application.
    
    Args:
        log_level: Log level (optional, defaults to INFO or from environment variable)
        log_file: Log file path (optional, defaults to logs/app.log)
        
    Returns:
        Configured logger
    """
    # Get log level from environment or parameter with fallback to INFO
    level = log_level or os.environ.get('LOG_LEVEL', 'INFO').upper()
    level_dict = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    log_level = level_dict.get(level, logging.INFO)
    
    # Get log file path with default
    if not log_file:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        log_file = str(log_dir / 'app.log')
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # Create file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Create a logger specific to this application
    app_logger = logging.getLogger('logicLoom')
    app_logger.info(f"Logging configured with level {level} to {log_file}")
    
    return app_logger 