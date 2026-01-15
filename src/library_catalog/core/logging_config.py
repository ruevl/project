"""Конфигурация логирования."""

import logging
import sys


def setup_logging() -> None:
    """Настроить логирование приложения."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Логгер для приложения
    logger = logging.getLogger("library_catalog")
    logger.setLevel(logging.INFO)

    # Уменьшаем количество логов от библиотек
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)