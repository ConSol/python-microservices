import logging
import os
from functools import cache
from typing import Generator

from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

logger = logging.getLogger(__name__)


@cache
def get_engine():
    database_url = os.environ["DATABASE_URL"]
    engine = create_engine(database_url)
    logger.info(f"using database {engine.url}")
    SQLAlchemyInstrumentor().instrument(engine=engine)
    return engine


def get_db() -> Generator:
    with Session(get_engine()) as session:
        yield session


def create_schema():
    import dispo.models  # noqa

    SQLModel.metadata.create_all(get_engine())


if __name__ == "__main__":
    # could be explicitly called with
    # kubectl exec deploy/dispo -- bash -c '. /venv/bin/activate && python -m dispo.database'      # noqa: E501
    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    create_schema()
