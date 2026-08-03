from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.lead import Lead


async def fetch_leads(
    session: AsyncSession, job_id: str | None = None, lead_ids: list[str] | None = None
) -> list[Lead]:
    stmt = select(Lead).options(selectinload(Lead.staff)).order_by(Lead.lead_score.desc())
    if lead_ids:
        stmt = stmt.where(Lead.id.in_(lead_ids))
    elif job_id:
        stmt = stmt.where(Lead.job_id == job_id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


def primary_contact_for(lead: Lead):
    decision_makers = [s for s in lead.staff if s.is_decision_maker]
    if decision_makers:
        return sorted(decision_makers, key=lambda s: s.priority_rank)[0]
    return lead.staff[0] if lead.staff else None


def lead_to_flat_dict(lead: Lead) -> dict:
    contact = primary_contact_for(lead)
    return {
        "Lead Score": lead.lead_score,
        "Business Name": lead.business_name,
        "Business Type": lead.business_type,
        "Website": lead.website or "",
        "Phone": lead.phone or "",
        "Email": lead.email or "",
        "Decision Maker": contact.full_name if contact else "",
        "Decision Maker Title": contact.title if contact else "",
        "Decision Maker Email": contact.email if contact else "",
        "Decision Maker LinkedIn": contact.linkedin_url if contact else "",
        "Address": lead.address or "",
        "City": lead.city or "",
        "State": lead.state or "",
        "Country": lead.country or "",
        "Google Rating": lead.google_rating,
        "Google Reviews": lead.google_reviews_count,
        "Facebook": lead.facebook_url or "",
        "Instagram": lead.instagram_url or "",
        "LinkedIn Company Page": lead.linkedin_company_url or "",
        "Booking Link": lead.booking_link or "",
        "Pain Points": "; ".join(p.get("label", "") for p in lead.pain_points),
        "Strengths": "; ".join(lead.strengths),
        "Recommended Services": "; ".join(lead.recommended_services),
        "Estimated Hours Saved/Week": lead.estimated_hours_saved_per_week,
        "Outreach Message": lead.outreach_message or "",
        "Follow-Up Message": lead.follow_up_message or "",
        "Discovery Call Questions": " | ".join(lead.discovery_questions),
        "Status": lead.status,
    }
