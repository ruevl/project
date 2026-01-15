"""In-memory cache for the application."""

from aiocache import Cache

cache = Cache(Cache.MEMORY, namespace="library", ttl=300)
