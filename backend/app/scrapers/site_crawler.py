from dataclasses import dataclass, field

from bs4 import BeautifulSoup
from loguru import logger

from app.scrapers.fetcher import CrawlConfig, SiteFetcher
from app.scrapers.link_discovery import find_about_page, find_booking_link, find_contact_page, find_staff_page


@dataclass
class SiteCrawlBundle:
    website: str
    homepage_html: str | None = None
    contact_html: str | None = None
    contact_url: str | None = None
    staff_html: str | None = None
    staff_url: str | None = None
    about_html: str | None = None
    about_url: str | None = None
    booking_link: str | None = None
    load_time_ms: float | None = None
    screenshot_path: str | None = None
    blocked: bool = False
    error: str | None = None
    extra_pages_html: dict[str, str] = field(default_factory=dict)


class SiteCrawler:
    def __init__(self, config: CrawlConfig):
        self.fetcher = SiteFetcher(config)

    async def crawl(self, website: str, capture_screenshot: bool = False, screenshot_path: str | None = None) -> SiteCrawlBundle:
        bundle = SiteCrawlBundle(website=website)

        home_result = await self.fetcher.fetch(website)
        bundle.load_time_ms = home_result.load_time_ms

        if home_result.blocked:
            bundle.blocked = True
            bundle.error = home_result.error
            return bundle

        if not home_result.html:
            bundle.error = home_result.error or "no_content"
            return bundle

        bundle.homepage_html = home_result.html
        soup = BeautifulSoup(home_result.html, "lxml")
        base_url = home_result.final_url

        bundle.booking_link = find_booking_link(soup, base_url)

        contact_url = find_contact_page(soup, base_url)
        if contact_url:
            contact_result = await self.fetcher.fetch(contact_url)
            if contact_result.html and not contact_result.blocked:
                bundle.contact_html = contact_result.html
                bundle.contact_url = contact_url

        staff_url = find_staff_page(soup, base_url)
        if staff_url:
            staff_result = await self.fetcher.fetch(staff_url)
            if staff_result.html and not staff_result.blocked:
                bundle.staff_html = staff_result.html
                bundle.staff_url = staff_url

        about_url = find_about_page(soup, base_url)
        if about_url and about_url != staff_url:
            about_result = await self.fetcher.fetch(about_url)
            if about_result.html and not about_result.blocked:
                bundle.about_html = about_result.html
                bundle.about_url = about_url
                # Some small business sites list their team on the About page instead of a dedicated Team page.
                if not bundle.staff_html:
                    bundle.staff_html = about_result.html
                    bundle.staff_url = about_url

        if capture_screenshot and screenshot_path:
            try:
                ok = await self.fetcher.screenshot(website, screenshot_path)
                if ok:
                    bundle.screenshot_path = screenshot_path
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"Screenshot capture failed for {website}: {exc}")

        return bundle
