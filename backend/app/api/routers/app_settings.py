import json

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


class AppSettings(BaseModel):
    theme: str = "system"  # dark | light | system
    export_folder: str | None = None
    language: str = "en"
    auto_save: bool = True


def _settings_file_path():
    return get_settings().exports_dir.parent / "app_settings.json"


def _load() -> AppSettings:
    path = _settings_file_path()
    if path.exists():
        return AppSettings.model_validate(json.loads(path.read_text()))
    return AppSettings()


def _save(settings: AppSettings) -> None:
    path = _settings_file_path()
    path.write_text(settings.model_dump_json(indent=2))


@router.get("", response_model=AppSettings)
async def get_app_settings():
    return _load()


@router.put("", response_model=AppSettings)
async def update_app_settings(settings: AppSettings):
    _save(settings)
    return settings
