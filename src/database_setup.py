"""
Script to set up the database locally for development.
"""
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from loguru import logger
from src.logger import setup_logger
from src.database import init_db

if __name__ == "__main__":
    # Set up logger
    setup_logger()
    
    logger.info("Setting up database for local development")
    
    try:
        # Initialize database
        init_db()
        logger.info("Database setup completed successfully")
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        sys.exit(1)