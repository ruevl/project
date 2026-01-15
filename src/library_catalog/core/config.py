"""Конфигурация приложения."""

from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    # Основные настройки
    app_name: str = "Library Catalog API"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # База данных
    database_url: PostgresDsn
    database_pool_size: int = 20

    # API
    api_v1_prefix: str = "/api/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"

    # CORS
    cors_origins: list[str] = ["*"]

    # Логирование
    log_level: str = "INFO"

    # Open Library
    openlibrary_base_url: str = "https://openlibrary.org"
    openlibrary_timeout: float = 10.0

    # JWT Auth (добавлено)
    jwt_secret_key: str = "super-secret-key-change-in-production-2025!"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: PostgresDsn) -> PostgresDsn:
        """Проверить что используется PostgreSQL."""
        if v.scheme not in ("postgresql", "postgresql+asyncpg"):
            raise ValueError("Only PostgreSQL is supported")
        return v

    @property
    def is_production(self) -> bool:
        """Проверить production окружение."""
        return self.environment == "production"

    @property
    def database_url_str(self) -> str:
        """Получить строку подключения."""
        return str(self.database_url)


@lru_cache
def get_settings() -> Settings:
    """Получить настройки (singleton)."""
    return Settings()


settings = get_settings()