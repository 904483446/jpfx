from pathlib import Path

from alembic import command
from alembic.config import Config
from app.core.config import Settings
from sqlalchemy import create_engine, inspect, text

API_ROOT = Path(__file__).resolve().parents[1]


def test_initial_migration_round_trip_on_empty_test_database():
    alembic_ini = API_ROOT / "alembic.ini"
    assert alembic_ini.is_file()

    database_url = Settings().test_database_url
    assert database_url is not None
    configuration = Config(str(alembic_ini))
    configuration.set_main_option("sqlalchemy.url", database_url)

    command.downgrade(configuration, "base")
    command.upgrade(configuration, "head")

    engine = create_engine(database_url)
    try:
        inspector = inspect(engine)
        assert {
            "users",
            "spaces",
            "knowledge_bases",
            "documents",
            "document_chunks",
        }.issubset(
            inspector.get_table_names()
        )
        document_chunks = {
            column["name"]: column for column in inspector.get_columns("document_chunks")
        }
        assert str(document_chunks["embedding"]["type"]) == "VECTOR(1024)"
        unique_constraints = inspector.get_unique_constraints("document_chunks")
        assert {"document_id", "chunk_index"} in {
            set(constraint["column_names"]) for constraint in unique_constraints
        }
        with engine.connect() as connection:
            extensions = set(
                connection.execute(
                    text(
                        "SELECT extname FROM pg_extension "
                        "WHERE extname IN ('uuid-ossp', 'vector')"
                    )
                ).scalars()
            )
        assert extensions == {"uuid-ossp", "vector"}

        command.downgrade(configuration, "base")
        assert not {
            "users",
            "spaces",
            "knowledge_bases",
            "documents",
            "document_chunks",
        }.intersection(
            inspect(engine).get_table_names()
        )
        with engine.connect() as connection:
            retained_extensions = set(
                connection.execute(
                    text(
                        "SELECT extname FROM pg_extension "
                        "WHERE extname IN ('uuid-ossp', 'vector')"
                    )
                ).scalars()
            )
        assert retained_extensions == {"uuid-ossp", "vector"}

        command.upgrade(configuration, "head")
    finally:
        engine.dispose()
