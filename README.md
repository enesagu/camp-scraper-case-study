# Web-Scrape Case Study

## Overview

Develop a scraper to extract all campground locations across the United States from The Dyrt ([https://thedyrt.com/search](https://thedyrt.com/search)) by leveraging their map interface, which exposes latitude/longitude data through API requests triggered by mouse movement. You are free to use any library (requests, httpx, selenium, playwright).

**Hint:** Look for a search endpoint in the browser’s network tab!

For questions, contact us at [info@smart-maple.com](mailto:info@smart-maple.com)

---

## Core Requirements

* ✅ **Connect to PostgreSQL with Docker Compose and create required tables** (15p)

  * Implemented
  * `docker-compose.yml` sets up a PostgreSQL service.
  * SQLAlchemy ORM model is defined in `src/database.py`, and tables are created via `init_db()`.

* ✅ **Scrape all US campground data and store in database** (30p)

  * Implemented
  * `DyrtScraper` divides the US map into 16 bounding boxes and scrapes each area iteratively.

* ✅ **Validate data using Pydantic** (15p)

  * Implemented
  * A Pydantic model in `src/models/campground.py` validates each item before insertion.

* ✅ **Schedule recurring scraping jobs (cron-like)** (15p)

  * Implemented
  * The `schedule` library is used in `scheduler.py` to support daily/hourly/weekly runs.

* ✅ **Update existing records if found** (10p)

  * Implemented
  * The scraper checks if each item already exists and updates it if necessary.

* ✅ **Handle HTTP errors and implement retry mechanism** (15p)

  * Implemented
  * Retries are handled using the `tenacity` library with proper logging on failure.

---

## Bonus Features

* ✅ **ORM-based database operations**

  * Fully implemented using SQLAlchemy.

* ✅ **Advanced logging system**

  * Loguru is used to log to both the console and rotating log files.

* ✅ **FastAPI endpoint for triggering and controlling scraper**

  * Available endpoints include `/scrape`, `/status`, and `/campgrounds`.

* ✅ **Async / Multithreading performance boost**

  * Scraper runs asynchronously using `run_in_executor` to offload blocking work.

* ✅ **Reverse geocoding from lat/lon**

  * Geopy with Nominatim is used to retrieve addresses if they are missing from the API.

* ✅ **Creative/Additional fields**

  * `address` is created by combining multiple fields or by geocoding.
  * Swagger UI is auto-generated and available for testing endpoints.

---

## Setup and Installation

### Option 1: Docker (Recommended)

```bash
git clone <repo_url>
cd <repo_name>

docker-compose up -d
```

### Option 2: Local Development

```bash
pip install -r requirements.txt

# For Windows
t.​\u200b\u200b setup_local_db.bat

# For Unix/Linux/macOS
chmod +x setup_local_db.sh
./setup_local_db.sh
```

---

## Running and Testing

### Docker Environment

```bash
# Start services
docker-compose up -d

# Run scraper once
docker-compose run scraper python main.py --scrape

# Run API server
docker-compose run -p 8000:8000 scraper python main.py --api

# Start scheduler every 24 hours
docker-compose run scraper python main.py --schedule 24

# View logs
docker-compose logs -f scraper
```

### Local Execution

```bash
# Run scraper
python main.py --scrape

# Start API server
python main.py --api

# Start scheduler (e.g., every 24 hours)
python main.py --schedule 24
```

---

## API Endpoints

```bash
GET     /                  # Welcome message
POST    /scrape            # Start scraper in background
GET     /status            # Check scraper status
GET     /campgrounds       # List campgrounds
GET     /campgrounds/{id}  # Get campground details by ID
```

---

## Database Inspection

```sql
-- Connect to PostgreSQL
docker-compose exec postgres psql -U user -d case_study

-- List sample campgrounds
SELECT id, name, latitude, longitude FROM campgrounds LIMIT 10;

-- Count total campgrounds
SELECT COUNT(*) FROM campgrounds;
```

---

## How It Works

1. **Entry Point**: `main.py` supports `--scrape`, `--api`, and `--schedule` flags.
2. **Region Division**: The US is divided into 16 regions to scrape data in manageable chunks.
3. **Data Validation**: All data is validated with Pydantic before storage.
4. **Upsert Logic**: Existing records are updated; new ones are inserted.
5. **Geocoding**: Missing addresses are retrieved using reverse geocoding (Geopy + Nominatim).
6. **Interactive API**: A FastAPI server provides endpoints for manual control and monitoring of scraping jobs.
