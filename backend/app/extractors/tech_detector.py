import re

from bs4 import BeautifulSoup

# Known script/domain/class-name signatures for common widgets and tools.
# This is inherently a best-effort heuristic list, not exhaustive — it's meant
# to catch the widely-used tools a small/local business is most likely to run.
SIGNATURES = {
    "live_chat": [
        "tawk.to", "tidio", "livechatinc.com", "crisp.chat", "zopim", "purechat",
        "olark.com", "smartsupp.com",
    ],
    "chatbot": [
        "intercom.io", "drift.com", "chatbot.com", "landbot.io", "mobilemonkey",
        "manychat.com", "botpress",
    ],
    "booking_system": [
        "calendly.com", "acuityscheduling.com", "squareup.com/appointments",
        "square.site", "setmore.com", "booksy.com", "opentable.com", "resy.com",
        "simplybook.me", "vagaro.com", "zocdoc.com", "mindbodyonline.com",
    ],
    "facebook_pixel": ["connect.facebook.net", "fbevents.js", "fbq("],
    "google_analytics": ["google-analytics.com", "googletagmanager.com", "gtag("],
    "crm": [
        "hubspot.com", "hs-scripts.com", "salesforce.com", "pipedrive.com",
        "zoho.com", "activecampaign.com",
    ],
    "newsletter": ["mailchimp.com", "klaviyo.com", "constantcontact.com", "sendinblue.com", "convertkit.com"],
    "google_reviews_widget": ["elfsight.com", "trustindex.io", "reviews.io", "widget.reviews"],
}


def _search_signatures(html_lower: str, keywords: list[str]) -> bool:
    return any(kw in html_lower for kw in keywords)


def _has_faq_section(soup: BeautifulSoup) -> bool:
    text = soup.get_text(" ", strip=True).lower()
    if "frequently asked question" in text or re.search(r"\bfaq\b", text):
        return True
    if soup.find(attrs={"itemtype": re.compile("FAQPage", re.I)}):
        return True
    return False


def _has_mobile_viewport(soup: BeautifulSoup) -> bool:
    tag = soup.find("meta", attrs={"name": "viewport"})
    return bool(tag and "width=device-width" in (tag.get("content") or ""))


def detect_technologies(html: str, website_url: str, load_time_ms: float | None) -> dict:
    soup = BeautifulSoup(html, "lxml")
    html_lower = html.lower()

    technologies = {
        name: _search_signatures(html_lower, keywords) for name, keywords in SIGNATURES.items()
    }
    technologies["ssl"] = website_url.lower().startswith("https://")
    technologies["mobile_friendly"] = _has_mobile_viewport(soup)
    technologies["faq"] = _has_faq_section(soup)
    technologies["speed_ms"] = round(load_time_ms) if load_time_ms is not None else None
    technologies["is_slow"] = bool(load_time_ms and load_time_ms > 3000)
    technologies["instagram_feed"] = "instagram" in html_lower and ("feed" in html_lower or "elfsight" in html_lower or "curator.io" in html_lower)

    return technologies
