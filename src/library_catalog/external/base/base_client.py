# src/library_catalog/external/base/base_client.py
"""Base HTTP client for external API integrations."""

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class BaseClient:
    """Base class for HTTP API clients."""
    
    def __init__(self, base_url: str, timeout: float = 10.0):
        """
        Initialize base client.
        
        Args:
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                follow_redirects=True,
            )
        return self._client
    
    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Make HTTP request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path
            params: Query parameters
            json: JSON body
            headers: HTTP headers
            
        Returns:
            Response JSON data
            
        Raises:
            httpx.HTTPError: On HTTP errors
        """
        try:
            response = await self.client.request(
                method=method,
                url=path,
                params=params,
                json=json,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(
                f"HTTP error during {method} {path}: {e}",
                extra={"method": method, "path": path, "params": params}
            )
            raise
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None