"""
API module for controlling the scraper.
This is a bonus feature.
"""
import asyncio
from datetime import datetime
from typing import Dict, List

from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import CampgroundORM, get_db
from src.scraper import DyrtScraper

# Create FastAPI app
app = FastAPI(
    title="The Dyrt Scraper API",
    description="API for controlling The Dyrt campground scraper",
    version="1.0.0",
)

class ScraperStatus(BaseModel):
    """
    Model for scraper status response.
    """
    status: str
    last_run: str = None
    message: str = None

class CampgroundResponse(BaseModel):
    """
    Model for campground response.
    """
    id: str
    name: str
    latitude: float
    longitude: float
    region_name: str
    rating: float = None
    reviews_count: int = 0
    address: str = None

# Store the last run time
last_run_time = None

# Create scraper instance
scraper = DyrtScraper()

async def run_scraper_async():
    """
    Run the scraper asynchronously.
    """
    global last_run_time
    
    loop = asyncio.get_event_loop()
    try:
        # Run the scraper in a thread pool
        await loop.run_in_executor(None, scraper.run)
        last_run_time = datetime.now().isoformat()
        logger.info(f"Scraper completed at {last_run_time}")
    except Exception as e:
        logger.error(f"Error running scraper: {e}")
        raise

@app.get("/", response_model=Dict[str, str])
async def root():
    """
    Root endpoint.
    """
    return {"message": "Welcome to The Dyrt Scraper API"}

@app.post("/scrape", response_model=ScraperStatus)
async def start_scraper(background_tasks: BackgroundTasks):
    """
    Start the scraper in the background.
    """
    try:
        background_tasks.add_task(run_scraper_async)
        return {
            "status": "started",
            "message": "Scraper started in the background",
        }
    except Exception as e:
        logger.error(f"Error starting scraper: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status", response_model=ScraperStatus)
async def get_status():
    """
    Get the status of the scraper.
    """
    return {
        "status": "idle",
        "last_run": last_run_time,
        "message": "Scraper is idle",
    }

@app.get("/campgrounds", response_model=List[CampgroundResponse])
async def get_campgrounds(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Get campgrounds from the database.
    """
    try:
        campgrounds = db.query(CampgroundORM).offset(offset).limit(limit).all()
        
        return [
            {
                "id": c.id,
                "name": c.name,
                "latitude": c.latitude,
                "longitude": c.longitude,
                "region_name": c.region_name,
                "rating": c.rating,
                "reviews_count": c.reviews_count,
                "address": c.address,
            }
            for c in campgrounds
        ]
    except Exception as e:
        logger.error(f"Error getting campgrounds: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campgrounds/{campground_id}", response_model=Dict)
async def get_campground(
    campground_id: str,
    db: Session = Depends(get_db),
):
    """
    Get a specific campground from the database.
    """
    try:
        campground = db.query(CampgroundORM).filter(CampgroundORM.id == campground_id).first()
        
        if not campground:
            raise HTTPException(status_code=404, detail="Campground not found")
        
        # Convert to dictionary
        campground_dict = {
            column.name: getattr(campground, column.name)
            for column in campground.__table__.columns
        }
        
        # Convert datetime objects to strings
        for key, value in campground_dict.items():
            if isinstance(value, datetime):
                campground_dict[key] = value.isoformat()
        
        return campground_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campground {campground_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))