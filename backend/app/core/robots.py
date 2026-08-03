from urllib.parse import urljoin, urlparse

import httpx
from loguru import logger
from protego import Protego

from app.core.config import get_settings

_robots_cache: dict[str, Protego] = {}


async def _fetch_robots(base_url: str, client: httpx.AsyncClient) -> Protego:
    robots_url = urljoin(base_url, "/robots.txt")
    try:
        resp = await client.get(robots_url, timeout=10)
        content = resp.text if resp.status_code == 200 else ""
    except httpx.HTTPError:
        content = ""
    return Protego.parse(content)


async def is_allowed(url: str, client: httpx.AsyncClient) -> bool:
    """Checks robots.txt for the given URL's domain. Fails open (allowed) only
    when robots.txt is unreachable, per standard crawler convention, but always
    respects an explicit Disallow when robots.txt is present."""
    settings = get_settings()
    if not settings.respect_robots_txt:
        return True

    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    if base_url not in _robots_cache:
        _robots_cache[base_url] = await _fetch_robots(base_url, client)

    robots = _robots_cache[base_url]
    allowed = robots.can_fetch(url, settings.user_agent)
    if not allowed:
        logger.info(f"robots.txt disallows crawling: {url}")
    return allowed
