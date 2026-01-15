"""Dependency Injection контейнер."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.clients import clients_manager
from ..core.database import get_db
from ..data.repositories.book_repository import BookRepository
from ..domain.services.book_service import BookService
from ..external.openlibrary.client import OpenLibraryClient


def get_openlibrary_client() -> OpenLibraryClient:
    """
    Получить OpenLibrary клиент из менеджера.
    Теперь БЕЗ lru_cache — менеджер сам управляет lifecycle.
    """
    return clients_manager.get_openlibrary()


async def get_book_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> BookRepository:
    """Создать BookRepository для текущей сессии."""
    return BookRepository(db)


async def get_book_service(
    book_repo: Annotated[BookRepository, Depends(get_book_repository)],
    ol_client: Annotated[OpenLibraryClient, Depends(get_openlibrary_client)],
) -> BookService:
    """Создать BookService с внедренными зависимостями."""
    return BookService(
        book_repository=book_repo,
        openlibrary_client=ol_client,
    )


# Удобные алиасы
BookServiceDep = Annotated[BookService, Depends(get_book_service)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]



# JWT Authentication
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from ..core.config import settings

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Удобный алиас
from typing import Annotated
CurrentUser = Annotated[dict, Depends(get_current_user)]