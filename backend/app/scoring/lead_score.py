"""Lead score = how good an automation-sales opportunity this business is,
0-100. Higher means MORE gaps (more to sell) combined with being reachable
(so the gaps are actually actionable). This mirrors how the score is used
downstream: a 90+ lead is a business with lots of missing automation AND a
name/email/phone to reach out to — not a "quality" score in the sense of a
well-run business.

Weights are grouped in one place so they're easy to retune without touching
the scoring logic itself.
"""

SEVERITY_WEIGHTS = {"high": 9, "medium": 5, "low": 2}
MAX_PAIN_POINT_COMPONENT = 70

CONTACTABILITY_WEIGHTS = {"has_email": 8, "has_phone": 7}
DECISION_MAKER_WEIGHT = 15


def calculate_lead_score(
    pain_points: list[dict],
    has_decision_maker: bool,
    has_email: bool,
    has_phone: bool,
) -> tuple[int, dict]:
    pain_point_component = min(
        sum(SEVERITY_WEIGHTS.get(p["severity"], 2) for p in pain_points),
        MAX_PAIN_POINT_COMPONENT,
    )

    contactability_component = (
        (CONTACTABILITY_WEIGHTS["has_email"] if has_email else 0)
        + (CONTACTABILITY_WEIGHTS["has_phone"] if has_phone else 0)
    )

    decision_maker_component = DECISION_MAKER_WEIGHT if has_decision_maker else 0

    total = pain_point_component + contactability_component + decision_maker_component
    total = max(0, min(100, total))

    breakdown = {
        "pain_point_component": pain_point_component,
        "contactability_component": contactability_component,
        "decision_maker_component": decision_maker_component,
        "max_pain_point_component": MAX_PAIN_POINT_COMPONENT,
        "total": total,
    }
    return total, breakdown
