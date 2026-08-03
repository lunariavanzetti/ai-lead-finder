from bs4 import BeautifulSoup

SOCIAL_DOMAINS = {
    "facebook": ["facebook.com", "fb.com"],
    "instagram": ["instagram.com"],
    "linkedin": ["linkedin.com/company", "linkedin.com/in"],
    "whatsapp": ["wa.me", "api.whatsapp.com"],
    "messenger": ["m.me", "messenger.com"],
}


def extract_social_links(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    links = [a["href"] for a in soup.find_all("a", href=True)]

    result = {
        "facebook_url": None,
        "instagram_url": None,
        "linkedin_company_url": None,
        "whatsapp_detected": False,
        "messenger_detected": False,
    }

    for link in links:
        lowered = link.lower()
        if not result["facebook_url"] and any(d in lowered for d in SOCIAL_DOMAINS["facebook"]):
            result["facebook_url"] = link
        if not result["instagram_url"] and any(d in lowered for d in SOCIAL_DOMAINS["instagram"]):
            result["instagram_url"] = link
        if not result["linkedin_company_url"] and any(d in lowered for d in SOCIAL_DOMAINS["linkedin"]):
            result["linkedin_company_url"] = link
        if any(d in lowered for d in SOCIAL_DOMAINS["whatsapp"]):
            result["whatsapp_detected"] = True
        if any(d in lowered for d in SOCIAL_DOMAINS["messenger"]):
            result["messenger_detected"] = True

    return result
