from datetime import datetime

from pydantic import BaseModel

from app.models.job import JobStatus


class JobCreatedResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobProgress(BaseModel):
    job_id: str
    status: JobStatus
    businesses_found: int
    businesses_analyzed: int
    emails_found: int
    websites_scanned: int
    max_results: int
    estimated_remaining_seconds: float | None = None
    current_business: str | None = None
    current_step: str | None = None
    message: str | None = None

    model_config = {"from_attributes": True}


class JobSummary(BaseModel):
    id: str
    status: JobStatus
    params: dict
    businesses_found: int
    businesses_analyzed: int
    emails_found: int
    websites_scanned: int
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

    model_config = {"from_attributes": True}
