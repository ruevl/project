# src/library_catalog/main.py
"""FastAPI application with security improvements."""

import os
from dotenv import load_dotenv

# Загружаем .env до импорта ЛЮБЫХ модулей проекта
load_dotenv()

# Только теперь можно импортировать остальное
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.routers import books, auth
from .core.cache import close_cache
from .core.clients import clients_manager
from .core.config import settings
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info(f"Starting Library Catalog API in {settings.environment} mode")
    logger.info(f"Database: {settings.database_url.split('@')[-1]}")  # Don't log credentials
    logger.info(f"Redis: {settings.redis_host}:{settings.redis_port}")

    yield

    # Shutdown
    logger.info("Shutting down Library Catalog API")
    await clients_manager.close_all()
    await close_cache()
    logger.info("Cleanup complete")


app = FastAPI(
    title="Library Catalog API",
    description="REST API for managing library book catalog with OpenLibrary integration",
    version="1.0.0",
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    lifespan=lifespan,
)

# CORS Middleware - Configured securely
if settings.cors_origins:
    # Only add CORS if origins are configured
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Authorization", "Content-Type"],
        max_age=3600,
    )
    logger.info(f"CORS enabled for origins: {settings.cors_origins}")

    # Warning for wildcard in production
    if "*" in settings.cors_origins and settings.environment == "production":
        logger.warning(
            "⚠️  SECURITY WARNING: CORS wildcard (*) should NOT be used in production!"
        )
else:
    logger.info("CORS not configured (no origins specified)")

# Include routers
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(books.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Library Catalog API",
        "version": "1.0.0",
        "environment": settings.environment,
        "docs": settings.docs_url,
        "status": "healthy",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "environment": settings.environment,
    }