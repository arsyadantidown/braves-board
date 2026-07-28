import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 1. Import setting environment dan Base metadata dari proyek Anda
from app.settings import settings
from app.connections.postgres import Base
from app.models.user_model import User
from app.models.board_model import Board
from app.models.column_model import Column
from app.models.task_model import Task
from app.models.subtask_model import Subtask
from app.models.task_comment_model import TaskComment
from app.models.task_attachment_model import TaskAttachment
from app.models.time_log_model import TimeLog
from app.models.app_log_model import AppLog
from app.models.board_member_model import BoardMember
from app.models.notification_model import Notification
# from app.models import ... (Nanti Anda perlu mengimpor semua file model Anda di sini agar terdeteksi Alembic)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 2. Timpa URL database bawaan alembic.ini dengan URL dari .env kita
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3. Set target_metadata ke Base.metadata milik kita
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """In this scenario we need to create an AsyncEngine
    and associate it with the context.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()