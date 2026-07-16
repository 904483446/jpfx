import importlib

import pytest
from app.core.config import Settings
from sqlalchemy import text


def test_settings_load_database_urls_from_environment(monkeypatch):
    database_url = "postgresql+psycopg://user:password@localhost:5432/app"
    test_database_url = "postgresql+psycopg://user:password@localhost:5433/app_test"
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("TEST_DATABASE_URL", test_database_url)

    configured = Settings(_env_file=None)

    assert configured.database_url == database_url
    assert configured.test_database_url == test_database_url


def test_get_engine_rejects_missing_database_url():
    session_module = importlib.import_module("app.db.session")

    with pytest.raises(RuntimeError, match="DATABASE_URL 未配置"):
        session_module.get_engine("")


def test_session_factory_connects_to_test_database():
    session_module = importlib.import_module("app.db.session")
    test_database_url = Settings().test_database_url
    assert test_database_url is not None

    engine = session_module.get_engine(test_database_url)
    session_factory = session_module.get_session_factory(test_database_url)

    try:
        with session_factory() as database_session:
            assert database_session.execute(text("SELECT 1")).scalar_one() == 1
    finally:
        engine.dispose()


def test_engine_registers_pgvector_adapter_for_psycopg_connections(
    monkeypatch: pytest.MonkeyPatch,
):
    session_module = importlib.import_module("app.db.session")
    test_database_url = Settings().test_database_url
    assert test_database_url is not None
    registered_connections = []
    monkeypatch.setattr(
        session_module,
        "register_vector",
        lambda connection: registered_connections.append(connection),
    )
    session_module.get_engine.cache_clear()
    try:
        with session_module.get_engine(test_database_url).connect() as connection:
            connection.execute(text("SELECT 1"))
    finally:
        session_module.get_engine.cache_clear()

    assert len(registered_connections) == 1
