"""Redis cache for application with proper configuration."""

import logging
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from redis.asyncio import ConnectionError as RedisConnectionError

from .config import settings

logger = logging.getLogger(__name__)


class CacheKeys:
    """Cache key constants and generators."""

    # OpenLibrary cache keys
    OPENLIBRARY_ISBN = "ol:isbn:{isbn}"
    OPENLIBRARY_TITLE_AUTHOR = "ol:title:{title}:author:{author}"

    # Book cache keys
    BOOK_DETAIL = "book:{book_id}"
    BOOKS_LIST = "books:list"

    @classmethod
    def openlibrary_isbn(cls, isbn: str) -> str:
        """Generate cache key for OpenLibrary ISBN lookup."""
        return cls.OPENLIBRARY_ISBN.format(isbn=isbn)

    @classmethod
    def openlibrary_title_author(cls, title: str, author: str) -> str:
        """Generate cache key for OpenLibrary title/author lookup."""
        title_clean = title.lower().strip()
        author_clean = author.lower().strip()
        return cls.OPENLIBRARY_TITLE_AUTHOR.format(
            title=title_clean,
            author=author_clean
        )

    @classmethod
    def book_detail(cls, book_id: str) -> str:
        """Generate cache key for book detail."""
        return cls.BOOK_DETAIL.format(book_id=book_id)

    @classmethod
    def books_list_all(cls) -> str:
        """Pattern for all books list cache keys."""
        return f"{cls.BOOKS_LIST}:*"


def create_cache() -> Cache:
    """
    Create Redis cache instance.

    Falls back to in-memory only if Redis is truly unavailable.
    """
    try:
        # Try Redis first
        cache_instance = Cache(
            Cache.REDIS,
            endpoint=settings.redis_host,
            port=settings.redis_port,
            namespace="library",
            ttl=settings.cache_ttl,
            serializer=JsonSerializer(),
        )

        # Test connection (optional but recommended)
        # Note: aiocache doesn't expose direct connection test,
        # so we rely on first operation to fail if needed

        logger.info(f"Using Redis cache at {settings.redis_host}:{settings.redis_port}")
        return cache_instance

    except (RedisConnectionError, Exception) as e:
        logger.warning(
            f"Redis connection failed ({e}), falling back to in-memory cache. "
            "For production, ensure Redis is running."
        )
        return Cache(
            Cache.MEMORY,
            namespace="library",
            ttl=settings.cache_ttl,
        )


# Global cache instance
cache = create_cache()


async def clear_cache_pattern(pattern: str) -> None:
    """
    Clear all cache keys matching a pattern.

    Works with both Redis and in-memory (limited support for memory).
    """
    try:
        await cache.delete(pattern)
        logger.info(f"Cleared cache pattern: {pattern}")
    except Exception as e:
        logger.warning(f"Failed to clear cache pattern {pattern}: {e}")


async def close_cache() -> None:
    """Close cache connections."""
    try:
        await cache.close()
        logger.info("Cache connections closed")
    except Exception as e:
        logger.warning(f"Error closing cache: {e}")