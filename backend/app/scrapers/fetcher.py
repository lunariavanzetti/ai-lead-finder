import time
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx
from loguru import logger
from playwright.async_api import async_playwright
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.rate_limiter import DomainRateLimiter
from app.core.robots import is_allowed
from app.scrapers.user_agents import pick_user_agent

BOT_WALL_MARKERS = [
    "captcha", "are you a human", "verify you are a human", "cf-browser-verification",
    "pardon our interruption", "access denied", "unusual traffic", "request blocked",
    "please enable javascript and cookies",
]


@dataclass
class FetchResult:
    url: str
    final_url: str
    status_code: int | None
    html: str | None
    load_time_ms: float | None
    blocked: bool
    error: str | None = None


class CrawlConfig:
    def __init__(
        self,
        timeout_seconds: int = 15,
        retries: int = 2,
        delay_seconds: float = 2.5,
        proxy_url: str | None = None,
        rotate_user_agent: bool = True,
        respect_robots: bool = True,
    ):
        self.timeout_seconds = timeout_seconds
        self.retries = retries
        self.rate_limiter = DomainRateLimiter(delay_seconds)
        self.proxy_url = proxy_url
        self.rotate_user_agent = rotate_user_agent
        self.respect_robots = respect_robots
        self._ua_counter = 0


def _looks_like_bot_wall(status_code: int, html: str) -> bool:
    if status_code in (403, 429, 503):
        return True
    lowered = (html or "")[:5000].lower()
    return any(marker in lowered for marker in BOT_WALL_MARKERS)


class SiteFetcher:
    """Fetches a page with httpx first (fast, cheap); falls back to Playwright
    only when the page appears to be JS-rendered (near-empty body) or httpx
    was blocked outright. Never attempts to solve or bypass a CAPTCHA — a
    detected bot-wall is reported back as `blocked=True` and the caller skips
    that domain."""

    def __init__(self, config: CrawlConfig):
        self.config = config
        self.settings = get_settings()

    async def fetch(self, url: str, use_playwright_fallback: bool = True) -> FetchResult:
        domain = urlparse(url).netloc

        async with httpx.AsyncClient(follow_redirects=True, proxy=self.config.proxy_url) as client:
            if self.config.respect_robots and not await is_allowed(url, client):
                return FetchResult(url, url, None, None, None, blocked=True, error="disallowed_by_robots_txt")

            await self.config.rate_limiter.wait(domain)

            try:
                result = await self._fetch_httpx(client, url)
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"httpx fetch failed for {url}: {exc}")
                result = FetchResult(url, url, None, None, None, blocked=False, error=str(exc))

        needs_js = result.html is not None and len(result.html.strip()) < 500
        if use_playwright_fallback and (result.error or needs_js) and not result.blocked:
            logger.info(f"Falling back to Playwright for {url}")
            result = await self._fetch_playwright(url)

        return result

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadTimeout)),
    )
    async def _fetch_httpx(self, client: httpx.AsyncClient, url: str) -> FetchResult:
        headers = {
            "User-Agent": pick_user_agent(self.config._ua_counter, self.config.rotate_user_agent, self.settings.user_agent),
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.config._ua_counter += 1

        started = time.monotonic()
        resp = await client.get(url, headers=headers, timeout=self.config.timeout_seconds)
        load_time_ms = (time.monotonic() - started) * 1000

        blocked = _looks_like_bot_wall(resp.status_code, resp.text)
        return FetchResult(
            url=url,
            final_url=str(resp.url),
            status_code=resp.status_code,
            html=resp.text if not blocked else None,
            load_time_ms=load_time_ms,
            blocked=blocked,
            error="bot_wall_detected" if blocked else None,
        )

    async def _fetch_playwright(self, url: str) -> FetchResult:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context_kwargs = {}
                if self.config.proxy_url:
                    context_kwargs["proxy"] = {"server": self.config.proxy_url}
                context = await browser.new_context(
                    user_agent=pick_user_agent(self.config._ua_counter, self.config.rotate_user_agent, self.settings.user_agent),
                    **context_kwargs,
                )
                page = await context.new_page()
                started = time.monotonic()
                try:
                    resp = await page.goto(url, timeout=self.config.timeout_seconds * 1000, wait_until="networkidle")
                    html = await page.content()
                    status_code = resp.status if resp else None
                finally:
                    load_time_ms = (time.monotonic() - started) * 1000
                    final_url = page.url
                    await context.close()
                    await browser.close()

                blocked = _looks_like_bot_wall(status_code or 200, html)
                return FetchResult(
                    url=url,
                    final_url=final_url,
                    status_code=status_code,
                    html=html if not blocked else None,
                    load_time_ms=load_time_ms,
                    blocked=blocked,
                    error="bot_wall_detected" if blocked else None,
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Playwright fetch failed for {url}: {exc}")
            return FetchResult(url, url, None, None, None, blocked=False, error=str(exc))

    async def screenshot(self, url: str, out_path: str) -> bool:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(viewport={"width": 1440, "height": 900})
                page = await context.new_page()
                await page.goto(url, timeout=self.config.timeout_seconds * 1000, wait_until="networkidle")
                await page.screenshot(path=out_path, full_page=False)
                await context.close()
                await browser.close()
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Screenshot failed for {url}: {exc}")
            return False
