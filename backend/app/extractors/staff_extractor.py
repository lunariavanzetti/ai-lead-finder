import re
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag

NAME_PATTERN = re.compile(r"^(Dr\.?\s+)?[A-Z][a-zA-Z'.-]+(\s+[A-Z][a-zA-Z'.-]+){1,3}$")
NON_NAME_HEADINGS = {
    "our team", "meet the team", "meet our team", "our staff", "our doctors",
    "leadership", "who we are", "about us", "get in touch", "contact us",
}
CONTAINER_TAGS = ["div", "li", "article", "section"]
HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]

TITLE_HINT_CLASS = re.compile(r"(title|role|position|job)", re.I)

# Section headings like "Advanced Training", "Our Core Values", or "Quick
# Links" are title-case and 2-4 words, so they pass NAME_PATTERN — this list
# rejects a candidate if ANY word in it is a common heading/marketing word
# rather than something that could plausibly be part of a person's name.
# False negatives (a real name gets dropped) are the acceptable failure mode
# here, not false positives (a heading gets shown to the user as a person).
NON_NAME_WORDS = {
    "our", "the", "we", "us", "meet", "about", "quick", "links", "link", "value", "values",
    "core", "story", "stories", "training", "trainings", "advanced", "recommendation",
    "recommendations", "personalized", "payment", "method", "methods", "saved", "use",
    "overview", "service", "services", "provider", "providers", "team", "staff", "family",
    "families", "smile", "smiles", "dental", "dentistry", "dentist", "dentists", "practice",
    "clinic", "care", "health", "welcome", "learn", "more", "why", "what", "how", "choose",
    "faq", "faqs", "blog", "news", "location", "locations", "hour", "hours", "appointment",
    "appointments", "booking", "book", "schedule", "contact", "review", "reviews",
    "testimonial", "testimonials", "gallery", "before", "after", "financing", "insurance",
    "patient", "patients", "new", "emergency", "cosmetic", "orthodontics", "orthodontist",
    "pediatric", "kids", "children", "child", "general", "restorative", "porcelain",
    "registered", "assistant", "assistants", "coordinator", "specialist", "specialists",
    "plan", "plans", "set", "sets", "apart", "mission", "vision", "difference", "commitment",
    "promise", "philosophy", "procedure", "procedures", "difference",
}

# Stripped from the front of a heading before validation — "Meet Dr. Smith"
# should be evaluated (and displayed) as "Dr. Smith", not rejected outright
# because "Meet" doesn't look like part of a name.
FILLER_PREFIX = re.compile(
    r"^(Meet\s+|Introducing\s+|Say Hello to\s+|Get to Know\s+)", re.I
)

# A blocklist alone is whack-a-mole — every site invents new marketing
# phrases ("Get Started Today", "Root Canal Treatment", "Affiliate Success")
# that happen to be title-case 2-4 word phrases. So a candidate that clears
# the blocklist above still needs POSITIVE evidence it's a real person:
# a job-title keyword nearby, a personal email, a LinkedIn profile link, a
# staff-card-ish container class, or a "Dr." prefix on the name itself.
TITLE_KEYWORDS = re.compile(
    r"\b(dds|dmd|rdh|dr|doctor|owner|founder|manager|director|hygienist|"
    r"assistant|coordinator|dentist|orthodontist|periodontist|endodontist|"
    r"prosthodontist|president|partner|receptionist|technician)\b",
    re.I,
)
CONTAINER_HINT_CLASS = re.compile(r"(team|staff|provider|doctor|bio|person|employee)", re.I)


def _has_supporting_evidence(heading: Tag, name_text: str, title: str | None, email: str | None, linkedin: str | None) -> bool:
    if email or linkedin:
        return True
    if name_text.lower().startswith("dr"):
        return True
    if title and TITLE_KEYWORDS.search(title):
        return True
    parent = heading.find_parent(CONTAINER_TAGS) or heading.parent
    if parent is not None:
        for ancestor in [parent, *parent.find_parents(CONTAINER_TAGS)][:3]:
            class_attr = " ".join(ancestor.get("class", [])) + " " + (ancestor.get("id") or "")
            if CONTAINER_HINT_CLASS.search(class_attr):
                return True
    return False


@dataclass
class ExtractedStaffMember:
    full_name: str
    title: str | None
    email: str | None
    linkedin_url: str | None


def _looks_like_name(text: str) -> bool:
    text = text.strip()
    if len(text) < 4 or len(text) > 50:
        return False
    if text.lower() in NON_NAME_HEADINGS:
        return False
    if not NAME_PATTERN.match(text):
        return False
    words = {w.strip(".").lower() for w in text.split()}
    if words & NON_NAME_WORDS:
        return False
    return True


def _find_title_near(heading: Tag) -> str | None:
    # Prefer an explicitly-classed title/role element within the same card.
    parent = heading.find_parent(CONTAINER_TAGS) or heading.parent
    if parent:
        title_el = parent.find(class_=TITLE_HINT_CLASS)
        if title_el and title_el is not heading:
            text = title_el.get_text(" ", strip=True)
            if text and len(text) < 80:
                return text

    # Otherwise fall back to the next short text sibling.
    sibling = heading.find_next_sibling()
    while sibling and isinstance(sibling, Tag):
        text = sibling.get_text(" ", strip=True)
        if text and len(text) < 80:
            return text
        sibling = sibling.find_next_sibling()
    return None


def _find_email_near(heading: Tag) -> str | None:
    parent = heading.find_parent(CONTAINER_TAGS) or heading.parent
    if not parent:
        return None
    mailto = parent.find("a", href=re.compile(r"^mailto:", re.I))
    if mailto:
        return mailto["href"][7:].split("?")[0].strip()
    return None


def _find_linkedin_near(heading: Tag) -> str | None:
    parent = heading.find_parent(CONTAINER_TAGS) or heading.parent
    if not parent:
        return None
    link = parent.find("a", href=re.compile(r"linkedin\.com/in/", re.I))
    return link["href"] if link else None


def extract_staff_members(html: str) -> list[ExtractedStaffMember]:
    soup = BeautifulSoup(html, "lxml")
    results: list[ExtractedStaffMember] = []
    seen_names: set[str] = set()

    for heading in soup.find_all(HEADING_TAGS):
        raw_text = heading.get_text(" ", strip=True)
        text = FILLER_PREFIX.sub("", raw_text).strip()
        if not _looks_like_name(text):
            continue
        if text.lower() in seen_names:
            continue

        title = _find_title_near(heading)
        email = _find_email_near(heading)
        linkedin = _find_linkedin_near(heading)
        if not _has_supporting_evidence(heading, text, title, email, linkedin):
            continue

        seen_names.add(text.lower())
        results.append(
            ExtractedStaffMember(full_name=text, title=title, email=email, linkedin_url=linkedin)
        )

    return results
