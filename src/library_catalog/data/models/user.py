# src/library_catalog/data/models/user.py
"""User model for authentication."""

from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

# noinspection PyUnresolvedReferences
from ...core.database import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    user_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
        doc="User unique identifier"
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        doc="Unique username"
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="User email address"
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Bcrypt hashed password"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Is user account active"
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Is user a superuser"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="User creation timestamp"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Last update timestamp"
    )

    def __repr__(self) -> str:
        return f"<User(username={self.username}, email={self.email})>"