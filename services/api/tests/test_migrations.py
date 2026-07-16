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
            "model_configs",
            "analysis_tasks",
            "competitor_candidates",
            "task_evidence",
            "competitor_reports",
        }.issubset(inspector.get_table_names())
        unique_constraints = inspector.get_unique_constraints("document_chunks")
        assert frozenset({"document_id", "chunk_index"}) in {
            frozenset(constraint["column_names"]) for constraint in unique_constraints
        }
        evidence_foreign_keys = {
            (
                tuple(foreign_key["constrained_columns"]),
                foreign_key["referred_table"],
                tuple(foreign_key["referred_columns"]),
            )
            for foreign_key in inspector.get_foreign_keys("task_evidence")
        }
        assert (
            ("document_id", "space_id", "user_id"),
            "documents",
            ("id", "space_id", "user_id"),
        ) in evidence_foreign_keys
        evidence_checks = {
            constraint["name"]: constraint["sqltext"]
            for constraint in inspector.get_check_constraints("task_evidence")
        }
        assert evidence_checks["ck_task_evidence_chunk_knowledge_base"] == (
            "chunk_id IS NULL OR knowledge_base_id IS NOT NULL"
        )
        assert (
            ("chunk_id", "space_id", "user_id", "knowledge_base_id"),
            "document_chunks",
            ("id", "space_id", "user_id", "knowledge_base_id"),
        ) in evidence_foreign_keys
        with engine.connect() as connection:
            embedding_type = connection.scalar(
                text(
                    "SELECT format_type(a.atttypid, a.atttypmod) "
                    "FROM pg_attribute a "
                    "JOIN pg_class c ON c.oid = a.attrelid "
                    "WHERE c.relname = 'document_chunks' "
                    "AND a.attname = 'embedding'"
                )
            )
            assert embedding_type == "vector(1024)"
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
            "model_configs",
            "analysis_tasks",
            "competitor_candidates",
            "task_evidence",
            "competitor_reports",
        }.intersection(inspect(engine).get_table_names())
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
