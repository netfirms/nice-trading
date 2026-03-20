from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Platform-wide settings using Pydantic for validation."""

    # Dashboard Auth
    DASHBOARD_USER: str = "admin"
    DASHBOARD_PASS: str = "password"

    # Exchange API
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET: Optional[str] = None

    # Infrastructure (Consolidated Postgres 17)
    QUESTDB_HOST: str = "localhost"
    QUESTDB_PORT: int = 9009

    # Persistent Storage (PostgreSQL)
    DATABASE_URL: Optional[str] = None  # e.g. postgresql://user:pass@host:port/db

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
