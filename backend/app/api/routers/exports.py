import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from starlette.responses import FileResponse

from app.api.deps import db_session
from app.core.config import get_settings
from app.exports.common import fetch_leads
from app.exports.csv_export import export_csv
from app.exports.json_export import export_json
from app.exports.pdf_audit import generate_audit_pdf
from app.exports.sqlite_export import export_sqlite
from app.exports.xlsx_export import export_xlsx
from app.models.lead import Lead

router = APIRouter(prefix="/api/exports", tags=["exports"])

MEDIA_TYPES = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "json": "application/json",
    "sqlite": "application/x-sqlite3",
}


class ExportRequest(BaseModel):
    format: str  # csv | xlsx | json | sqlite
    job_id: str | None = None
    lead_ids: list[str] | None = None


@router.post("")
async def export_leads(request: ExportRequest, session: AsyncSession = Depends(db_session)):
    if request.format not in MEDIA_TYPES:
        raise HTTPException(400, f"Unsupported format: {request.format}")

    leads = await fetch_leads(session, job_id=request.job_id, lead_ids=request.lead_ids)
    if not leads:
        raise HTTPException(404, "No leads matched this export request")

    settings = get_settings()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"leads_export_{timestamp}.{request.format}"
    out_path = settings.exports_dir / filename

    if request.format == "csv":
        export_csv(leads, out_path)
    elif request.format == "xlsx":
        export_xlsx(leads, out_path)
    elif request.format == "json":
        export_json(leads, out_path)
    elif request.format == "sqlite":
        export_sqlite(leads, out_path)

    return FileResponse(out_path, media_type=MEDIA_TYPES[request.format], filename=filename)


@router.post("/audit/{lead_id}")
async def export_audit_pdf(lead_id: str, session: AsyncSession = Depends(db_session)):
    stmt = select(Lead).options(selectinload(Lead.staff)).where(Lead.id == lead_id)
    lead = (await session.execute(stmt)).scalar_one_or_none()
    if not lead:
        raise HTTPException(404, "Lead not found")

    settings = get_settings()
    filename = f"audit_{lead.business_name.replace(' ', '_')[:40]}_{uuid.uuid4().hex[:6]}.pdf"
    out_path = settings.exports_dir / filename
    generate_audit_pdf(lead, out_path)

    return FileResponse(out_path, media_type="application/pdf", filename=filename)
