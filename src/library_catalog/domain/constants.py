# src/library_catalog/domain/constants.py
"""Domain constants to avoid magic values."""

from datetime import datetime


class BookConstants:
    """Constants for book validation and business rules."""

    # Year validation
    MIN_YEAR = 1000

    @classmethod
    def max_year(cls) -> int:
        """Get current year as maximum allowed year."""
        return datetime.now().year

    # Pages validation
    MIN_PAGES = 1
    MAX_PAGES = 10000

    # ISBN validation
    ISBN_10_LENGTH = 10
    ISBN_13_LENGTH = 13

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    MIN_PAGE_SIZE = 1


class CacheConstants:
    """Constants for caching configuration."""

    # Cache TTL in seconds
    OPENLIBRARY_TTL = 300  # 5 minutes
    BOOK_DETAIL_TTL = 60  # 1 minute
    BOOK_LIST_TTL = 30  # 30 seconds

    # Cache prefixes (defined in cache.py CacheKeys, but can reference here)
    PREFIX_OPENLIBRARY = "ol"
    PREFIX_BOOK = "book"
    PREFIX_BOOKS_LIST = "books:list"


class RateLimitConstants:
    """Constants for rate limiting."""

    # Requests per minute
    OPENLIBRARY_MAX_CONCURRENT = 5
    API_REQUESTS_PER_MINUTE = 60

    # Burst limits
    CREATE_BOOKS_PER_MINUTE = 10
    SEARCH_REQUESTS_PER_MINUTE = 100


class AuthConstants:
    """Constants for authentication."""

    # Token expiration
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    # Password requirements
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128

    # Username requirements
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50