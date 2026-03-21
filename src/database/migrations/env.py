"""Alembic environment configuration.

Uses a synchronous engine for migrations while the application uses async.
Imports all SQLAlchemy models so that autogenerate can detect schema changes.
"""

from __future__ import annotations

import sys
import os
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# ---------------------------------------------------------------------------
# Ensure src/ is on sys.path so model imports resolve correctly
# ---------------------------------------------------------------------------
src_path = str(Path(__file__).resolve().parents[3] / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# ---------------------------------------------------------------------------
# Import Base and all models (required for autogenerate)
# ---------------------------------------------------------------------------
from database.models import (  # noqa: E402, F401
    Base,
    Person,
    Message,
    Observation,
    Episode,
    EpisodeMessage,
    Reflection,
    ReflectionSource,
    Tag,
    TagMessage,
    TagObservation,
    TagReflection,
    TagEpisode,
    EmotionRecord,
    Interest,
    DialoguePlan,
    UserPortrait,
    MemoryAccessHistory,
)
from core.config import get_settings  # noqa: E402

# ---------------------------------------------------------------------------
# Alembic Config
# ---------------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url with the sync URL from application settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.db.sync_url)

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Migration runners
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no DB connection required)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (synchronous engine)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
