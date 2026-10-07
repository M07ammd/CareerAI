"""
CareerPilot AI - Application Configuration

All settings are read from environment variables (or a .env file).
Add new variables here AND in .env.example.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- LLM ---------------------------------------------------------------
    llm_provider: str = Field(default="openai", description="openai | google | anthropic")
    llm_model: str = Field(default="gpt-4o-mini")

    # ---- API Keys -----------------------------------------------------------
    openai_api_key: Optional[str] = Field(default=None)
    google_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)

    # ---- Web Search --------------------------------------------------------
    tavily_api_key: Optional[str] = Field(default=None)
    serper_api_key: Optional[str] = Field(default=None)
    web_search_enabled: bool = Field(default=True)

    # ---- Application -------------------------------------------------------
    app_name: str = Field(default="CareerPilot AI")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # ---- Security ----------------------------------------------------------
    # Optional API-key gate. Disabled (None) for local dev convenience.
    # Set API_KEY=<secret> in production to require X-API-Key header.
    api_key: Optional[str] = Field(default=None, description="Secret for X-API-Key auth (disabled when unset)")

    # ---- Rate Limiting (slowapi) -------------------------------------------
    rate_limit_per_minute: int = Field(default=10, description="Max /analyze requests per IP per minute")

    # ---- File Handling -----------------------------------------------------
    max_pdf_size_mb: int = Field(default=10, description="Maximum PDF upload size in MB")
    max_pdf_pages: int = Field(default=50, description="Maximum pages extracted from PDF")
    max_resume_chars: int = Field(default=30_000, description="Max characters kept from resume text")
    max_jd_chars: int = Field(default=15_000, description="Max characters accepted in job description")

    # ---- Report Saving (opt-in, default off) --------------------------------
    save_reports: bool = Field(default=False, description="Persist reports to disk (SAVE_REPORTS=true to enable)")
    report_output_dir: str = Field(default="data/reports")

    # ---- Retry / Reliability -----------------------------------------------
    # max_agent_retries: N retries AFTER the first attempt (total attempts = N+1)
    max_agent_retries: int = Field(default=2)
    agent_timeout_seconds: int = Field(default=120)

    # ---- CORS --------------------------------------------------------------
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
