"""Клиент для Open Library API."""

import httpx

from ...domain.exceptions import OpenLibraryException, OpenLibraryTimeoutException
from ..base.base_client import BaseApiClient


class OpenLibraryClient(BaseApiClient):
    """Клиент для Open Library API."""

    def __init__(
            self,
            base_url: str = "https://openlibrary.org",
            timeout: float = 10.0,
    ):
        """Инициализация клиента."""
        super().__init__(base_url, timeout=timeout)

    def client_name(self) -> str:
        """Имя клиента."""
        return "openlibrary"

    async def search_by_isbn(self, isbn: str) -> dict:
        """
        Поиск книги по ISBN.

        Args:
            isbn: ISBN-10 или ISBN-13

        Returns:
            Данные книги (cover_url, subjects, etc.)

        Raises:
            OpenLibraryException: При ошибке API
            OpenLibraryTimeoutException: При таймауте
        """
        try:
            data = await self._get(
                "/search.json",
                params={"isbn": isbn, "limit": 1}
            )

            docs = data.get("docs", [])
            if not docs:
                return {}

            return self._extract_book_data(docs[0])

        except httpx.TimeoutException:
            raise OpenLibraryTimeoutException(self.timeout)
        except httpx.HTTPError as e:
            raise OpenLibraryException(str(e))

    async def search_by_title_author(
            self,
            title: str,
            author: str
    ) -> dict:
        """
        Поиск по названию и автору.

        Args:
            title: Название книги
            author: Автор

        Returns:
            Данные книги

        Raises:
            OpenLibraryException: При ошибке API
        """
        try:
            data = await self._get(
                "/search.json",
                params={
                    "title": title,
                    "author": author,
                    "limit": 1
                }
            )

            docs = data.get("docs", [])
            if not docs:
                return {}

            return self._extract_book_data(docs[0])

        except httpx.TimeoutException:
            raise OpenLibraryTimeoutException(self.timeout)
        except httpx.HTTPError as e:
            raise OpenLibraryException(str(e))

    async def enrich(
            self,
            title: str,
            author: str,
            isbn: str | None = None,
    ) -> dict:
        """
        Обогатить данные книги.

        Сначала пытается найти по ISBN, затем по title+author.

        Args:
            title: Название
            author: Автор
            isbn: ISBN (опционально)

        Returns:
            Обогащенные данные или пустой словарь
        """
        # Попытка 1: По ISBN
        if isbn:
            data = await self.search_by_isbn(isbn)
            if data:
                return data

        # Попытка 2: По title + author
        return await self.search_by_title_author(title, author)

    def _extract_book_data(self, doc: dict) -> dict:
        """
        Извлечь нужные поля из ответа Open Library.

        Args:
            doc: Документ из массива docs

        Returns:
            Обработанные данные
        """
        result = {}

        # Cover URL
        if cover_id := doc.get("cover_i"):
            result["cover_url"] = (
                f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            )

        # Subjects (темы)
        if subjects := doc.get("subject"):
            result["subjects"] = subjects[:10]  # Первые 10

        # Publisher
        if publisher := doc.get("publisher"):
            result["publisher"] = publisher[0] if publisher else None

        # Language
        if language := doc.get("language"):
            result["language"] = language[0] if language else None

        # Ratings
        if ratings := doc.get("ratings_average"):
            result["rating"] = ratings

        return result