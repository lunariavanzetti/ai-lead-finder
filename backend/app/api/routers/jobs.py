import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.api.deps import db_session
from app.db.session import AsyncSessionLocal
from app.models.job import ScrapeJob
from app.schemas.job import JobCreatedResponse, JobSummary
from app.schemas.search import SearchRequest
from app.services.job_control import job_control
from app.services.job_orchestrator import create_job, run_job
from app.services.progress_bus import progress_bus

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobCreatedResponse)
async def start_job(request: SearchRequest):
    job_id = await create_job(request)
    asyncio.create_task(run_job(job_id, request))
    return JobCreatedResponse(job_id=job_id, status="pending")


@router.get("", response_model=list[JobSummary])
async def list_jobs(session: AsyncSession = Depends(db_session), limit: int = 20):
    stmt = select(ScrapeJob).order_by(ScrapeJob.created_at.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get("/{job_id}", response_model=JobSummary)
async def get_job(job_id: str, session: AsyncSession = Depends(db_session)):
    job = await session.get(ScrapeJob, job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


TERMINAL_STATUSES = ("completed", "cancelled", "failed")


@router.get("/{job_id}/stream")
async def stream_job_progress(job_id: str):
    # Subscribe before doing anything else so no event published after this
    # point can be missed — the queue buffers everything until we read it.
    queue = progress_bus.subscribe(job_id)

    async def event_generator():
        try:
            # A fast/instant job (e.g. discovery returns zero results) can
            # finish before the client's EventSource even connects. Snapshot
            # current DB state up front so the UI never hangs on "pending"
            # for a job that already finished.
            async with AsyncSessionLocal() as session:
                job = await session.get(ScrapeJob, job_id)

            if job is None:
                return

            status_value = job.status.value if hasattr(job.status, "value") else job.status
            snapshot = {
                "type": "progress",
                "status": status_value,
                "businesses_found": job.businesses_found,
                "businesses_analyzed": job.businesses_analyzed,
                "emails_found": job.emails_found,
                "websites_scanned": job.websites_scanned,
                "estimated_remaining_seconds": job.estimated_remaining_seconds,
            }
            yield f"data: {json.dumps(snapshot)}\n\n"

            if status_value in TERMINAL_STATUSES:
                yield f"data: {json.dumps({'type': 'status', 'status': status_value, 'message': job.error_message})}\n\n"
                return

            while True:
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") == "status" and event.get("status") in TERMINAL_STATUSES:
                    break
        finally:
            progress_bus.unsubscribe(job_id, queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/{job_id}/pause")
async def pause_job(job_id: str):
    if not job_control.pause(job_id):
        raise HTTPException(404, "Job not running")
    return {"status": "paused"}


@router.post("/{job_id}/resume")
async def resume_job(job_id: str):
    if not job_control.resume(job_id):
        raise HTTPException(404, "Job not running")
    return {"status": "resumed"}


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    if not job_control.cancel(job_id):
        raise HTTPException(404, "Job not running")
    return {"status": "cancelling"}
