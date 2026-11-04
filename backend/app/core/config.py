"""Application settings, loaded from environment variables (and `.env` in local dev).

Every tunable lives here so nothing (paths, models, URLs) is hardcoded elsewhere.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Repo-root .env when running from backend/, or a local one; real env vars always win.
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["dev", "test", "prod"] = "dev"
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    database_url: str = "postgresql+asyncpg://documind:documind@localhost:5432/documind"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "documind_chunks"

    ollama_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen2.5:3b"
    embedding_model: str = "bge-m3"

    # Per-dependency timeout for /api/health/ready, in seconds.
    health_timeout_s: float = 2.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
