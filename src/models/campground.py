from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CampgroundLinks(BaseModel):
    self: str  # URL, ama HttpUrl yerine str kullanıyoruz (daha esnek)


class Campground(BaseModel):
    """
    The Dyrt kamp alanı verisi için Pydantic doğrulama modeli.
    """
    id: str
    type: str
    links: CampgroundLinks
    name: str
    latitude: float
    longitude: float

    region_name: Optional[str] = Field(None, alias="region-name")
    administrative_area: Optional[str] = Field(None, alias="administrative-area")
    nearest_city_name: Optional[str] = Field(None, alias="nearest-city-name")

    accommodation_type_names: List[str] = Field(default_factory=list, alias="accommodation-type-names")
    bookable: bool = Field(default=False)
    camper_types: List[str] = Field(default_factory=list, alias="camper-types")
    operator: Optional[str] = None

    photo_url: Optional[str] = Field(None, alias="photo-url")
    photo_urls: List[str] = Field(default_factory=list, alias="photo-urls")
    photos_count: int = Field(default=0, alias="photos-count")

    rating: Optional[float] = None
    reviews_count: int = Field(default=0, alias="reviews-count")
    slug: Optional[str] = None

    price_low: Optional[float] = Field(None, alias="price-low")
    price_high: Optional[float] = Field(None, alias="price-high")
    availability_updated_at: Optional[datetime] = Field(None, alias="availability-updated-at")

    # Bonus alan: ters geocoding için kullanılabilir
    address: Optional[str] = None
