# src/library_catalog/api/dependencies.py

from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_db
from ..data.repositories.book_repository import BookRepository
from ..domain.services.book_service import BookService
from ..external.openlibrary.client import OpenLibraryClient
from ..core.config import settings

@lru_cache
def get_openlibrary_client() -> OpenLibraryClient:
    return OpenLibraryClient(
        base_url=settings.openlibrary_base_url,
        timeout=settings.openlibrary_timeout,
    )

async def get_book_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> BookRepository:
    return BookRepository(db)

async def get_book_service(
    book_repo: Annotated[BookRepository, Depends(get_book_repository)],
    ol_client: Annotated[OpenLibraryClient, Depends(get_openlibrary_client)],
) -> BookService:
    return BookService(book_repository=book_repo, openlibrary_client=ol_client)

# Удобные алиасы
BookServiceDep = Annotated[BookService, Depends(get_book_service)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]