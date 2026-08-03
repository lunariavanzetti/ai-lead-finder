from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import db_session
from app.exports.common import primary_contact_for
from app.models.lead import Lead
from app.schemas.lead import LeadDetail, LeadListItem, LeadListResponse, LeadStatusUpdate

router = APIRouter(prefix="/api/leads", tags=["leads"])

SORTABLE_COLUMNS = {
    "lead_score": Lead.lead_score,
    "business_name": Lead.business_name,
    "google_rating": Lead.google_rating,
    "created_at": Lead.created_at,
}


@router.get("", response_model=LeadListResponse)
async def list_leads(
    session: AsyncSession = Depends(db_session),
    job_id: str | None = None,
    search: str | None = None,
    business_type: str | None = None,
    city: str | None = None,
    status: str | None = None,
    min_score: int | None = None,
    sort_by: str = "lead_score",
    sort_dir: str = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=200),
):
    stmt = select(Lead).options(selectinload(Lead.staff))
    count_stmt = select(func.count()).select_from(Lead)

    filters = []
    if job_id:
        filters.append(Lead.job_id == job_id)
    if business_type:
        filters.append(Lead.business_type.ilike(f"%{business_type}%"))
    if city:
        filters.append(Lead.city.ilike(f"%{city}%"))
    if status:
        filters.append(Lead.status == status)
    if min_score is not None:
        filters.append(Lead.lead_score >= min_score)
    if search:
        like = f"%{search}%"
        filters.append(
            or_(Lead.business_name.ilike(like), Lead.email.ilike(like), Lead.website.ilike(like))
        )

    for f in filters:
        stmt = stmt.where(f)
        count_stmt = count_stmt.where(f)

    sort_column = SORTABLE_COLUMNS.get(sort_by, Lead.lead_score)
    stmt = stmt.order_by(desc(sort_column) if sort_dir == "desc" else asc(sort_column))
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)

    total = (await session.execute(count_stmt)).scalar_one()
    items = (await session.execute(stmt)).scalars().all()

    def to_list_item(lead: Lead) -> LeadListItem:
        contact = primary_contact_for(lead)
        item = LeadListItem.model_validate(lead)
        item.owner_name = contact.full_name if contact else None
        item.owner_title = contact.title if contact else None
        return item

    return LeadListResponse(
        items=[to_list_item(lead) for lead in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{lead_id}", response_model=LeadDetail)
async def get_lead(lead_id: str, session: AsyncSession = Depends(db_session)):
    stmt = select(Lead).options(selectinload(Lead.staff)).where(Lead.id == lead_id)
    lead = (await session.execute(stmt)).scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadDetail)
async def update_lead_status(lead_id: str, update: LeadStatusUpdate, session: AsyncSession = Depends(db_session)):
    stmt = select(Lead).options(selectinload(Lead.staff)).where(Lead.id == lead_id)
    lead = (await session.execute(stmt)).scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Lead not found")
    lead.status = update.status
    await session.commit()
    await session.refresh(lead)
    return lead
