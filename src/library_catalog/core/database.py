"""Настройка подключения к базе данных."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    """Базовый класс для моделей."""
    pass


# Создаём async engine
engine: AsyncEngine = create_async_engine(
    settings.database_url_str,
    pool_size=settings.database_pool_size,
    echo=settings.debug,
    future=True,
)

# Создаём фабрику сессий
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии БД.

    Yields:
        AsyncSession: Сессия базы данных
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_engine() -> None:
    """Закрыть все соединения с БД."""
    await engine.dispose()