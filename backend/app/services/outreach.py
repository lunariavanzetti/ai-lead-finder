"""Rule-based (no external AI call) generator for outreach copy: a single-gap
opener, a follow-up nudge, discovery-call questions, and an honest strengths
list. Templates are deliberately built around ONE specific, real observation
per message — never a dump of every detected flaw — following the standard
"observation -> benefit -> question" structure for cold outreach that doesn't
read as spam.
"""

import re

# Ordered by how natural/relatable each gap is as a conversation opener.
# Codes not listed here (ssl, reminders, faq, no_website, unreachable,
# processing_error) are real findings but poor icebreakers — they still show
# up in the audit's pain-point list, just not as the outreach opener.
OUTREACH_PRIORITY = [
    "booking_system", "ai_receptionist", "chatbot", "live_chat",
    "google_reviews_widget", "contact_form", "mobile_friendly", "is_slow",
]

OPENERS = {
    "no_website": "I noticed {business} doesn't have a website come up online yet.",
    "booking_system": "I noticed clients still have to call {business} directly to book — there's no online scheduling on the site.",
    "ai_receptionist": "I noticed {business} probably gets calls after hours that go straight to voicemail.",
    "chatbot": "I noticed {business}'s website doesn't have a way for visitors to get quick answers when the office is closed.",
    "live_chat": "I noticed there's no live chat on {business}'s site, so visitors with a quick question have to call or email and wait.",
    "google_reviews_widget": "I noticed {business} has {rating}★ from {reviews} reviews but no easy way for happy customers to leave new ones.",
    "contact_form": "I noticed {business}'s website doesn't have a simple contact form — reaching out means calling or emailing directly.",
    "mobile_friendly": "I noticed {business}'s website is a little tricky to use on a phone, and that's probably where most visitors are checking you out from.",
    "is_slow": "I noticed {business}'s website takes a moment to load, which can be enough for a visitor to bounce before they even see what you offer.",
}

BENEFITS = {
    "no_website": "I help {category} businesses get set up online with the essentials — a simple site, online booking, and a way for people to reach you after hours.",
    "booking_system": "I help {category} businesses add self-serve online booking so your team spends less time on scheduling calls.",
    "ai_receptionist": "I help businesses set up an AI receptionist that picks up after-hours calls and handles simple requests automatically.",
    "chatbot": "I help {category} businesses automate common questions so your front desk isn't repeating the same answers all day.",
    "live_chat": "I help businesses add a simple way to answer quick questions in real time without adding headcount.",
    "google_reviews_widget": "I help businesses automatically ask happy customers for a review right after their visit.",
    "contact_form": "I help businesses set up a simple contact form that routes inquiries straight to the right person.",
    "mobile_friendly": "I help businesses clean up their mobile experience so visitors don't bounce before booking or calling.",
    "is_slow": "I help businesses speed up their site so fewer visitors leave before it finishes loading.",
}

QUESTIONS = {
    "no_website": "How are new customers finding and reaching you right now?",
    "booking_system": "Out of curiosity, how much of your team's time would you say goes into scheduling calls each week?",
    "ai_receptionist": "How many calls would you guess go to voicemail after hours in a typical week?",
    "chatbot": "How do you currently handle questions that come in after you close?",
    "live_chat": "How does your team usually handle quick questions from the website right now?",
    "google_reviews_widget": "How do you currently ask customers for reviews, if at all?",
    "contact_form": "How do most new inquiries reach you today — phone, email, social?",
    "mobile_friendly": "Have you checked how the site feels on a phone recently?",
    "is_slow": "Have you noticed anything about how the site performs, especially on mobile?",
}

FALLBACK_OPENER = "I was looking at {business} online and wanted to reach out."
FALLBACK_BENEFIT = "I help {category} businesses fine-tune the automation around scheduling, follow-ups, and customer questions."
FALLBACK_QUESTION = "Would you be open to a quick chat about what's working well and where there might be room to save your team time?"

STRENGTH_LABELS = {
    "ssl": "Website has a valid SSL certificate",
    "mobile_friendly": "Website is mobile-friendly",
    "chatbot": "Already has a chatbot",
    "live_chat": "Already has live chat",
    "booking_system": "Already has online booking",
    "faq": "Has an FAQ section",
    "google_reviews_widget": "Already automates review requests",
}


def _first_name(full_name: str | None) -> str | None:
    if not full_name:
        return None
    cleaned = re.sub(r"^(Dr\.?|Mr\.?|Mrs\.?|Ms\.?)\s+", "", full_name.strip())
    return cleaned.split(" ")[0] if cleaned else None


def _pick_opener_code(pain_point_codes: set[str], google_rating: float | None) -> str | None:
    if "no_website" in pain_point_codes:
        return "no_website"
    for code in OUTREACH_PRIORITY:
        if code not in pain_point_codes:
            continue
        if code == "google_reviews_widget" and (not google_rating or google_rating < 4.0):
            continue
        return code
    return None


def build_strengths(technologies: dict, has_contact_form: bool, google_rating: float | None, google_reviews_count: int | None) -> list[str]:
    strengths = []
    for code, label in STRENGTH_LABELS.items():
        if technologies.get(code):
            strengths.append(label)
    if has_contact_form:
        strengths.append("Has an online contact form")
    if google_rating and google_rating >= 4.5 and (google_reviews_count or 0) >= 20:
        strengths.append(f"Strong Google reputation ({google_rating}★ from {google_reviews_count} reviews)")
    return strengths


def build_outreach_message(
    business_name: str,
    business_type: str,
    pain_points: list[dict],
    google_rating: float | None,
    google_reviews_count: int | None,
    contact_full_name: str | None,
) -> str:
    first_name = _first_name(contact_full_name)
    greeting = f"Hi {first_name}," if first_name else "Hi,"
    category = business_type.lower()
    pain_codes = {p["code"] for p in pain_points}

    code = _pick_opener_code(pain_codes, google_rating)
    if code:
        opener = OPENERS[code].format(business=business_name, rating=google_rating, reviews=google_reviews_count)
        benefit = BENEFITS[code].format(category=category)
        question = QUESTIONS[code]
    else:
        opener = FALLBACK_OPENER.format(business=business_name)
        benefit = FALLBACK_BENEFIT.format(category=category)
        question = FALLBACK_QUESTION

    return f"{greeting} {opener} {benefit} {question}"


def build_followup_message(business_name: str, contact_full_name: str | None) -> str:
    first_name = _first_name(contact_full_name)
    greeting = f"Hi {first_name}," if first_name else "Hi again,"
    return (
        f"{greeting} following up on my note about {business_name} — happy to put together a quick, "
        "free audit of what's working and what could be automated, no strings attached. "
        "Let me know if that'd be useful!"
    )


def build_discovery_questions(pain_points: list[dict]) -> list[str]:
    questions = [
        "Walk me through what happens today when a new customer reaches out to you for the first time.",
        "How does your team currently handle appointment scheduling?",
        "What's your process for following up with leads who don't book right away?",
    ]

    pain_codes = {p["code"] for p in pain_points}
    if "google_reviews_widget" in pain_codes:
        questions.append("How do you currently collect and respond to customer reviews?")
    if "ai_receptionist" in pain_codes or "chatbot" in pain_codes or "live_chat" in pain_codes:
        questions.append("What happens to calls or messages that come in after hours?")
    if "is_slow" in pain_codes or "mobile_friendly" in pain_codes:
        questions.append("Have you gotten any feedback on how the website feels to use, especially on mobile?")

    return questions[:5]
