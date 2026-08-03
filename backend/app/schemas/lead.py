from datetime import datetime

from pydantic import BaseModel


class StaffMemberOut(BaseModel):
    id: str
    full_name: str
    title: str | None
    email: str | None
    linkedin_url: str | None
    is_decision_maker: bool
    priority_rank: int

    model_config = {"from_attributes": True}


class LeadListItem(BaseModel):
    id: str
    lead_score: int
    business_name: str
    business_type: str
    website: str | None
    phone: str | None
    email: str | None
    city: str | None
    state: str | None
    country: str | None
    google_rating: float | None
    google_reviews_count: int | None
    status: str
    owner_name: str | None = None
    owner_title: str | None = None
    pain_points: list = []
    recommended_services: list = []

    model_config = {"from_attributes": True}


class LeadDetail(LeadListItem):
    address: str | None
    google_maps_url: str | None
    opening_hours: dict | None
    facebook_url: str | None
    instagram_url: str | None
    linkedin_company_url: str | None
    whatsapp_detected: bool
    messenger_detected: bool
    booking_link: str | None
    has_contact_form: bool
    has_staff_page: bool
    has_about_page: bool
    technologies: dict
    pain_points: list
    recommended_services: list
    score_breakdown: dict
    estimated_hours_saved_per_week: float | None
    strengths: list
    outreach_message: str | None
    follow_up_message: str | None
    discovery_questions: list
    screenshot_path: str | None
    crawl_error: str | None
    staff: list[StaffMemberOut]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadListResponse(BaseModel):
    items: list[LeadListItem]
    total: int
    page: int
    page_size: int


class LeadStatusUpdate(BaseModel):
    status: str
