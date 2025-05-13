"""
Main entrypoint for The Dyrt web scraper case study.

Usage:
    The scraper can be run directly (`python main.py`) or via Docker Compose (`docker compose up`).

If you have any questions in mind you can connect to me directly via info@smart-maple.com
"""
import argparse
import os
import sys
import time
import uvicorn

from loguru import logger

from src.api import app
from src.database import init_db
from src.logger import setup_logger
from src.scheduler import ScraperScheduler
from src.scraper import DyrtScraper

def run_scraper():
    """
    Run the scraper once.
    """
    logger.info("Running scraper")
    scraper = DyrtScraper()
    scraper.run()
    logger.info("Scraper completed")

def run_scheduler(interval=24):
    """
    Run the scheduler with the specified interval.
    
    Args:
        interval: Interval in hours
    """
    logger.info(f"Starting scheduler with {interval} hour interval")
    scheduler = ScraperScheduler()
    scheduler.schedule_interval(hours=interval)
    scheduler.run_forever()

def run_api(host="0.0.0.0", port=8000):
    """
    Run the API server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    # Set up logger
    setup_logger()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="The Dyrt campground scraper")
    parser.add_argument("--scrape", action="store_true", help="Run the scraper once")
    parser.add_argument("--schedule", type=float, default=0, help="Run the scheduler with the specified interval in hours")
    parser.add_argument("--api", action="store_true", help="Run the API server")
    parser.add_argument("--port", type=int, default=8000, help="Port for the API server")
    
    args = parser.parse_args()
    
    try:
        # Initialize database
        init_db()
        
        # Run the requested mode
        if args.scrape:
            run_scraper()
        elif args.schedule > 0:
            run_scheduler(interval=args.schedule)
        elif args.api:
            run_api(port=args.port)
        else:
            # Default: run the scraper once
            logger.info("No mode specified, running scraper once")
            run_scraper()
            
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
