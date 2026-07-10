from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def _resolve_database_url(database_url: str | None) -> str:
    resolved_url = settings.database_url if database_url is None else database_url
    if not resolved_url:
        raise RuntimeError("DATABASE_URL 未配置")
    return resolved_url


@lru_cache
def get_engine(database_url: str | None = None) -> Engine:
    return create_engine(
        _resolve_database_url(database_url),
        pool_pre_ping=True,
    )


@lru_cache
def get_session_factory(
    database_url: str | None = None,
) -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(database_url),
        autoflush=False,
        expire_on_commit=False,
    )


def get_db_session() -> Generator[Session, None, None]:
    session_factory = get_session_factory()
    with session_factory() as database_session:
        yield database_session
