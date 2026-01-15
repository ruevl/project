# src/library_catalog/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.clients import clients_manager
from .core.config import settings
from .core.database import dispose_engine
from .core.exceptions import register_exception_handlers
from .core.logging_config import setup_logging
from .api.v1.routers import books, health, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle-менеджер для корректного запуска и завершения приложения.
    """
    # --- Startup ---
    setup_logging()
    print("🚀 Application started")

    yield

    # --- Shutdown ---
    print("👋 Shutting down...")
    await clients_manager.close_all()
    await dispose_engine()
    print("✅ Application stopped")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(books.router, prefix=settings.api_v1_prefix)
app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(auth.router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Library Catalog API",
        "version": "1.0.0",
        "docs": settings.docs_url,
    }