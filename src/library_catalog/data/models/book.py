"""Модель книги."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...core.database import Base


class Book(Base):
    """
    Модель книги в каталоге.

    Attributes:
        book_id: Уникальный ID книги
        title: Название книги
        author: Автор
        year: Год издания
        genre: Жанр
        pages: Количество страниц
        available: Доступна ли книга
        isbn: ISBN номер
        cover_url: URL обложки книги (из OpenLibrary)
        description: Описание
        subjects: Список тем/категорий (из OpenLibrary)
        extra: Дополнительные данные из Open Library
        created_at: Дата создания записи
        updated_at: Дата последнего обновления
    """

    __tablename__ = "books"

    # Primary Key
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Обязательные поля
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )

    author: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    genre: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    pages: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    # Опциональные поля
    isbn: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        unique=True,
    )

    cover_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    subjects: Mapped[list[str] | None] = mapped_column(  # ← ИСПРАВЛЕНО: теперь list[str] + JSON
        JSON,
        nullable=True,
    )

    extra: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        """Строковое представление."""
        return f"<Book(id={self.book_id}, title='{self.title}')>"