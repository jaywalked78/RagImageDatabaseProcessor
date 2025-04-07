#!/usr/bin/env python
"""
Start the TheLogicLoomDB application.
"""

import asyncio
import os
import sys
import argparse

# Add the parent directory to the path to allow imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Import the application
from src.main import run, app, verify_config, debug_config, logger

# Define command-line arguments
parser = argparse.ArgumentParser(description='Start the TheLogicLoomDB application.')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
parser.add_argument('--verify-config', action='store_true', help='Verify configuration and exit')
parser.add_argument('--show-config', action='store_true', help='Show configuration and exit')
parser.add_argument('--init-db', action='store_true', help='Initialize database and exit')

# Parse arguments
args = parser.parse_args()

# Handle --verify-config
if args.verify_config:
    logger.info("Verifying configuration...")
    config_status = verify_config()
    print("Configuration status:")
    for component, is_valid in config_status.items():
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"  {component}: {status}")
    
    if all(config_status.values()):
        print("All configuration components are valid.")
        sys.exit(0)
    else:
        print("Some configuration components are invalid. Please check your .env file.")
        sys.exit(1)

# Handle --show-config
if args.show_config:
    logger.info("Showing configuration...")
    config = debug_config()
    print("Configuration:")
    import json
    print(json.dumps(config, indent=2))
    sys.exit(0)

# Handle --init-db
if args.init_db:
    from src.db.connection import init_db
    logger.info("Initializing database...")
    success = init_db()
    if success:
        print("Database initialized successfully.")
        sys.exit(0)
    else:
        print("Database initialization failed. Check logs for details.")
        sys.exit(1)

# Set debug mode
if args.debug:
    from src.config.logging_config import configure_logging
    logger = configure_logging(level="DEBUG")
    logger.info("Debug mode enabled")

# Run the application
if __name__ == "__main__":
    logger.info("Starting TheLogicLoomDB application")
    asyncio.run(run()) 