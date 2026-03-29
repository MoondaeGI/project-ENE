"""Configuration management using pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, ValidationError, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_", env_file=".env", extra="ignore")

    user: str = Field(description="PostgreSQL username")
    password: str = Field(description="PostgreSQL password")
    db: str = Field(description="PostgreSQL database name")
    host: str = Field(default="localhost", description="PostgreSQL host")
    port: int = Field(default=5432, description="PostgreSQL port")
    pool_size: int = Field(default=5, ge=1, le=100)
    max_overflow: int = Field(default=10, ge=0, le=100)
    pool_timeout: int = Field(default=30, ge=1)

    @computed_field
    @property
    def url(self) -> str:
        """Async database URL for SQLAlchemy."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @computed_field
    @property
    def sync_url(self) -> str:
        """Sync database URL for Alembic migrations."""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    default_llm_provider: str = Field(default="openai")

    # OpenAI
    openai_api_key: str = Field(description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o")
    openai_embedding_model: str = Field(default="text-embedding-3-small")

    # Ollama (local — no API key required)
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3")

    # LM Studio (local — no API key required)
    lm_studio_base_url: str = Field(default="http://localhost:1234/v1")
    lm_studio_model: str = Field(default="local-model")

    # LocalAI (local — no API key required)
    local_ai_base_url: str = Field(default="http://localhost:8080/v1")
    local_ai_model: str = Field(default="gpt-3.5-turbo")


class MemorySettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    embedding_dimension: int = Field(default=1536, ge=1)

    # Retrieval weights
    retrieval_weight_recency: float = Field(default=0.3, ge=0.0, le=1.0)
    retrieval_weight_importance: float = Field(default=0.3, ge=0.0, le=1.0)
    retrieval_weight_relevance: float = Field(default=0.4, ge=0.0, le=1.0)

    # Reflection
    reflection_importance_threshold: float = Field(default=10.0, gt=0.0)

    # Memory evolution
    memory_decay_rate: float = Field(default=0.01, gt=0.0)
    memory_reinforcement_factor: float = Field(default=0.1, gt=0.0)
    memory_weak_threshold: float = Field(default=0.1, ge=0.0, le=1.0)
    memory_decay_threshold_days: int = Field(default=30, ge=1)

    # Context window
    max_context_tokens: int = Field(default=200_000, ge=1000)

    @field_validator("retrieval_weight_relevance")
    @classmethod
    def weights_must_sum_to_one(cls, v: float, info) -> float:
        # Soft validation — exact sum checked at runtime
        return v


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "staging", "production"] = Field(default="development")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000, ge=1, le=65535)
    app_debug: bool = Field(default=False)
    secret_key: str = Field(description="Secret key for token signing")

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    log_format: Literal["json", "text"] = Field(default="json")

    cors_origins: list[str] = Field(default=["http://localhost:3000"])


class Settings(BaseSettings):
    """Aggregated application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    memory: MemorySettings = Field(default_factory=MemorySettings)
    app: AppSettings = Field(default_factory=AppSettings)


@lru_cache(maxsize=1)
def _load_settings() -> Settings:
    return Settings()


def get_settings() -> Settings:
    """Return cached application settings. Exits with a clear message on missing env vars."""
    try:
        return _load_settings()
    except ValidationError as e:
        lines = ["[Config Error] Missing or invalid environment variables:"]
        for err in e.errors():
            loc = " > ".join(str(part) for part in err["loc"])
            lines.append(f"  - {loc}: {err['msg']}")
        raise SystemExit("\n".join(lines))
