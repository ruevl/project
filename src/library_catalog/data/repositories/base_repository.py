"""Базовый репозиторий с CRUD операциями."""

from typing import Generic, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import Base

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    """
    Базовый репозиторий для CRUD операций.

    ВАЖНО: Репозиторий НЕ делает commit!
    Commit — это ответственность сервиса.
    """

    def __init__(self, session: AsyncSession, model: Type[T]):
        """Инициализация репозитория."""
        self.session = session
        self.model = model

    async def create(self, **kwargs) -> T:
        """
        Создать новую запись БЕЗ commit.

        flush() генерирует ID и проверяет constraints,
        но оставляет commit вызывающему коду.
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: UUID) -> T | None:
        """Получить запись по ID."""
        result = await self.session.get(self.model, id)
        return result

    async def update(self, id: UUID, **kwargs) -> T | None:
        """Обновить запись БЕЗ commit."""
        instance = await self.get_by_id(id)
        if instance is None:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: UUID) -> bool:
        """Удалить запись БЕЗ commit."""
        instance = await self.get_by_id(id)
        if instance is None:
            return False

        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def get_all(
            self,
            limit: int = 100,
            offset: int = 0,
    ) -> list[T]:
        """Получить все записи с пагинацией."""
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())