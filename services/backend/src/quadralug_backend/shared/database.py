import logging

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger("quadralug.database")

CONNECT_TIMEOUT_SECONDS = 2


def build_engine(url: str) -> Engine:
    return create_engine(
        url, pool_pre_ping=True, connect_args={"connect_timeout": CONNECT_TIMEOUT_SECONDS}
    )


class SqlDatabaseProbe:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def is_reachable(self) -> bool:
        try:
            with self._engine.connect() as connection:
                connection.execute(text("SELECT 1"))
        except SQLAlchemyError as error:
            logger.warning(
                "database.unreachable", extra={"attributes": {"error.type": type(error).__name__}}
            )
            return False
        return True
