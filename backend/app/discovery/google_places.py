"""Business discovery via the official Google Places API.

Deliberately used instead of scraping Google Search result pages: scraping
Google's SERPs violates Google's Terms of Service and gets IPs CAPTCHA-walled
quickly. The Places API is the sanctioned, structured way to do this and it
returns cleaner data (place_id, address, rating, review count) than an HTML
scrape ever would.

Requires a Google Cloud project with the "Places API" enabled and billing set
up (Google gives a monthly free credit that covers moderate usage). Set
GOOGLE_PLACES_API_KEY in .env.
"""

import asyncio

import httpx
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.discovery.schemas import DiscoveredBusiness

# Transient network/TLS blips (a flaky Wi-Fi hop, a VPN or antivirus doing
# HTTPS inspection that occasionally serves a bad handshake, a momentary DNS
# hiccup) shouldn't kill an entire discovery run — retry those specifically.
_RETRYABLE = (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError)
_retry_network = retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=6),
    retry=retry_if_exception_type(_RETRYABLE),
)

FIND_PLACE_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
NEARBY_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# Google returns at most 20 results per page and at most 3 pages (60 total)
# per Nearby Search request.
MAX_PAGES = 3
RESULTS_PER_PAGE = 20


class GooglePlacesClient:
    def __init__(self, api_key: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.google_places_api_key
        if not self.api_key:
            logger.warning("GOOGLE_PLACES_API_KEY is not set — business discovery will fail.")

    @_retry_network
    async def _geocode_location(self, client: httpx.AsyncClient, location_label: str) -> tuple[float, float] | None:
        params = {
            "input": location_label,
            "inputtype": "textquery",
            "fields": "geometry",
            "key": self.api_key,
        }
        resp = await client.get(FIND_PLACE_URL, params=params, timeout=15)
        data = resp.json()
        candidates = data.get("candidates") or []
        if not candidates:
            logger.error(f"Could not geocode location '{location_label}': {data.get('status')}")
            return None
        loc = candidates[0]["geometry"]["location"]
        return loc["lat"], loc["lng"]

    @_retry_network
    async def _place_details(self, client: httpx.AsyncClient, place_id: str) -> dict:
        params = {
            "place_id": place_id,
            "fields": "formatted_phone_number,international_phone_number,website,url,address_component",
            "key": self.api_key,
        }
        resp = await client.get(PLACE_DETAILS_URL, params=params, timeout=15)
        data = resp.json()
        return data.get("result", {})

    def _extract_address_component(self, components: list[dict], type_name: str) -> str | None:
        for comp in components:
            if type_name in comp.get("types", []):
                return comp.get("long_name")
        return None

    @_retry_network
    async def _nearby_search_page(self, client: httpx.AsyncClient, params: dict) -> dict:
        resp = await client.get(NEARBY_SEARCH_URL, params=params, timeout=15)
        return resp.json()

    async def search_businesses(
        self,
        business_type: str,
        city: str,
        state: str | None,
        country: str,
        radius_km: int,
        max_results: int,
        fetch_details: bool = True,
    ) -> list[DiscoveredBusiness]:
        if not self.api_key:
            raise RuntimeError("Google Places API key is not configured. Set GOOGLE_PLACES_API_KEY in .env.")

        location_label = ", ".join(filter(None, [city, state, country]))
        results: list[DiscoveredBusiness] = []

        async with httpx.AsyncClient() as client:
            coords = await self._geocode_location(client, location_label)
            if coords is None:
                return results
            lat, lng = coords

            params = {
                "location": f"{lat},{lng}",
                "radius": min(radius_km, 50) * 1000,  # Nearby Search caps at 50km radius
                "keyword": business_type,
                "key": self.api_key,
            }

            page_token: str | None = None
            for page in range(MAX_PAGES):
                if page_token:
                    params = {"pagetoken": page_token, "key": self.api_key}
                    await asyncio.sleep(2)  # Google requires a short delay before a page token becomes valid

                data = await self._nearby_search_page(client, params)
                status = data.get("status")
                if status not in ("OK", "ZERO_RESULTS"):
                    logger.error(f"Google Places Nearby Search error: {status} — {data.get('error_message')}")
                    break

                for place in data.get("results", []):
                    if len(results) >= max_results:
                        break

                    details = {}
                    if fetch_details:
                        try:
                            details = await self._place_details(client, place["place_id"])
                        except Exception as exc:  # noqa: BLE001
                            logger.warning(f"Place details lookup failed for {place.get('name')}: {exc}")

                    components = details.get("address_component", [])
                    results.append(
                        DiscoveredBusiness(
                            source="google_places",
                            business_name=place.get("name", "Unknown"),
                            website=details.get("website"),
                            phone=details.get("formatted_phone_number") or details.get("international_phone_number"),
                            address=place.get("vicinity"),
                            city=self._extract_address_component(components, "locality") or city,
                            state=self._extract_address_component(components, "administrative_area_level_1") or state,
                            country=self._extract_address_component(components, "country") or country,
                            google_place_id=place.get("place_id"),
                            google_maps_url=details.get("url"),
                            google_rating=place.get("rating"),
                            google_reviews_count=place.get("user_ratings_total"),
                        )
                    )

                if len(results) >= max_results:
                    break

                page_token = data.get("next_page_token")
                if not page_token:
                    break

        logger.info(f"Google Places discovery found {len(results)} businesses for '{business_type}' near {location_label}")
        return results
