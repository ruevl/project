# src/library_catalog/api/v1/routers/books.py

from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from ..schemas.book import BookCreate, BookUpdate, ShowBook
from ..schemas.common import PaginatedResponse, PaginationParams
from ...dependencies import BookServiceDep, CurrentUser

router = APIRouter(prefix="/books", tags=["Books"])

@router.post("/", response_model=ShowBook, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    service: BookServiceDep,
    current_user: CurrentUser,
):
    return await service.create_book(book_data)

@router.get("/", response_model=PaginatedResponse[ShowBook])
async def get_books(
    service: BookServiceDep,
    pagination: Annotated[PaginationParams, Depends()],
    title: str | None = Query(None),
    author: str | None = Query(None),
    genre: str | None = Query(None),
    year: int | None = Query(None),
    available: bool | None = Query(None),
):
    books, total = await service.search_books(
        title=title,
        author=author,
        genre=genre,
        year=year,
        available=available,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return PaginatedResponse.create(books, total, pagination)

@router.get("/{book_id}", response_model=ShowBook)
async def get_book(book_id: UUID, service: BookServiceDep):
    return await service.get_book(book_id)

@router.patch("/{book_id}", response_model=ShowBook)
async def update_book(
    book_id: UUID,
    book_data: BookUpdate,
    service: BookServiceDep,
    current_user: CurrentUser,
):
    return await service.update_book(book_id, book_data)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: UUID,
    service: BookServiceDep,
    current_user: CurrentUser,
):
    await service.delete_book(book_id)