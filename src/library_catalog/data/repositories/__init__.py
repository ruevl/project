"""Репозитории для работы с данными."""

from .base_repository import BaseRepository
from .book_repository import BookRepository

__all__ = ["BaseRepository", "BookRepository"]