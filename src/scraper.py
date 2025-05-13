import time
from datetime import datetime
from typing import Dict, List, Optional
import concurrent.futures

import requests
from dateutil.parser import parse as parse_date
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential
from geopy.geocoders import Nominatim

from src.database import CampgroundORM, get_db
from src.models.campground import Campground


class DyrtScraper:
    SEARCH_API_URL = "https://thedyrt.com/api/v6/locations/search-results"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })
        self.db: Session = get_db()
        self.geolocator = Nominatim(user_agent="camp_scraper")

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    def _make_request(self, params: Dict) -> Dict:
        logger.debug(f"Request params: {params}")
        resp = self.session.get(self.SEARCH_API_URL, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def search_campgrounds(self, bounds: Dict[str, float], page: int = 1, per_page: int = 100) -> Dict:
        bbox = f"{bounds['west']},{bounds['south']},{bounds['east']},{bounds['north']}"
        params = {
            "filter[search][bbox]": bbox,
            "sort": "recommended",
            "page[number]": page,
            "page[size]": per_page,
        }
        return self._make_request(params)

    def _divide_region(self, bounds: Dict[str, float], divisions: int = 4) -> List[Dict[str, float]]:
        regions = []
        lat_step = (bounds["north"] - bounds["south"]) / divisions
        lng_step = (bounds["east"] - bounds["west"]) / divisions
        for i in range(divisions):
            for j in range(divisions):
                south = bounds["south"] + i * lat_step
                north = south + lat_step
                west = bounds["west"] + j * lng_step
                east = west + lng_step
                regions.append({"south": south, "north": north, "west": west, "east": east})
        return regions

    def _get_address_from_coords(self, lat: float, lon: float) -> Optional[str]:
        try:
            location = self.geolocator.reverse((lat, lon), language="en", timeout=10)
            return location.address if location else None
        except Exception as e:
            logger.warning(f"Could not resolve address from coords {lat},{lon}: {e}")
            return None

    def _get_campgrounds_in_region(self, bounds: Dict[str, float]) -> List[Campground]:
        camp_list: List[Campground] = []
        page = 1
        while True:
            resp = self.search_campgrounds(bounds, page)
            items = resp.get("data", [])
            if not items:
                break

            for item in items:
                attrs = item.get("attributes", {})
                availability_updated_at = None
                if attrs.get("availability-updated-at"):
                    try:
                        availability_updated_at = parse_date(attrs["availability-updated-at"])
                    except Exception as e:
                        logger.warning(f"⛔ Failed to parse date: {e}")

                address_parts = [
                    attrs.get("name"),
                    attrs.get("administrative-area"),
                    attrs.get("nearest-city-name"),
                    attrs.get("region-name")
                ]
                address = ", ".join(p for p in address_parts if p)
                if not address:
                    address = self._get_address_from_coords(attrs.get("latitude"), attrs.get("longitude"))

                data = {
                    "id": item.get("id"),
                    "type": item.get("type"),
                    "links": {"self": item.get("links", {}).get("self")},
                    "name": attrs.get("name"),
                    "latitude": attrs.get("latitude"),
                    "longitude": attrs.get("longitude"),
                    "region-name": attrs.get("region-name") or "Unknown",
                    "administrative-area": attrs.get("administrative-area"),
                    "nearest-city-name": attrs.get("nearest-city-name"),
                    "accommodation-type-names": attrs.get("accommodation-type-names", []),
                    "bookable": attrs.get("bookable", False),
                    "camper-types": attrs.get("camper-types", []),
                    "operator": attrs.get("operator"),
                    "photo-url": attrs.get("photo-url"),
                    "photo-urls": attrs.get("photo-urls", []),
                    "photos-count": attrs.get("photos-count", 0),
                    "rating": attrs.get("rating"),
                    "reviews-count": attrs.get("reviews-count", 0),
                    "slug": attrs.get("slug"),
                    "price-low": float(attrs["price-low"]) if attrs.get("price-low") else None,
                    "price-high": float(attrs["price-high"]) if attrs.get("price-high") else None,
                    "availability-updated-at": availability_updated_at,
                }

                try:
                    camp = Campground.model_validate(data)
                    camp.__dict__["address"] = address
                    camp_list.append(camp)
                except ValidationError as ve:
                    logger.warning(f"❌ Validation failed {data['id']}: {ve}")

            if len(items) < 100:
                break
            page += 1
            time.sleep(1)

        logger.info(f"🧩 Found {len(camp_list)} in region.")
        return camp_list

    def get_all_us_campgrounds(self) -> List[Campground]:
        us_bounds = {"north": 49.38, "south": 24.52, "east": -66.95, "west": -124.77}
        regions = self._divide_region(us_bounds)
        all_campgrounds: List[Campground] = []

        def process(region):
            try:
                logger.info(f"📍 Processing region: {region}")
                return self._get_campgrounds_in_region(region)
            except Exception as e:
                logger.warning(f"⚠️ Region failed: {region}, Error: {e}")
                return []

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process, region) for region in regions]
            for future in concurrent.futures.as_completed(futures):
                all_campgrounds.extend(future.result())

        logger.info(f"✅ Total campgrounds collected (parallel): {len(all_campgrounds)}")
        return all_campgrounds

    def save_campgrounds(self, campgrounds: List[Campground]) -> None:
        seen_ids = set()
        count = 0
        for cg in campgrounds:
            if cg.id in seen_ids:
                continue
            seen_ids.add(cg.id)

            existing = self.db.get(CampgroundORM, cg.id)
            record = cg.model_dump(by_alias=True)

            if existing:
                for field, val in record.items():
                    if field == "links":
                        setattr(existing, "links_self", val.get("self"))
                    else:
                        setattr(existing, field.replace("-", "_"), val)
                existing.address = getattr(cg, "address", None)
                existing.updated_at = datetime.utcnow()
            else:
                self.db.add(CampgroundORM(
                    id=record["id"],
                    type=record["type"],
                    links_self=record["links"]["self"],
                    name=record["name"],
                    latitude=record["latitude"],
                    longitude=record["longitude"],
                    region_name=record["region-name"],
                    administrative_area=record.get("administrative-area"),
                    nearest_city_name=record.get("nearest-city-name"),
                    accommodation_type_names=record.get("accommodation-type-names", []),
                    bookable=record.get("bookable", False),
                    camper_types=record.get("camper-types", []),
                    operator=record.get("operator"),
                    photo_url=record.get("photo-url"),
                    photo_urls=record.get("photo-urls", []),
                    photos_count=record.get("photos-count", 0),
                    rating=record.get("rating"),
                    reviews_count=record.get("reviews-count", 0),
                    slug=record.get("slug"),
                    price_low=record.get("price-low"),
                    price_high=record.get("price-high"),
                    availability_updated_at=record.get("availability-updated-at"),
                    address=getattr(cg, "address", None)
                ))
            count += 1

        try:
            self.db.commit()
            logger.info(f"🗂️ Saved/updated {count} unique campgrounds")
        except Exception as e:
            logger.error(f"❗ Commit failed: {e}")
            self.db.rollback()

    def run(self) -> None:
        logger.info("🚀 Scraper started")
        try:
            campgrounds = self.get_all_us_campgrounds()
            self.save_campgrounds(campgrounds)
            logger.info("✅ Scraper finished")
        except Exception as err:
            logger.error(f"❌ Fatal error: {err}")


if __name__ == "__main__":
    DyrtScraper().run()
