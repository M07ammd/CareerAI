"""
CareerPilot AI - Application Configuration

All settings are read from environment variables (or a .env file).
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
    llm_provider: str = Field(default="openai", description="LLM provider: openai | google | anthropic")
    llm_model: str = Field(default="gpt-4o-mini", description="Model name for the chosen provider")

    # ---- API Keys (at least one must be set based on provider) -------------
    openai_api_key: Optional[str] = Field(default=None)
    google_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)

    # ---- Web Search --------------------------------------------------------
    tavily_api_key: Optional[str] = Field(default=None, description="Tavily API key for web search")
    serper_api_key: Optional[str] = Field(default=None, description="Serper.dev API key for web search")
    web_search_enabled: bool = Field(default=True, description="Enable/disable web search tool")

    # ---- Application -------------------------------------------------------
    app_name: str = Field(default="CareerPilot AI")
    version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # ---- File Handling -----------------------------------------------------
    max_pdf_size_mb: int = Field(default=10, description="Maximum PDF upload size in MB")
    report_output_dir: str = Field(default="data/reports", description="Directory for saved reports")

    # ---- Retry / Reliability -----------------------------------------------
    max_agent_retries: int = Field(default=2, description="Maximum retries per agent on failure")
    agent_timeout_seconds: int = Field(default=120, description="Per-agent timeout in seconds")

    # ---- CORS --------------------------------------------------------------
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"],
        description="Allowed CORS origins",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
