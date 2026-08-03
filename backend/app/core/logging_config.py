import sys

from loguru import logger

from app.core.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    logger.remove()
    logger.add(sys.stderr, level="INFO", colorize=True)
    logger.add(
        settings.logs_dir / "app_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="14 days",
        level="DEBUG",
        enqueue=True,
    )


def job_log_sink(job_id: str):
    """Returns a logger bound to a specific job so each run's log lines can be filtered/streamed."""
    settings = get_settings()
    log_path = settings.logs_dir / f"job_{job_id}.log"
    logger.add(log_path, filter=lambda record: record["extra"].get("job_id") == job_id, level="DEBUG")
    return logger.bind(job_id=job_id)
