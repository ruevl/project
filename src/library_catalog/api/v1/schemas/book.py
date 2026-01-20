# src/library_catalog/api/v1/schemas/book.py

from datetime import datetime
from uuid import UUID
from typing import Optional, Union, List
from pydantic import BaseModel, Field, field_validator


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=300)
    year: int = Field(..., ge=1000, le=2100)
    pages: int = Field(..., gt=0)
    genre: Optional[str] = Field(None, max_length=100)


class BookCreate(BookBase):
    isbn: Optional[str] = Field(None, min_length=10, max_length=20)
    description: Optional[str] = Field(None, max_length=5000)

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        clean = v.replace("-", "").replace(" ", "")
        if not clean.replace("X", "").isdigit():
            raise ValueError("ISBN must contain only digits")
        if len(clean) not in (10, 13):
            raise ValueError("ISBN must be 10 or 13 digits")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Clean Code",
                    "author": "Robert Martin",
                    "year": 2008,
                    "genre": "Programming",
                    "pages": 464,
                    "isbn": "978-0132350884",
                    "description": "A Handbook of Agile Software Craftsmanship"
                }
            ]
        }
    }


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    author: Optional[str] = Field(None, min_length=1, max_length=300)
    year: Optional[int] = Field(None, ge=1000, le=2100)
    pages: Optional[int] = Field(None, gt=0)
    genre: Optional[str] = Field(None, max_length=100)
    available: Optional[bool] = None
    isbn: Optional[str] = None
    description: Optional[str] = None


class ShowBook(BookBase):
    book_id: UUID
    available: bool
    isbn: Optional[str]
    description: Optional[str]
    subjects: Optional[Union[List[str], str]] = None
    extra: Optional[dict]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "book_id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Clean Code",
                    "author": "Robert Martin",
                    "year": 2008,
                    "genre": "Programming",
                    "pages": 464,
                    "available": True,
                    "isbn": "978-0132350884",
                    "description": "A Handbook of Agile Software Craftsmanship",
                    "subjects": ["Computer Science", "Software Engineering"],
                    "extra": {
                        "cover_url": "https://covers.openlibrary.org/b/id/123-L.jpg"
                    },
                    "created_at": "2024-01-01T12:00:00",
                    "updated_at": "2024-01-01T12:00:00"
                }
            ]
        }
    }