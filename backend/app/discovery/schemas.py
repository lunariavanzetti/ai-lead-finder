from pydantic import BaseModel


class DiscoveredBusiness(BaseModel):
    """Normalized business record coming out of the discovery layer, before the
    site crawl enriches it further."""

    source: str  # "google_places" | "google_custom_search"
    business_name: str
    website: str | None = None
    phone: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    google_place_id: str | None = None
    google_maps_url: str | None = None
    google_rating: float | None = None
    google_reviews_count: int | None = None
