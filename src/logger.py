"""
Logger configuration for the scraper.
"""
import os
import sys
from datetime import datetime

from loguru import logger

def setup_logger():
    """
    Set up the logger.
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    
    # Log file path with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"scraper_{timestamp}.log")
    
    # Configure logger
    logger.remove()  # Remove default handler
    
    # Add console handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
    )
    
    # Add file handler
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",  # Rotate when file reaches 10 MB
        retention="1 week",  # Keep logs for 1 week
    )
    
    logger.info(f"Logger initialized. Log file: {log_file}")
    
    return logger