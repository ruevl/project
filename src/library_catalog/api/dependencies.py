# src/library_catalog/api/dependencies.py
"""Dependency Injection container with secure authentication."""

from typing import Annotated
from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.clients import clients_manager
from ..core.database import get_db
from ..core.auth import decode_access_token
from ..data.repositories.book_repository import BookRepository
from ..data.repositories.user_repository import UserRepository
from ..data.models.user import User
from ..domain.services.book_service import BookService
from ..external.openlibrary.client import OpenLibraryClient

security = HTTPBearer()


def get_openlibrary_client() -> OpenLibraryClient:
    """
    Get OpenLibrary client from manager.
    Manager handles lifecycle - no lru_cache needed.
    """
    return clients_manager.get_openlibrary()


async def get_book_repository(
        db: Annotated[AsyncSession, Depends(get_db)]
) -> BookRepository:
    """Create BookRepository for current session."""
    return BookRepository(db)


async def get_user_repository(
        db: Annotated[AsyncSession, Depends(get_db)]
) -> UserRepository:
    """Create UserRepository for current session."""
    return UserRepository(db)


async def get_book_service(
        db: Annotated[AsyncSession, Depends(get_db)],
        ol_client: Annotated[OpenLibraryClient, Depends(get_openlibrary_client)],
) -> BookService:
    """Create BookService with injected dependencies."""
    return BookService(
        session=db,
        openlibrary_client=ol_client,
    )


async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> User:
    """
    Get current authenticated user from JWT token.

    This dependency:
    1. Validates JWT token
    2. Checks token expiration
    3. Verifies user exists in database
    4. Ensures user account is active

    Args:
        credentials: Bearer token from Authorization header
        user_repo: User repository for database access

    Returns:
        Authenticated User object

    Raises:
        HTTPException 401: If token is invalid or user not found
        HTTPException 403: If user account is disabled
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = decode_access_token(credentials.credentials)

        # Extract username from token
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception

        # Verify token expiration (jose does this automatically, but we can double-check)
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = await user_repo.find_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


# Convenient type aliases
BookServiceDep = Annotated[BookService, Depends(get_book_service)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]