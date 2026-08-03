import re

from bs4 import BeautifulSoup

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9.\-_+]+@[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_.]+")
PHONE_REGEX = re.compile(
    r"(\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
)

IGNORED_EMAIL_DOMAINS = {
    "example.com", "yourdomain.com", "domain.com", "email.com", "wixpress.com",
    "sentry.io", "godaddy.com", "schema.org", "ingest.sentry.io",
    "browser-intake-datadoghq.com", "browser-intake-datadoghq.eu",
}
IGNORED_EMAIL_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js")

ROLE_BASED_LOCAL_PARTS = {
    "info", "contact", "office", "hello", "support", "admin", "sales",
    "team", "enquiries", "inquiries", "front desk", "frontdesk", "reception",
}


def extract_emails(html: str) -> list[str]:
    found = set()

    soup = BeautifulSoup(html, "lxml")
    for a in soup.find_all("a", href=True):
        if a["href"].lower().startswith("mailto:"):
            addr = a["href"][7:].split("?")[0].strip()
            if addr:
                found.add(addr.lower())

    for match in EMAIL_REGEX.findall(html):
        found.add(match.lower())

    cleaned = []
    for email in found:
        domain = email.split("@")[-1]
        if any(domain == d or domain.endswith(f".{d}") for d in IGNORED_EMAIL_DOMAINS):
            continue
        if email.endswith(IGNORED_EMAIL_SUFFIXES):
            continue
        cleaned.append(email)

    return sorted(set(cleaned))


def is_role_based_email(email: str) -> bool:
    local_part = email.split("@")[0].lower()
    return local_part in ROLE_BASED_LOCAL_PARTS


def extract_phones(html: str) -> list[str]:
    found = set()

    soup = BeautifulSoup(html, "lxml")
    for a in soup.find_all("a", href=True):
        if a["href"].lower().startswith("tel:"):
            number = a["href"][4:].strip()
            if number:
                found.add(number)

    text = soup.get_text(" ", strip=True)
    for match in re.finditer(PHONE_REGEX, text):
        candidate = match.group(0).strip()
        digits = re.sub(r"\D", "", candidate)
        if 7 <= len(digits) <= 15:
            found.add(candidate)

    return sorted(found)[:5]


def extract_address(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")

    address_tag = soup.find("address")
    if address_tag:
        text = address_tag.get_text(" ", strip=True)
        if text:
            return text

    for el in soup.find_all(attrs={"itemprop": "address"}):
        text = el.get_text(" ", strip=True)
        if text:
            return text

    for el in soup.find_all(class_=re.compile("address", re.I)):
        text = el.get_text(" ", strip=True)
        if text and len(text) < 250:
            return text

    return None


def has_contact_form(html: str) -> bool:
    soup = BeautifulSoup(html, "lxml")
    forms = soup.find_all("form")
    for form in forms:
        text = form.get_text(" ", strip=True).lower()
        inputs = form.find_all(["input", "textarea"])
        if len(inputs) >= 2 and any(
            kw in text for kw in ["message", "email", "name", "contact", "send"]
        ):
            return True
    return bool(forms)
