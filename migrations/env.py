import os
import asyncio  # Добавьте этот импорт
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine  # Замените AsyncEngine на create_async_engine
from alembic import context
from app.models import Base  # Убедитесь, что импортируете свои модели правильно
from app.config import DATABASE_URL as url_db
config = context.config
fileConfig(config.config_file_name)

DATABASE_URL = os.getenv("DATABASE_URL", url_db)
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Указываем метаданные для использования в миграциях
target_metadata = Base.metadata


# Создаем асинхронный движок SQLAlchemy
def get_async_engine():
    return create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

def do_run_migrations(connection):
    """Синхронная функция для выполнения миграций."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True  # Это позволяет избегать потери данных при изменении схемы
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations():
    """Асинхронная функция для подключения к базе данных и выполнения миграций."""
    connectable = get_async_engine()

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

def run_migrations_online():
    """Запуск миграций онлайн (в реальной базе данных)."""
    asyncio.run(run_migrations())

run_migrations_online()