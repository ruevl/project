# src/library_catalog/data/unit_of_work.py
"""Unit of Work pattern for transaction management."""

from typing import Self
from sqlalchemy.ext.asyncio import AsyncSession

from .repositories.book_repository import BookRepository
from .repositories.user_repository import UserRepository


class UnitOfWork:
    """
    Unit of Work pattern implementation.

    Manages database transactions and provides access to repositories.
    Ensures all repository operations happen within a single transaction.

    Usage:
        async with UnitOfWork(session) as uow:
            book = await uow.books.create(...)
            user = await uow.users.create(...)
            await uow.commit()
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize Unit of Work with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session
        self._books: BookRepository | None = None
        self._users: UserRepository | None = None

    @property
    def books(self) -> BookRepository:
        """Get book repository (lazy initialization)."""
        if self._books is None:
            self._books = BookRepository(self.session)
        return self._books

    @property
    def users(self) -> UserRepository:
        """Get user repository (lazy initialization)."""
        if self._users is None:
            self._users = UserRepository(self.session)
        return self._users

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        await self.session.rollback()

    async def flush(self) -> None:
        """Flush pending changes to database without committing."""
        await self.session.flush()

    async def refresh(self, instance) -> None:
        """Refresh an instance from database."""
        await self.session.refresh(instance)

    async def __aenter__(self) -> Self:
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit async context manager.

        Automatically commits on success, rolls back on exception.
        """
        if exc_type is not None:
            # Exception occurred - rollback
            await self.rollback()
        else:
            # No exception - commit
            await self.commit()