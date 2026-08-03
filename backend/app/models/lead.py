import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("scrape_jobs.id"), index=True)

    business_name: Mapped[str] = mapped_column(String(300))
    business_type: Mapped[str] = mapped_column(String(120))
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(60), nullable=True)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)

    address: Mapped[str | None] = mapped_column(String(400), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    country: Mapped[str | None] = mapped_column(String(120), nullable=True)

    google_place_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    google_maps_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    google_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    google_reviews_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    opening_hours: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    facebook_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    instagram_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    linkedin_company_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    whatsapp_detected: Mapped[bool] = mapped_column(default=False)
    messenger_detected: Mapped[bool] = mapped_column(default=False)

    booking_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    has_contact_form: Mapped[bool] = mapped_column(default=False)
    has_staff_page: Mapped[bool] = mapped_column(default=False)
    has_about_page: Mapped[bool] = mapped_column(default=False)

    # Website analyzer results, e.g. {"live_chat": false, "ssl": true, "speed_ms": 812, ...}
    technologies: Mapped[dict] = mapped_column(JSON, default=dict)

    pain_points: Mapped[list] = mapped_column(JSON, default=list)
    recommended_services: Mapped[list] = mapped_column(JSON, default=list)
    lead_score: Mapped[int] = mapped_column(Integer, default=0)
    score_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    estimated_hours_saved_per_week: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Honest strengths (the inverse of pain_points) + generated outreach copy.
    # All rule-based from detected data — never fabricated claims or numbers.
    strengths: Mapped[list] = mapped_column(JSON, default=list)
    outreach_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    follow_up_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    discovery_questions: Mapped[list] = mapped_column(JSON, default=list)

    screenshot_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="new")  # new, reviewed, contacted, archived

    crawl_error: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    staff: Mapped[list["StaffMember"]] = relationship(back_populates="lead", cascade="all, delete-orphan")
