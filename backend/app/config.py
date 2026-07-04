"""
Application configuration.

Settings are loaded from environment variables (see .env.example at the repo
root). Nothing sensitive is hard-coded here - threat intel API keys are
optional; when absent, the corresponding feed is skipped gracefully.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "Telnora SOC Platform"
    environment: str = "development"

    # Security
    secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8

    # Database
    database_url: str = "sqlite:///./soc.db"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Rate limiting (basic in-memory, per-client-IP fixed window)
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Threat intel feeds (all optional - features degrade gracefully if unset)
    abuseipdb_api_key: str | None = None
    otx_api_key: str | None = None
    nvd_api_key: str | None = None  # NVD works without a key, key just raises rate limits

    # SLA targets used by analytics (minutes)
    sla_critical_minutes: int = 30
    sla_high_minutes: int = 120
    sla_medium_minutes: int = 480
    sla_low_minutes: int = 1440


@lru_cache
def get_settings() -> Settings:
    return Settings()
