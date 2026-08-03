from collections import Counter

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session
from app.models.job import ScrapeJob
from app.models.lead import Lead

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


class DashboardStats(BaseModel):
    total_leads: int
    total_jobs: int
    average_lead_score: float
    high_priority_leads: int  # score >= 70
    top_pain_points: list[dict]
    recent_jobs: list[dict]


@router.get("", response_model=DashboardStats)
async def get_dashboard_stats(session: AsyncSession = Depends(db_session)):
    total_leads = (await session.execute(select(func.count()).select_from(Lead))).scalar_one()
    total_jobs = (await session.execute(select(func.count()).select_from(ScrapeJob))).scalar_one()
    avg_score = (await session.execute(select(func.avg(Lead.lead_score)))).scalar_one() or 0
    high_priority = (
        await session.execute(select(func.count()).select_from(Lead).where(Lead.lead_score >= 70))
    ).scalar_one()

    all_leads = (await session.execute(select(Lead.pain_points))).scalars().all()
    counter = Counter()
    for pain_points in all_leads:
        for point in pain_points or []:
            counter[point.get("label", "Unknown")] += 1
    top_pain_points = [{"label": label, "count": count} for label, count in counter.most_common(6)]

    recent_jobs_result = (
        await session.execute(select(ScrapeJob).order_by(ScrapeJob.created_at.desc()).limit(5))
    ).scalars().all()
    recent_jobs = [
        {
            "id": job.id,
            "status": job.status.value if hasattr(job.status, "value") else job.status,
            "business_type": (job.params or {}).get("business_type"),
            "city": (job.params or {}).get("city"),
            "businesses_analyzed": job.businesses_analyzed,
            "created_at": job.created_at.isoformat() if job.created_at else None,
        }
        for job in recent_jobs_result
    ]

    return DashboardStats(
        total_leads=total_leads,
        total_jobs=total_jobs,
        average_lead_score=round(float(avg_score), 1),
        high_priority_leads=high_priority,
        top_pain_points=top_pain_points,
        recent_jobs=recent_jobs,
    )
