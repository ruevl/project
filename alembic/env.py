# alembic/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Импортируем настройки и модели
from src.library_catalog.core.config import settings
from src.library_catalog.core.database import Base
from src.library_catalog.data.models import book  # noqa: F401

# Убираем +asyncpg, потому что Alembic — синхронный инструмент
database_url = str(settings.database_url).replace("+asyncpg", "")

config = context.config

# Передаём URL напрямую (в обход alembic.ini)
config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()