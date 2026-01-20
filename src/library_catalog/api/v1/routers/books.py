"""Book API routers."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...dependencies import BookServiceDep, CurrentUser
from ..schemas.book import BookCreate, BookUpdate, ShowBook
from ..schemas.common import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/books", tags=["books"])


@router.post(
    "/",
    response_model=ShowBook,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
    description="Create a new book with optional ISBN for enrichment from OpenLibrary",
)
async def create_book(
    book_data: BookCreate,
    service: BookServiceDep,
    current_user: CurrentUser,
) -> ShowBook:
    """Create a new book."""
    return await service.create_book(book_data)


@router.get("/", response_model=PaginatedResponse[ShowBook])
async def get_books(
    service: BookServiceDep,
    current_user: CurrentUser,
    pagination: PaginationParams = Depends(),
    title: str | None = Query(None),
    author: str | None = Query(None),
    year: int | None = Query(None),
) -> PaginatedResponse[ShowBook]:
    """Get paginated list of books with optional filters."""
    return await service.get_books(pagination, title=title, author=author, year=year)


@router.get(
    "/{book_id}",
    response_model=ShowBook,
    summary="Get book by ID",
    description="Get detailed information about a specific book",
)
async def get_book(
    book_id: str,
    service: BookServiceDep,
    current_user: CurrentUser,
) -> ShowBook:
    """Get book by ID."""
    # Convert string to UUID in service layer
    from uuid import UUID
    return await service.get_book(UUID(book_id))


@router.put(
    "/{book_id}",
    response_model=ShowBook,
    summary="Update book",
    description="Update existing book information",
)
async def update_book(
    book_id: str,
    book_data: BookUpdate,
    service: BookServiceDep,
    current_user: CurrentUser,
) -> ShowBook:
    """Update book."""
    from uuid import UUID
    return await service.update_book(UUID(book_id), book_data)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete book",
    description="Delete a book by ID",
)
async def delete_book(
    book_id: str,
    service: BookServiceDep,
    current_user: CurrentUser,
) -> None:
    """Delete book."""
    from uuid import UUID
    await service.delete_book(UUID(book_id))