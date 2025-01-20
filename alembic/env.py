from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Import your models
from app.models import Base
from app.database import database_url

# Interpret the config file for Python logging.
fileConfig(context.config.config_file_name)

# Set the target metadata for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_online():
    connectable = engine_from_config(
        context.config.get_section(context.config.config_ini_section),
        url=database_url,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()