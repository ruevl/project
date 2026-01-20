# src/library_catalog/external/openlibrary/exceptions.py
"""Exceptions for OpenLibrary API client."""


class OpenLibraryException(Exception):
    """Base exception for OpenLibrary API errors."""
    pass


class OpenLibraryTimeoutException(OpenLibraryException):
    """Raised when OpenLibrary API request times out."""

    def __init__(self, timeout: float, message: str = ""):
        self.timeout = timeout
        super().__init__(message or f"OpenLibrary API request timed out after {timeout}s")


class OpenLibraryHTTPException(OpenLibraryException):
    """Raised when OpenLibrary API returns HTTP error."""

    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        super().__init__(message or f"OpenLibrary API returned status {status_code}")


class OpenLibraryNotFoundException(OpenLibraryException):
    """Raised when requested resource is not found."""
    pass
