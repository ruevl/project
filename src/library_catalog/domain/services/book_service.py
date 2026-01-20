# src/library_catalog/domain/services/book_service.py
"""Book service with Unit of Work pattern and cache invalidation."""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ...api.v1.schemas.book import BookCreate, BookUpdate, ShowBook
from ...api.v1.schemas.common import PaginatedResponse, PaginationParams
from ...core.cache import cache, CacheKeys
from ...data.unit_of_work import UnitOfWork
from ...external.openlibrary.client import OpenLibraryClient
from ..exceptions import (
    BookAlreadyExistsException,
    BookNotFoundException,
    InvalidYearException,
    InvalidPagesException,
)
from ..mappers.book_mapper import BookMapper

logger = logging.getLogger(__name__)


class BookService:
    """Book business logic service using Unit of Work pattern."""

    def __init__(
            self,
            session: AsyncSession,
            openlibrary_client: OpenLibraryClient,
    ):
        """
        Initialize service.

        Args:
            session: Database session for UnitOfWork
            openlibrary_client: Client for OpenLibrary API
        """
        self.session = session
        self.ol_client = openlibrary_client

    def _validate_year(self, year: int) -> None:
        """Validate book year."""
        current_year = datetime.now().year
        if year < 1000 or year > current_year:
            raise InvalidYearException(year)

    def _validate_pages(self, pages: int) -> None:
        """Validate book pages."""
        if pages <= 0:
            raise InvalidPagesException(pages)

    async def _enrich_book_data(self, book_data: BookCreate) -> dict | None:
        """
        Enrich book data from OpenLibrary API.

        Returns enriched data or None if enrichment fails.
        """
        try:
            extra_data = await self.ol_client.enrich(
                isbn=book_data.isbn,
                title=book_data.title,
                author=book_data.author,
            )

            if extra_data:
                logger.info(
                    f"Successfully enriched book '{book_data.title}' with OpenLibrary data"
                )

            return extra_data

        except Exception as e:
            logger.warning(
                f"Failed to enrich book '{book_data.title}' from OpenLibrary: {e}",
                extra={"isbn": book_data.isbn, "error": str(e)}
            )
            return None

    async def create_book(self, book_data: BookCreate) -> ShowBook:
        """
        Create a new book with enrichment from OpenLibrary.

        Args:
            book_data: Book creation data

        Returns:
            Created book with enriched data

        Raises:
            BookAlreadyExistsException: If ISBN already exists
            InvalidYearException: If year is invalid
            InvalidPagesException: If pages is invalid
        """
        async with UnitOfWork(self.session) as uow:
            # Validation
            self._validate_year(book_data.year)
            if book_data.pages:
                self._validate_pages(book_data.pages)

            # Check for duplicates by ISBN
            if book_data.isbn:
                existing = await uow.books.find_by_isbn(book_data.isbn)
                if existing:
                    raise BookAlreadyExistsException(book_data.isbn)

            # Enrich data from OpenLibrary
            extra_data = await self._enrich_book_data(book_data)

            # Create book
            book = await uow.books.create(
                title=book_data.title,
                author=book_data.author,
                year=book_data.year,
                isbn=book_data.isbn,
                pages=book_data.pages,
                cover_url=extra_data.get("cover_url") if extra_data else None,
                subjects=extra_data.get("subjects") if extra_data else None,
            )

            # Commit transaction
            await uow.commit()

            # 🔥 Invalidate cache - use specific keys instead of patterns
            await cache.delete(CacheKeys.books_list_all())
            if book_data.isbn:
                await cache.delete(CacheKeys.openlibrary_isbn(book_data.isbn))

            return BookMapper.to_show_book(book)

    async def get_books(
            self,
            pagination: PaginationParams,
            title: str | None = None,
            author: str | None = None,
            year: int | None = None,
    ) -> PaginatedResponse[ShowBook]:
        """Get paginated list of books with optional filters."""
        async with UnitOfWork(self.session) as uow:
            books, total = await uow.books.find_all(
                limit=pagination.page_size,
                offset=(pagination.page - 1) * pagination.page_size,
                title=title,
                author=author,
                year=year,
            )

            show_books = [BookMapper.to_show_book(book) for book in books]

            return PaginatedResponse.create(
                items=show_books,
                total=total,
                pagination=pagination,
            )

    async def get_book(self, book_id: UUID) -> ShowBook:
        """
        Get book by ID.

        Raises:
            BookNotFoundException: If book not found
        """
        # Try to get from cache first
        cache_key = CacheKeys.book_detail(str(book_id))
        cached_book = await cache.get(cache_key)
        if cached_book:
            return ShowBook(**cached_book)

        async with UnitOfWork(self.session) as uow:
            book = await uow.books.get_by_id(book_id)

            if not book:
                raise BookNotFoundException(book_id)

            # Cache the result
            book_dict = BookMapper.to_show_book(book).model_dump()
            await cache.set(cache_key, book_dict)

            return BookMapper.to_show_book(book)

    async def update_book(self, book_id: UUID, book_data: BookUpdate) -> ShowBook:
        """
        Update book.

        Raises:
            BookNotFoundException: If book not found
            InvalidYearException: If year is invalid
            InvalidPagesException: If pages is invalid
        """
        async with UnitOfWork(self.session) as uow:
            # Get existing book
            book = await uow.books.get_by_id(book_id)
            if not book:
                raise BookNotFoundException(book_id)

            # Validate new data
            if book_data.year is not None:
                self._validate_year(book_data.year)
            if book_data.pages is not None:
                self._validate_pages(book_data.pages)

            # Update book
            updated_book = await uow.books.update(book_id, **book_data.model_dump(exclude_unset=True))

            # Commit transaction
            await uow.commit()

            # 🔥 Invalidate cache - use specific keys
            await cache.delete(CacheKeys.book_detail(str(book_id)))
            await cache.delete(CacheKeys.books_list_all())

            return BookMapper.to_show_book(updated_book)

    async def delete_book(self, book_id: UUID) -> None:
        """
        Delete book.

        Raises:
            BookNotFoundException: If book not found
        """
        async with UnitOfWork(self.session) as uow:
            book = await uow.books.get_by_id(book_id)
            if not book:
                raise BookNotFoundException(book_id)

            # Store ISBN for cache invalidation
            book_isbn = book.isbn

            await uow.books.delete(book_id)

            # Commit transaction
            await uow.commit()

            # 🔥 Invalidate cache - use specific keys
            await cache.delete(CacheKeys.book_detail(str(book_id)))
            await cache.delete(CacheKeys.books_list_all())
            if book_isbn:
                await cache.delete(CacheKeys.openlibrary_isbn(book_isbn))