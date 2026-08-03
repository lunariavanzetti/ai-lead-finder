# Category-specific phrasing for the same underlying gap, falling back to a
# generic label when the detected business type has no custom copy. Matched
# by substring against whatever the user typed/selected in Business Type
# (dropdown value like "Dentist" or free text like "Family Dental Clinic"),
# so this deliberately doesn't require an exact key match.
CATEGORY_LABEL_OVERRIDES = [
    (["dent"], {"booking_system": "No online appointment booking"}),
    (["medical", "clinic", "doctor", "physician"], {"booking_system": "No online appointment booking"}),
    (["vet"], {"booking_system": "No online appointment booking"}),
    (["salon", "spa", "barber"], {"booking_system": "No online booking"}),
    (["gym", "fitness"], {"booking_system": "No online class/session booking"}),
    (["restaurant", "cafe", "diner"], {"booking_system": "No online reservations"}),
    (["law", "attorney", "legal"], {"booking_system": "No online consultation scheduling"}),
]

GENERIC_LABELS = {
    "chatbot": "No chatbot",
    "live_chat": "No live chat",
    "booking_system": "No online booking system",
    "faq": "No FAQ section",
    "is_slow": "Slow-loading website",
    "ssl": "Missing SSL certificate",
    "contact_form": "No online contact form",
    "google_reviews_widget": "No review automation / review widget",
    "reminders": "No appointment reminder system",
    "ai_receptionist": "Missed-call risk — no AI receptionist / after-hours coverage",
    "mobile_friendly": "Website is not mobile-friendly",
}


def _label(code: str, business_type: str) -> str:
    lowered = business_type.lower()
    for keywords, overrides in CATEGORY_LABEL_OVERRIDES:
        if code in overrides and any(kw in lowered for kw in keywords):
            return overrides[code]
    return GENERIC_LABELS[code]


def generate_pain_points(
    technologies: dict,
    has_contact_form: bool,
    booking_link: str | None,
    business_type: str,
) -> list[dict]:
    """Rule-based pain point / automation-opportunity detector. No external AI
    call — purely a checklist evaluated against what the crawler found."""

    findings: list[dict] = []

    def add(code: str, severity: str = "medium"):
        findings.append({"code": code, "label": _label(code, business_type), "severity": severity})

    if not technologies.get("chatbot"):
        add("chatbot", "high")
    if not technologies.get("live_chat"):
        add("live_chat", "medium")
    if not booking_link and not technologies.get("booking_system"):
        add("booking_system", "high")
        add("reminders", "medium")
    if not technologies.get("faq"):
        add("faq", "low")
    if technologies.get("is_slow"):
        add("is_slow", "medium")
    if not technologies.get("ssl"):
        add("ssl", "high")
    if not has_contact_form:
        add("contact_form", "medium")
    if not technologies.get("google_reviews_widget"):
        add("google_reviews_widget", "medium")
    if not technologies.get("mobile_friendly"):
        add("mobile_friendly", "high")
    if not technologies.get("live_chat") and not technologies.get("chatbot"):
        add("ai_receptionist", "high")

    return findings
