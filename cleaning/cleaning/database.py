import logging
import os
from functools import cache

from sqlmodel import Session, SQLModel, create_engine

logger = logging.getLogger(__name__)


@cache
def get_engine(echo=False):
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url, echo=echo)
    logger.info(f"using database {engine.url}")
    return engine


def create_schema():
    import cleaning.models  # noqa

    SQLModel.metadata.create_all(get_engine(echo=True))


def get_db():
    with Session(get_engine()) as session:
        yield session


if __name__ == "__main__":
    create_schema()
