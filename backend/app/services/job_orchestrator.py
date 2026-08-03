import asyncio
import time
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse

from loguru import logger
from sqlalchemy import update

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.discovery.google_custom_search import GoogleCustomSearchClient
from app.discovery.google_places import GooglePlacesClient
from app.models.job import JobStatus, ScrapeJob
from app.models.lead import Lead
from app.models.search_history import SearchHistoryEntry
from app.models.staff import StaffMember
from app.schemas.search import SearchRequest
from app.scrapers.fetcher import CrawlConfig
from app.services.job_control import job_control
from app.services.lead_pipeline import build_error_result, process_business
from app.services.progress_bus import progress_bus


async def _publish(job_id: str, **event) -> None:
    await progress_bus.publish(job_id, event)


async def _update_job(job_id: str, **fields) -> None:
    async with AsyncSessionLocal() as session:
        await session.execute(update(ScrapeJob).where(ScrapeJob.id == job_id).values(**fields))
        await session.commit()


async def create_job(request: SearchRequest) -> str:
    job_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        job = ScrapeJob(id=job_id, status=JobStatus.PENDING, params=request.model_dump())
        session.add(job)
        await session.commit()
    return job_id


async def run_job(job_id: str, request: SearchRequest) -> None:
    job_control.register(job_id)
    settings = get_settings()

    await _update_job(job_id, status=JobStatus.RUNNING, started_at=datetime.now(timezone.utc))
    await _publish(job_id, type="status", status="running", message="Searching for businesses...")

    try:
        discovered = await _discover_businesses(request)
        await _update_job(job_id, businesses_found=len(discovered))
        await _publish(job_id, type="discovery_complete", businesses_found=len(discovered))

        if not discovered:
            await _finish_job(job_id, JobStatus.COMPLETED)
            return

        crawl_config = CrawlConfig(
            timeout_seconds=request.advanced_settings.timeout_seconds,
            retries=request.advanced_settings.retries,
            delay_seconds=request.advanced_settings.delay_seconds,
            proxy_url=request.advanced_settings.proxy_url,
            rotate_user_agent=request.advanced_settings.rotate_user_agent,
            respect_robots=settings.respect_robots_txt,
        )

        semaphore = asyncio.Semaphore(request.advanced_settings.concurrent_workers)
        counters = {"analyzed": 0, "emails": 0, "websites_scanned": 0}
        counters_lock = asyncio.Lock()
        durations: list[float] = []

        async def process_one(business):
            async with semaphore:
                if job_control.is_cancelled(job_id):
                    return
                await job_control.wait_if_paused(job_id)
                if job_control.is_cancelled(job_id):
                    return

                await _publish(
                    job_id, type="progress", current_business=business.business_name,
                    current_step="Crawling website..." if business.website else "No website — scoring as-is...",
                )

                started = time.monotonic()
                screenshot_path = None
                if request.advanced_settings.capture_screenshots and business.website:
                    domain = urlparse(business.website).netloc.replace(".", "_")
                    screenshot_path = str(settings.screenshots_dir / f"{domain}_{uuid.uuid4().hex[:8]}.png")

                try:
                    lead_data = await process_business(
                        business=business,
                        business_type=request.business_type,
                        decision_maker_titles=request.decision_maker_titles,
                        crawl_config=crawl_config,
                        exclude_personal_data_eu=settings.exclude_personal_data_eu,
                        capture_screenshot=request.advanced_settings.capture_screenshots,
                        screenshot_path=screenshot_path,
                        find_decision_maker_linkedin=request.required_information.decision_maker_linkedin,
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.exception(f"[job {job_id}] failed processing {business.business_name}")
                    lead_data = build_error_result(business, request.business_type, str(exc))

                elapsed = time.monotonic() - started

                async with counters_lock:
                    durations.append(elapsed)
                    counters["analyzed"] += 1
                    if lead_data.get("website"):
                        counters["websites_scanned"] += 1
                    if lead_data.get("email"):
                        counters["emails"] += 1

                    avg_duration = sum(durations) / len(durations)
                    remaining_businesses = len(discovered) - counters["analyzed"]
                    estimated_remaining = (
                        remaining_businesses * avg_duration / max(request.advanced_settings.concurrent_workers, 1)
                    )
                    snapshot = dict(counters)

                await _persist_lead(job_id, lead_data)

                await _update_job(
                    job_id,
                    businesses_analyzed=snapshot["analyzed"],
                    emails_found=snapshot["emails"],
                    websites_scanned=snapshot["websites_scanned"],
                    estimated_remaining_seconds=estimated_remaining,
                )
                await _publish(
                    job_id, type="progress", current_business=business.business_name, current_step="done",
                    businesses_analyzed=snapshot["analyzed"], emails_found=snapshot["emails"],
                    websites_scanned=snapshot["websites_scanned"], estimated_remaining_seconds=estimated_remaining,
                    lead_score=lead_data.get("lead_score"),
                )

        await asyncio.gather(*(process_one(b) for b in discovered))

        cancelled = job_control.is_cancelled(job_id)
        await _record_search_history(job_id, request, counters["analyzed"])
        await _finish_job(job_id, JobStatus.CANCELLED if cancelled else JobStatus.COMPLETED)

    except Exception as exc:  # noqa: BLE001
        logger.exception(f"Job {job_id} failed")
        await _finish_job(job_id, JobStatus.FAILED, error_message=str(exc))
    finally:
        job_control.cleanup(job_id)


async def _discover_businesses(request: SearchRequest) -> list:
    places_client = GooglePlacesClient()
    discovered = []
    try:
        discovered = await places_client.search_businesses(
            business_type=request.business_type,
            city=request.city,
            state=request.state,
            country=request.country,
            radius_km=request.radius_km,
            max_results=request.max_results,
        )
    except RuntimeError as exc:
        logger.error(f"Places discovery unavailable: {exc}")

    if len(discovered) < request.max_results:
        custom_client = GoogleCustomSearchClient()
        existing_domains = {urlparse(d.website).netloc.replace("www.", "") for d in discovered if d.website}
        supplemental = await custom_client.search_business_websites(
            business_type=request.business_type,
            city=request.city,
            state=request.state,
            country=request.country,
            max_results=request.max_results - len(discovered),
            exclude_domains=existing_domains,
        )
        discovered.extend(supplemental)

    return discovered[: request.max_results]


async def _persist_lead(job_id: str, lead_data: dict) -> None:
    staff_list = lead_data.pop("staff", [])
    async with AsyncSessionLocal() as session:
        lead = Lead(job_id=job_id, **{k: v for k, v in lead_data.items() if k in Lead.__table__.columns.keys()})
        session.add(lead)
        await session.flush()

        for member in staff_list:
            session.add(
                StaffMember(
                    lead_id=lead.id,
                    full_name=member["full_name"],
                    title=member.get("title"),
                    email=member.get("email"),
                    linkedin_url=member.get("linkedin_url"),
                    is_decision_maker=member.get("is_decision_maker", False),
                    priority_rank=member.get("priority_rank", 99),
                )
            )
        await session.commit()


async def _record_search_history(job_id: str, request: SearchRequest, result_count: int) -> None:
    location_label = ", ".join(filter(None, [request.city, request.state, request.country]))
    async with AsyncSessionLocal() as session:
        session.add(
            SearchHistoryEntry(
                job_id=job_id,
                business_type=request.business_type,
                location_label=location_label,
                params=request.model_dump(),
                result_count=result_count,
            )
        )
        await session.commit()


async def _finish_job(job_id: str, status: JobStatus, error_message: str | None = None) -> None:
    fields = {"status": status, "finished_at": datetime.now(timezone.utc)}
    if error_message:
        fields["error_message"] = error_message
    await _update_job(job_id, **fields)
    await _publish(job_id, type="status", status=status.value, message=error_message)
