"""
Scheduler module for running the scraper at regular intervals.
"""
import time
from datetime import datetime

import schedule
from loguru import logger

from src.scraper import DyrtScraper

class ScraperScheduler:
    """
    Scheduler for running the scraper at regular intervals.
    """
    def __init__(self):
        self.scraper = DyrtScraper()
    
    def run_scraper(self):
        """
        Run the scraper.
        """
        logger.info(f"Running scheduled scraper job at {datetime.now()}")
        try:
            self.scraper.run()
            logger.info("Scheduled scraper job completed successfully")
        except Exception as e:
            logger.error(f"Error in scheduled scraper job: {e}")
    
    def schedule_daily(self, hour=2, minute=0):
        """
        Schedule the scraper to run daily at the specified time.
        
        Args:
            hour: Hour of the day (0-23)
            minute: Minute of the hour (0-59)
        """
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(self.run_scraper)
        logger.info(f"Scheduled scraper to run daily at {hour:02d}:{minute:02d}")
    
    def schedule_weekly(self, day_of_week=0, hour=2, minute=0):
        """
        Schedule the scraper to run weekly on the specified day and time.
        
        Args:
            day_of_week: Day of the week (0-6, where 0 is Monday)
            hour: Hour of the day (0-23)
            minute: Minute of the hour (0-59)
        """
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day = days[day_of_week]
        
        getattr(schedule.every(), day).at(f"{hour:02d}:{minute:02d}").do(self.run_scraper)
        logger.info(f"Scheduled scraper to run every {day.capitalize()} at {hour:02d}:{minute:02d}")
    
    def schedule_interval(self, hours=24):
        """
        Schedule the scraper to run at a regular interval.
        
        Args:
            hours: Interval in hours
        """
        schedule.every(hours).hours.do(self.run_scraper)
        logger.info(f"Scheduled scraper to run every {hours} hours")
    
    def run_forever(self):
        """
        Run the scheduler indefinitely.
        """
        logger.info("Starting scheduler")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying