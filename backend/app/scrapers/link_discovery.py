from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

CONTACT_PATTERNS = ["contact", "contact-us", "get-in-touch", "reach-us"]
STAFF_PATTERNS = ["team", "our-team", "staff", "doctors", "attorneys", "providers", "our-doctors", "physicians", "people"]
ABOUT_PATTERNS = ["about", "about-us", "who-we-are"]
BOOKING_PATTERNS = ["book", "booking", "appointment", "schedule", "reservations", "calendly.com", "acuityscheduling.com", "square.site"]


def _same_domain(base_url: str, link: str) -> bool:
    return urlparse(base_url).netloc.replace("www.", "") == urlparse(link).netloc.replace("www.", "")


def _find_matching_link(soup: BeautifulSoup, base_url: str, patterns: list[str]) -> str | None:
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        full_url = urljoin(base_url, href)
        haystack = f"{href} {a.get_text(' ', strip=True)}".lower()
        if any(pattern in haystack for pattern in patterns):
            return full_url
    return None


def find_contact_page(soup: BeautifulSoup, base_url: str) -> str | None:
    return _find_matching_link(soup, base_url, CONTACT_PATTERNS)


def find_staff_page(soup: BeautifulSoup, base_url: str) -> str | None:
    return _find_matching_link(soup, base_url, STAFF_PATTERNS)


def find_about_page(soup: BeautifulSoup, base_url: str) -> str | None:
    return _find_matching_link(soup, base_url, ABOUT_PATTERNS)


def find_booking_link(soup: BeautifulSoup, base_url: str) -> str | None:
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        haystack = f"{href} {a.get_text(' ', strip=True)}".lower()
        if any(pattern in haystack for pattern in BOOKING_PATTERNS):
            return href if href.startswith("http") else urljoin(base_url, href)
    return None
