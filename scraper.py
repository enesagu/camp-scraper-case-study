import json
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential

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

    def get_all_us_campgrounds(self) -> List[Campground]:
        us_bounds = {"north": 49.38, "south": 24.52, "east": -66.95, "west": -124.77}
        regions = self._divide_region(us_bounds)
        all_cg: List[Campground] = []

        for idx, region in enumerate(regions):
            logger.info(f"\U0001F4CD Region {idx+1}/{len(regions)}: {region}")
            all_cg.extend(self._get_campgrounds_in_region(region))
            time.sleep(1)

        logger.info(f"\u2705 Total campgrounds collected (raw): {len(all_cg)}")
        return all_cg

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
                data = {
                    "id": item.get("id"),
                    "type": item.get("type"),
                    "links": {"self": item.get("links", {}).get("self")},
                    "name": attrs.get("name"),
                    "latitude": attrs.get("latitude"),
                    "longitude": attrs.get("longitude"),
                    "region-name": attrs.get("region-name") or attrs.get("administrative-area") or "Unknown",
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
                    "availability-updated-at": datetime.fromisoformat(attrs["availability-updated-at"]) if attrs.get("availability-updated-at") else None,
                }
                try:
                    camp = Campground.model_validate(data)
                    camp_list.append(camp)
                except ValidationError as ve:
                    logger.warning(f"\u274C Validation failed {data['id']}: {ve}")

            if len(items) < 100:
                break
            page += 1
            time.sleep(1)

        logger.info(f"\U0001F9E9 Found {len(camp_list)} in region.")
        return camp_list

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
                ))
            count += 1

        try:
            self.db.commit()
            logger.info(f"\U0001F5C8️ Saved/updated {count} unique campgrounds")
        except Exception as e:
            logger.error(f"❗ Commit failed: {e}")
            self.db.rollback()

    def run(self) -> None:
        logger.info("\U0001F680 Scraper started")
        try:
            campgrounds = self.get_all_us_campgrounds()
            self.save_campgrounds(campgrounds)
            logger.info("✅ Scraper finished")
        except Exception as err:
            logger.error(f"❌ Fatal error: {err}")


if __name__ == "__main__":
    DyrtScraper().run()
