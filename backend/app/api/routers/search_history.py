from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import db_session
from app.models.search_history import SearchHistoryEntry

router = APIRouter(prefix="/api/search-history", tags=["search-history"])


class SearchHistoryItem(BaseModel):
    id: str
    job_id: str
    business_type: str
    location_label: str
    params: dict
    result_count: int

    model_config = {"from_attributes": True}


@router.get("", response_model=list[SearchHistoryItem])
async def list_search_history(session: AsyncSession = Depends(db_session), limit: int = 50):
    stmt = select(SearchHistoryEntry).order_by(SearchHistoryEntry.created_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())
