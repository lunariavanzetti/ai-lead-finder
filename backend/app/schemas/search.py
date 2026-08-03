from pydantic import BaseModel, Field


class AdvancedSettings(BaseModel):
    concurrent_workers: int = Field(default=6, ge=1, le=20)
    timeout_seconds: int = Field(default=15, ge=5, le=60)
    retries: int = Field(default=2, ge=0, le=5)
    delay_seconds: float = Field(default=2.5, ge=0.5, le=15)
    export_folder: str | None = None
    proxy_url: str | None = None
    rotate_user_agent: bool = True
    capture_screenshots: bool = False  # off by default — launches a headless browser per lead, slow at scale


class RequiredInformation(BaseModel):
    business_name: bool = True
    website: bool = True
    phone: bool = True
    email: bool = True
    address: bool = True
    google_rating: bool = True
    google_reviews_count: bool = True
    opening_hours: bool = False
    facebook: bool = True
    instagram: bool = True
    linkedin_company_page: bool = True
    booking_link: bool = True
    contact_form: bool = True
    staff_page: bool = True
    about_page: bool = False
    # Looks up the primary decision-maker's public LinkedIn profile via the
    # official Google Custom Search API when the business's own site doesn't
    # already link to one. Only attaches a result on a confident name match.
    decision_maker_linkedin: bool = True


class SearchRequest(BaseModel):
    business_type: str = Field(..., min_length=2, max_length=120)
    country: str
    state: str | None = None
    city: str
    radius_km: int = Field(default=30, ge=1, le=200)
    max_results: int = Field(default=100, ge=1, le=1000)

    decision_maker_titles: list[str] = Field(
        default_factory=lambda: [
            "Owner", "Founder", "CEO", "President", "Practice Manager",
            "Office Manager", "Managing Director", "Director", "Manager",
            "Partner", "Managing Partner", "Clinic Manager",
        ]
    )
    required_information: RequiredInformation = Field(default_factory=RequiredInformation)
    advanced_settings: AdvancedSettings = Field(default_factory=AdvancedSettings)
