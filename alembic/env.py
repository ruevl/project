# alembic/env.py

import os
import sys

# ЗАГРУЖАЕМ .env с ЯВНЫМ ПУТЁМ
from dotenv import load_dotenv
# Указываем путь к .env относительно этого файла
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Теперь можно импортировать настройки
from library_catalog.core.config import settings
from library_catalog.core.database import Base

# Импортируем модели
from library_catalog.data.models.user import User  # noqa: F401
from library_catalog.data.models.book import Book  # noqa: F401

# Остальной код остаётся без изменений...
database_url = str(settings.database_url).replace("+asyncpg", "")
# ... и так далее

config = context.config
config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
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