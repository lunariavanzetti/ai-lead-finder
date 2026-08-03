from app.extractors.staff_extractor import ExtractedStaffMember

# Lower rank == higher priority. Titles are matched as case-insensitive substrings.
PRIORITY_RANK = {
    "owner": 0, "founder": 0, "ceo": 0, "chief executive": 0,
    "president": 1, "managing partner": 1, "managing director": 1,
    "partner": 2, "practice manager": 2, "clinic manager": 2, "office manager": 2,
    "director": 3,
    "manager": 4,
    "supervisor": 6,
    "receptionist": 8, "assistant": 8, "coordinator": 8,
    "intern": 9,
}
DEFAULT_RANK = 5


def _rank_for_title(title: str | None) -> int:
    if not title:
        return DEFAULT_RANK
    lowered = title.lower()
    best = DEFAULT_RANK
    for keyword, rank in PRIORITY_RANK.items():
        if keyword in lowered and rank < best:
            best = rank
    return best


def rank_staff(staff: list[ExtractedStaffMember], selected_decision_maker_titles: list[str]) -> list[dict]:
    selected_lower = [t.lower() for t in selected_decision_maker_titles]

    ranked = []
    for member in staff:
        rank = _rank_for_title(member.title)
        title_lower = (member.title or "").lower()
        is_decision_maker = any(sel in title_lower for sel in selected_lower) if title_lower else False

        ranked.append(
            {
                "full_name": member.full_name,
                "title": member.title,
                "email": member.email,
                "linkedin_url": member.linkedin_url,
                "priority_rank": rank,
                "is_decision_maker": is_decision_maker,
            }
        )

    ranked.sort(key=lambda m: m["priority_rank"])
    return ranked


def primary_contact(ranked_staff: list[dict]) -> dict | None:
    decision_makers = [m for m in ranked_staff if m["is_decision_maker"]]
    pool = decision_makers or ranked_staff
    return pool[0] if pool else None
