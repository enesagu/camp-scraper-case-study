"""
Database connection and ORM models for the scraper.
"""
import os
from datetime import datetime
from typing import List, Optional

from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import Column, DateTime, Float, String, Boolean, Integer, create_engine, Table, MetaData
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Get database URL from environment variables
# When running locally (not in Docker), use LOCAL_DB_URL
# When running in Docker, use DB_URL
if os.environ.get("DOCKER_ENV") == "true":
    DB_URL = os.getenv("DB_URL")
else:
    DB_URL = os.getenv("LOCAL_DB_URL")

if not DB_URL:
    raise ValueError("Database URL not found in environment variables")

logger.info(f"Using database URL: {DB_URL}")

# Create SQLAlchemy engine
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for ORM models
Base = declarative_base()

class CampgroundORM(Base):
    """
    SQLAlchemy ORM model for campgrounds.
    """
    __tablename__ = "campgrounds"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    links_self = Column(String, nullable=False)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    region_name = Column(String, nullable=False)
    administrative_area = Column(String, nullable=True)
    nearest_city_name = Column(String, nullable=True)
    accommodation_type_names = Column(ARRAY(String), nullable=True)
    bookable = Column(Boolean, default=False)
    camper_types = Column(ARRAY(String), nullable=True)
    operator = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    photo_urls = Column(ARRAY(String), nullable=True)
    photos_count = Column(Integer, default=0)
    rating = Column(Float, nullable=True)
    reviews_count = Column(Integer, default=0)
    slug = Column(String, nullable=True)
    price_low = Column(Float, nullable=True)
    price_high = Column(Float, nullable=True)
    availability_updated_at = Column(DateTime, nullable=True)
    address = Column(String, nullable=True)  # Bonus field
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db():
    """
    Initialize the database by creating all tables.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def get_db():
    """
    Get a database session.
    """
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"Error getting database session: {e}")
        db.close()
        raise