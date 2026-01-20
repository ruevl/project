"""Репозиторий для работы с книгами."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.book import Book
from .base_repository import BaseRepository


class BookRepository(BaseRepository[Book]):
    """Репозиторий для работы с книгами."""

    def __init__(self, session: AsyncSession):
        """Инициализация."""
        super().__init__(session, Book)

    async def find_by_isbn(self, isbn: str) -> Book | None:
        """
        Найти книгу по ISBN.

        Args:
            isbn: ISBN номер

        Returns:
            Книга или None
        """
        stmt = select(Book).where(Book.isbn == isbn)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_filters(
            self,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None,
            limit: int = 20,
            offset: int = 0,
    ) -> list[Book]:
        """
        Поиск книг с фильтрацией.

        Args:
            title: Частичное совпадение по названию
            author: Частичное совпадение по автору
            genre: Точное совпадение жанра
            year: Точное совпадение года
            available: Фильтр по доступности
            limit: Максимум результатов
            offset: Сдвиг

        Returns:
            Список найденных книг
        """
        stmt = select(Book)

        # Применяем фильтры
        if title:
            stmt = stmt.where(Book.title.ilike(f"%{title}%"))

        if author:
            stmt = stmt.where(Book.author.ilike(f"%{author}%"))

        if genre:
            stmt = stmt.where(Book.genre == genre)

        if year is not None:
            stmt = stmt.where(Book.year == year)

        if available is not None:
            stmt = stmt.where(Book.available == available)

        # Пагинация
        stmt = stmt.limit(limit).offset(offset)

        # Выполнение запроса
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_all(
            self,
            limit: int = 20,
            offset: int = 0,
            title: str | None = None,
            author: str | None = None,
            year: int | None = None,
    ) -> tuple[list[Book], int]:
        """
        Получить все книги с фильтрацией и пагинацией.

        Returns:
            Кортеж из (список книг, общее количество)
        """
        # Сначала получаем общее количество
        count_stmt = select(func.count()).select_from(Book)
        if title:
            count_stmt = count_stmt.where(Book.title.ilike(f"%{title}%"))
        if author:
            count_stmt = count_stmt.where(Book.author.ilike(f"%{author}%"))
        if year is not None:
            count_stmt = count_stmt.where(Book.year == year)

        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar_one()

        # Затем получаем книги
        stmt = select(Book)
        if title:
            stmt = stmt.where(Book.title.ilike(f"%{title}%"))
        if author:
            stmt = stmt.where(Book.author.ilike(f"%{author}%"))
        if year is not None:
            stmt = stmt.where(Book.year == year)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        books = list(result.scalars().all())

        return books, total

    async def count_by_filters(
            self,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None,
    ) -> int:
        """
        Подсчитать количество книг по фильтрам.

        Args:
            title: Фильтр по названию
            author: Фильтр по автору
            genre: Фильтр по жанру
            year: Фильтр по году
            available: Фильтр по доступности

        Returns:
            Количество книг
        """
        stmt = select(func.count()).select_from(Book)

        # Применяем те же фильтры
        if title:
            stmt = stmt.where(Book.title.ilike(f"%{title}%"))

        if author:
            stmt = stmt.where(Book.author.ilike(f"%{author}%"))

        if genre:
            stmt = stmt.where(Book.genre == genre)

        if year is not None:
            stmt = stmt.where(Book.year == year)

        if available is not None:
            stmt = stmt.where(Book.available == available)

        result = await self.session.execute(stmt)
        return result.scalar_one()