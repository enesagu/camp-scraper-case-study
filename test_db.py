"""
Database test script for The Dyrt scraper.
"""
import argparse
import os
import sys
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def test_database_connection(db_url=None):
    """
    Test the database connection and query campgrounds.
    
    Args:
        db_url: Database URL
    """
    # Load environment variables if no DB URL provided
    if not db_url:
        load_dotenv()
        db_url = os.getenv("LOCAL_DB_URL") or os.getenv("DB_URL")
    
    if not db_url:
        print("Error: Database URL not found")
        sys.exit(1)
    
    print(f"Testing database connection to: {db_url}")
    
    try:
        # Create engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            print("\nConnection successful!")
            
            # Check if campgrounds table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'campgrounds'
                )
            """))
            table_exists = result.scalar()
            
            if table_exists:
                print("Campgrounds table exists")
                
                # Count campgrounds
                result = conn.execute(text("SELECT COUNT(*) FROM campgrounds"))
                count = result.scalar()
                print(f"Found {count} campgrounds in the database")
                
                if count > 0:
                    # Get sample campgrounds
                    result = conn.execute(text("SELECT id, name, latitude, longitude, region_name FROM campgrounds LIMIT 5"))
                    campgrounds = result.fetchall()
                    
                    print("\nSample campgrounds:")
                    for campground in campgrounds:
                        print(f"ID: {campground[0]}, Name: {campground[1]}, Location: ({campground[2]}, {campground[3]}), Region: {campground[4]}")
                    
                    # Get most recent update
                    result = conn.execute(text("SELECT MAX(updated_at) FROM campgrounds"))
                    last_update = result.scalar()
                    
                    if last_update:
                        print(f"\nLast update: {last_update}")
            else:
                print("Campgrounds table does not exist")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    print("\nDatabase testing completed!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test The Dyrt scraper database")
    parser.add_argument("--db-url", help="Database URL")
    
    args = parser.parse_args()
    
    try:
        test_database_connection(db_url=args.db_url)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)