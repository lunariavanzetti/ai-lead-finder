from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Lead Finder"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/lead_finder.db"

    google_places_api_key: str = ""
    google_custom_search_api_key: str = ""
    google_custom_search_cx: str = ""

    # Crawling defaults (overridable per-job from the UI's Advanced Settings)
    default_concurrent_workers: int = 6
    default_timeout_seconds: int = 15
    default_retries: int = 2
    default_delay_seconds: float = 2.5
    respect_robots_txt: bool = True
    user_agent: str = "AILeadFinderBot/1.0 (+contact: set-your-contact-email-here)"

    exports_dir: Path = BASE_DIR / "exported_files"
    logs_dir: Path = BASE_DIR / "logs"
    screenshots_dir: Path = BASE_DIR / "exported_files" / "screenshots"

    # If true, personal (non role-based) staff emails are withheld for
    # businesses located in EU/UK/EEA countries. Role-based addresses
    # (info@, contact@, office@ ...) are still collected.
    exclude_personal_data_eu: bool = True


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.exports_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    settings.screenshots_dir.mkdir(parents=True, exist_ok=True)
    return settings
