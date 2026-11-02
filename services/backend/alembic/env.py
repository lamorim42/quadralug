import os

from alembic import context
from quadralug_backend.shared.database import build_engine


def run_migrations() -> None:
    engine = build_engine(os.environ["DATABASE_URL"])
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()


run_migrations()
