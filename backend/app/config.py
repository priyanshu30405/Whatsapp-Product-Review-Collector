"""Application configuration and helpers."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic-powered settings loaded from environment variables or `.env` file."""

    database_url: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/reviews"
    )
    twilio_auth_token: Optional[str] = None
    twilio_enable_validation: bool = True
    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Cache settings so they are created only once per process."""
    return Settings()


