"""Базовый репозиторий с CRUD операциями."""

from typing import Generic, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import Base

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    """
    Базовый репозиторий с CRUD операциями.

    Generic репозиторий для любой модели SQLAlchemy.
    """

    def __init__(self, session: AsyncSession, model: Type[T]):
        """
        Инициализация репозитория.

        Args:
            session: Async сессия SQLAlchemy
            model: Класс модели SQLAlchemy
        """
        self.session = session
        self.model = model

    async def create(self, **kwargs) -> T:
        """
        Создать новую запись.

        Args:
            **kwargs: Поля для создания

        Returns:
            Созданная запись
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: UUID) -> T | None:
        """
        Получить запись по ID.

        Args:
            id: UUID записи

        Returns:
            Запись или None
        """
        result = await self.session.get(self.model, id)
        return result

    async def update(self, id: UUID, **kwargs) -> T | None:
        """
        Обновить запись.

        Args:
            id: UUID записи
            **kwargs: Поля для обновления

        Returns:
            Обновлённая запись или None
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return None

        for key, value in kwargs.items():
            setattr(instance, key, value)

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: UUID) -> bool:
        """
        Удалить запись.

        Args:
            id: UUID записи

        Returns:
            True если удалено, False если не найдено
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return False

        await self.session.delete(instance)
        await self.session.commit()
        return True

    async def get_all(
            self,
            limit: int = 100,
            offset: int = 0,
    ) -> list[T]:
        """
        Получить все записи с пагинацией.

        Args:
            limit: Максимум записей
            offset: Сдвиг

        Returns:
            Список записей
        """
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())