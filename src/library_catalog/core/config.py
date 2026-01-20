# src/library_catalog/core/config.py
"""Application configuration with security best practices."""

from typing import Any
from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Application
    environment: str = "development"
    debug: bool = False

    # Database
    database_url: str = Field(
        ...,  # Обязательное поле
        description="PostgreSQL connection string"
    )

    # API
    api_v1_prefix: str = "/api/v1"

    # Logging
    log_level: str = "INFO"

    # Documentation
    docs_url: str | None = "/docs"
    redoc_url: str | None = "/redoc"

    # CORS
    cors_origins: list[str] = Field(
        default_factory=list,
        description="Allowed CORS origins"
    )

    # OpenLibrary API
    openlibrary_base_url: str = "https://openlibrary.org"
    openlibrary_timeout: float = 10.0

    # JWT Authentication - ОБЯЗАТЕЛЬНО через env переменные!
    jwt_secret_key: SecretStr = Field(
        ...,  # Нет default - ОБЯЗАТЕЛЬНО из .env
        description="Secret key for JWT token generation (min 32 chars)"
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    # Redis Cache
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    redis_host: str = "localhost"
    redis_port: int = 6379
    cache_ttl: int = 300  # 5 минут

    # Rate Limiting
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, v: SecretStr) -> SecretStr:
        """Проверить что JWT secret достаточно длинный."""
        secret = v.get_secret_value()
        if len(secret) < 32:
            raise ValueError(
                "JWT secret key must be at least 32 characters long. "
                "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        return v

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, v: list[str], info: Any) -> list[str]:
        """Запретить wildcard CORS в production."""
        environment = info.data.get("environment", "development")
        if "*" in v and environment == "production":
            raise ValueError(
                "CORS wildcard (*) is not allowed in production environment"
            )
        return v

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Проверить формат database URL."""
        if not v.startswith("postgresql"):
            raise ValueError("Database URL must start with 'postgresql' or 'postgresql+asyncpg'")
        return v


settings = Settings()