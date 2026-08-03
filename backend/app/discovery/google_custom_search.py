"""Fallback / supplemental discovery via the official Google Custom Search
JSON API — used when Places doesn't return enough results for a niche
business type, or Places coverage is thin in a region. This is the sanctioned
API, not scraping of google.com/search result pages.

Requires a Programmable Search Engine (cx id) configured to search the whole
web, plus a Custom Search API key. Set GOOGLE_CUSTOM_SEARCH_API_KEY and
GOOGLE_CUSTOM_SEARCH_CX in .env.
"""

import re
from urllib.parse import urlparse

import httpx
from loguru import logger
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.discovery.schemas import DiscoveredBusiness

# See google_places.py for why: transient network/TLS blips shouldn't kill
# an entire discovery run.
_RETRYABLE = (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError)
_retry_network = retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=6),
    retry=retry_if_exception_type(_RETRYABLE),
)

CUSTOM_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"
RESULTS_PER_PAGE = 10
MAX_PAGES = 10  # Custom Search free/paid tiers cap at 100 results per query


class GoogleCustomSearchClient:
    def __init__(self, api_key: str | None = None, cx: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.google_custom_search_api_key
        self.cx = cx or settings.google_custom_search_cx

    @_retry_network
    async def _search(self, client: httpx.AsyncClient, params: dict) -> dict:
        resp = await client.get(CUSTOM_SEARCH_URL, params=params, timeout=15)
        return resp.json()

    async def search_business_websites(
        self,
        business_type: str,
        city: str,
        state: str | None,
        country: str,
        max_results: int,
        exclude_domains: set[str] | None = None,
    ) -> list[DiscoveredBusiness]:
        if not self.api_key or not self.cx:
            logger.warning("Google Custom Search is not configured — skipping supplemental discovery.")
            return []

        exclude_domains = exclude_domains or set()
        location_label = ", ".join(filter(None, [city, state, country]))
        query = f"{business_type} {location_label}"

        results: list[DiscoveredBusiness] = []
        seen_domains: set[str] = set(exclude_domains)

        async with httpx.AsyncClient() as client:
            for page in range(MAX_PAGES):
                if len(results) >= max_results:
                    break
                params = {
                    "key": self.api_key,
                    "cx": self.cx,
                    "q": query,
                    "start": page * RESULTS_PER_PAGE + 1,
                    "num": RESULTS_PER_PAGE,
                }
                data = await self._search(client, params)
                if "error" in data:
                    logger.error(f"Google Custom Search error: {data['error'].get('message')}")
                    break

                items = data.get("items", [])
                if not items:
                    break

                for item in items:
                    link = item.get("link")
                    if not link:
                        continue
                    domain = urlparse(link).netloc.replace("www.", "")
                    if domain in seen_domains:
                        continue
                    seen_domains.add(domain)

                    results.append(
                        DiscoveredBusiness(
                            source="google_custom_search",
                            business_name=item.get("title", domain),
                            website=link,
                            city=city,
                            state=state,
                            country=country,
                        )
                    )
                    if len(results) >= max_results:
                        break

        logger.info(f"Google Custom Search discovery found {len(results)} supplemental businesses for '{query}'")
        return results

    async def find_person_linkedin(self, full_name: str, business_name: str) -> str | None:
        """Looks up a decision-maker's public LinkedIn profile via the official
        Custom Search API — never visits or scrapes LinkedIn itself, just reads
        the search result URL/snippet Google already indexed.

        Only returns a URL when it's a confident match: the result must be a
        linkedin.com/in/ profile AND the person's name must actually appear in
        the URL slug or result title. Anything less confident returns None
        rather than risk attaching a stranger's profile to a lead.
        """
        if not self.api_key or not self.cx:
            return None

        name_parts = [p.lower() for p in re.sub(r"[^a-zA-Z\s'-]", "", full_name).split() if len(p) > 1]
        if not name_parts:
            return None
        last_name = name_parts[-1]

        query = f'"{full_name}" "{business_name}" site:linkedin.com/in'

        async with httpx.AsyncClient() as client:
            params = {"key": self.api_key, "cx": self.cx, "q": query, "num": 5}
            try:
                data = await self._search(client, params)
            except (httpx.HTTPError, ValueError) as exc:
                logger.warning(f"LinkedIn lookup failed for '{full_name}': {exc}")
                return None

        if "error" in data:
            logger.warning(f"Google Custom Search error during LinkedIn lookup: {data['error'].get('message')}")
            return None

        for item in data.get("items", []):
            link = item.get("link", "")
            if "linkedin.com/in/" not in link:
                continue
            haystack = f"{link} {item.get('title', '')}".lower()
            if last_name in haystack:
                return link

        return None
