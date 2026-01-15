# src/library_catalog/api/v1/schemas/common.py

from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def create(cls, items: list[T], total: int, pagination: PaginationParams):
        pages = (total + pagination.page_size - 1) // pagination.page_size
        return cls(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            pages=pages,
        )

class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    database: str = "connected"