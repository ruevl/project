# src/library_catalog/data/repositories/user_repository.py
"""User repository for database operations."""

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import User


class UserRepository:
    """Repository for User model."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    async def create(
            self,
            username: str,
            email: str,
            hashed_password: str,
            is_active: bool = True,
            is_superuser: bool = False,
    ) -> User:
        """Create a new user."""
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=is_active,
            is_superuser=is_superuser,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def find_by_username(self, username: str) -> User | None:
        """Find user by username."""
        stmt = select(User).where(User.username == username)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_email(self, email: str) -> User | None:
        """Find user by email."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        stmt = select(User).where(User.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, user: User) -> User:
        """Update user."""
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """Delete user."""
        await self.session.delete(user)
        await self.session.flush()