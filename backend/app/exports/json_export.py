import json
from pathlib import Path

from app.models.lead import Lead


def _staff_to_dict(staff) -> dict:
    return {
        "full_name": staff.full_name,
        "title": staff.title,
        "email": staff.email,
        "linkedin_url": staff.linkedin_url,
        "is_decision_maker": staff.is_decision_maker,
        "priority_rank": staff.priority_rank,
    }


def lead_to_full_dict(lead: Lead) -> dict:
    return {
        "id": lead.id,
        "lead_score": lead.lead_score,
        "score_breakdown": lead.score_breakdown,
        "business_name": lead.business_name,
        "business_type": lead.business_type,
        "website": lead.website,
        "phone": lead.phone,
        "email": lead.email,
        "address": lead.address,
        "city": lead.city,
        "state": lead.state,
        "country": lead.country,
        "google_place_id": lead.google_place_id,
        "google_maps_url": lead.google_maps_url,
        "google_rating": lead.google_rating,
        "google_reviews_count": lead.google_reviews_count,
        "opening_hours": lead.opening_hours,
        "facebook_url": lead.facebook_url,
        "instagram_url": lead.instagram_url,
        "linkedin_company_url": lead.linkedin_company_url,
        "whatsapp_detected": lead.whatsapp_detected,
        "messenger_detected": lead.messenger_detected,
        "booking_link": lead.booking_link,
        "has_contact_form": lead.has_contact_form,
        "has_staff_page": lead.has_staff_page,
        "has_about_page": lead.has_about_page,
        "technologies": lead.technologies,
        "pain_points": lead.pain_points,
        "strengths": lead.strengths,
        "recommended_services": lead.recommended_services,
        "estimated_hours_saved_per_week": lead.estimated_hours_saved_per_week,
        "outreach_message": lead.outreach_message,
        "follow_up_message": lead.follow_up_message,
        "discovery_questions": lead.discovery_questions,
        "screenshot_path": lead.screenshot_path,
        "status": lead.status,
        "staff": [_staff_to_dict(s) for s in lead.staff],
    }


def export_json(leads: list[Lead], out_path: Path) -> Path:
    data = [lead_to_full_dict(lead) for lead in leads]
    out_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return out_path
