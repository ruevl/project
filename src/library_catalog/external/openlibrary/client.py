# src/library_catalog/external/openlibrary/client.py
"""OpenLibrary API client with Redis caching."""

import logging
from typing import Any

from ...core.cache import cache, CacheKeys
from ..base.base_client import BaseClient
from .exceptions import OpenLibraryException, OpenLibraryTimeoutException

logger = logging.getLogger(__name__)


class OpenLibraryClient(BaseClient):
    """Client for OpenLibrary API with caching support."""

    async def search_by_isbn(self, isbn: str) -> dict[str, Any]:
        """
        Search book by ISBN with caching.

        Args:
            isbn: Book ISBN

        Returns:
            Book data from OpenLibrary or empty dict
        """
        # Check cache first
        cache_key = CacheKeys.openlibrary_isbn(isbn)
        cached = await cache.get(cache_key)

        if cached is not None:
            logger.debug(f"Cache HIT for ISBN {isbn}")
            return cached

        logger.debug(f"Cache MISS for ISBN {isbn}")

        # Query API
        try:
            data = await self._request(
                "GET",
                "/search.json",
                params={"isbn": isbn, "fields": "key,title,author_name,cover_i,subject,publisher,language"},
            )

            docs = data.get("docs", [])
            if not docs:
                result = {}
            else:
                result = self._extract_book_data(docs[0])

            # Cache result (even if empty)
            await cache.set(cache_key, result)

            return result

        except Exception as e:
            logger.warning(f"OpenLibrary API error for ISBN {isbn}: {e}")
            # Don't cache errors
            return {}

    async def search_by_title_author(self, title: str, author: str) -> dict[str, Any]:
        """
        Search book by title and author with caching.

        Args:
            title: Book title
            author: Book author

        Returns:
            Book data from OpenLibrary or empty dict
        """
        # Check cache first
        cache_key = CacheKeys.openlibrary_title_author(title, author)
        cached = await cache.get(cache_key)

        if cached is not None:
            logger.debug(f"Cache HIT for '{title}' by {author}")
            return cached

        logger.debug(f"Cache MISS for '{title}' by {author}")

        # Query API
        try:
            data = await self._request(
                "GET",
                "/search.json",
                params={
                    "title": title,
                    "author": author,
                    "fields": "key,title,author_name,cover_i,subject,publisher,language",
                },
            )

            docs = data.get("docs", [])
            if not docs:
                result = {}
            else:
                result = self._extract_book_data(docs[0])

            # Cache result
            await cache.set(cache_key, result)

            return result

        except Exception as e:
            logger.warning(f"OpenLibrary API error for '{title}' by {author}: {e}")
            return {}

    async def enrich(
            self,
            isbn: str | None = None,
            title: str | None = None,
            author: str | None = None,
    ) -> dict[str, Any]:
        """
        Enrich book data from OpenLibrary.

        Tries ISBN first (most accurate), then falls back to title/author.

        Args:
            isbn: Optional ISBN
            title: Optional title
            author: Optional author

        Returns:
            Enriched book data or empty dict
        """
        # Try ISBN first (most reliable)
        if isbn:
            data = await self.search_by_isbn(isbn)
            if data:
                return data

        # Fallback to title/author
        if title and author:
            data = await self.search_by_title_author(title, author)
            if data:
                return data

        return {}

    def _extract_book_data(self, doc: dict[str, Any]) -> dict[str, Any]:
        """
        Extract relevant book data from OpenLibrary document.

        Args:
            doc: OpenLibrary API document

        Returns:
            Extracted book data
        """
        result: dict[str, Any] = {}

        # Cover image
        cover_id = doc.get("cover_i")
        if cover_id:
            result["cover_url"] = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

        # Subjects (limited to top 5)
        subjects = doc.get("subject", [])
        if subjects:
            result["subjects"] = subjects[:5]

        # Publisher
        publishers = doc.get("publisher")
        if publishers and isinstance(publishers, list):
            result["publisher"] = publishers[0]

        # Language
        languages = doc.get("language")
        if languages and isinstance(languages, list):
            result["language"] = languages[0]

        return result