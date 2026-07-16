import importlib

from app.db.base import Base
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID


def load_model_tables():
    importlib.import_module("app.models")
    return Base.metadata.tables


def unique_column_sets(table) -> set[tuple[str, ...]]:
    return {
        tuple(constraint.columns.keys())
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }


def test_base_models_define_required_tables_and_columns():
    tables = load_model_tables()

    assert set(tables) == {
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
    }
    assert set(tables["users"].columns.keys()) == {
        "id",
        "email",
        "password_hash",
        "display_name",
        "is_admin",
        "created_at",
        "updated_at",
    }
    assert set(tables["spaces"].columns.keys()) == {
        "id",
        "user_id",
        "name",
        "industry",
        "product_direction",
        "description",
        "created_at",
        "updated_at",
        "deleted_at",
    }
    assert set(tables["knowledge_bases"].columns.keys()) == {
        "id",
        "user_id",
        "space_id",
        "name",
        "description",
        "created_at",
        "updated_at",
    }
    assert set(tables["documents"].columns.keys()) == {
        "id",
        "user_id",
        "space_id",
        "knowledge_base_id",
        "filename",
        "file_type",
        "file_size",
        "storage_path",
        "status",
        "error_message",
        "created_at",
        "updated_at",
    }
    assert set(tables["document_chunks"].columns.keys()) == {
        "id",
        "user_id",
        "space_id",
        "knowledge_base_id",
        "document_id",
        "chunk_index",
        "content",
        "embedding",
        "metadata",
        "created_at",
        "updated_at",
    }
    assert set(tables["model_configs"].columns.keys()) == {
        "id",
        "user_id",
        "provider",
        "encrypted_api_key",
        "api_key_hint",
        "created_at",
        "updated_at",
    }


def test_primary_keys_use_postgresql_uuid_with_application_and_server_defaults():
    tables = load_model_tables()

    for table in tables.values():
        primary_key = table.c.id
        assert isinstance(primary_key.type, PostgreSQLUUID)
        assert primary_key.default is not None
        assert primary_key.server_default is not None
        assert "uuid_generate_v4()" in str(primary_key.server_default.arg)


def test_user_and_space_constraints_support_isolation():
    tables = load_model_tables()
    users = tables["users"]
    spaces = tables["spaces"]

    assert ("email",) in unique_column_sets(users)
    assert ("id", "user_id") in unique_column_sets(spaces)
    assert ("user_id",) in {tuple(index.columns.keys()) for index in spaces.indexes}

    user_foreign_key = next(iter(spaces.c.user_id.foreign_keys))
    assert user_foreign_key.target_fullname == "users.id"
    assert user_foreign_key.ondelete == "CASCADE"


def test_knowledge_base_constraints_enforce_one_owner_and_one_per_space():
    knowledge_bases = load_model_tables()["knowledge_bases"]

    assert ("space_id",) in unique_column_sets(knowledge_bases)
    composite_foreign_keys = {
        (
            tuple(constraint.column_keys),
            tuple(element.target_fullname for element in constraint.elements),
        )
        for constraint in knowledge_bases.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }
    assert (
        ("space_id", "user_id"),
        ("spaces.id", "spaces.user_id"),
    ) in composite_foreign_keys

    user_foreign_key = next(
        foreign_key
        for foreign_key in knowledge_bases.c.user_id.foreign_keys
        if foreign_key.target_fullname == "users.id"
    )
    assert user_foreign_key.target_fullname == "users.id"
    assert user_foreign_key.ondelete == "CASCADE"
    assert ("id", "space_id", "user_id") in unique_column_sets(knowledge_bases)


def test_document_constraints_keep_document_with_its_owner_space_and_knowledge_base():
    documents = load_model_tables()["documents"]

    composite_foreign_keys = {
        (
            tuple(constraint.column_keys),
            tuple(element.target_fullname for element in constraint.elements),
        )
        for constraint in documents.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }
    assert (
        ("space_id", "user_id"),
        ("spaces.id", "spaces.user_id"),
    ) in composite_foreign_keys
    assert (
        ("knowledge_base_id", "space_id", "user_id"),
        (
            "knowledge_bases.id",
            "knowledge_bases.space_id",
            "knowledge_bases.user_id",
        ),
    ) in composite_foreign_keys
    assert documents.c.status.default.arg == "uploaded"


def test_document_chunks_are_bound_to_their_owner_document_and_knowledge_base():
    document_chunks = load_model_tables()["document_chunks"]

    assert ("document_id", "chunk_index") in unique_column_sets(document_chunks)
    assert (
        "id",
        "space_id",
        "user_id",
        "knowledge_base_id",
    ) in unique_column_sets(document_chunks)
    assert str(document_chunks.c.embedding.type).lower() == "vector(1024)"
    composite_foreign_keys = {
        (
            tuple(constraint.column_keys),
            tuple(element.target_fullname for element in constraint.elements),
        )
        for constraint in document_chunks.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }
    assert (
        ("space_id", "user_id"),
        ("spaces.id", "spaces.user_id"),
    ) in composite_foreign_keys
    assert (
        ("knowledge_base_id", "space_id", "user_id"),
        (
            "knowledge_bases.id",
            "knowledge_bases.space_id",
            "knowledge_bases.user_id",
        ),
    ) in composite_foreign_keys
    assert (
        ("document_id", "space_id", "user_id", "knowledge_base_id"),
        (
            "documents.id",
            "documents.space_id",
            "documents.user_id",
            "documents.knowledge_base_id",
        ),
    ) in composite_foreign_keys


def test_competitor_analysis_models_are_bound_to_their_owner_space_and_task():
    tables = load_model_tables()
    model_configs = tables["model_configs"]
    analysis_tasks = tables["analysis_tasks"]
    candidates = tables["competitor_candidates"]
    evidence = tables["task_evidence"]
    reports = tables["competitor_reports"]

    assert ("user_id", "provider") in unique_column_sets(model_configs)
    assert "api_key" not in model_configs.c
    assert {"encrypted_api_key", "api_key_hint"}.issubset(model_configs.c.keys())
    checks = {
        constraint.name: str(constraint.sqltext)
        for constraint in analysis_tasks.constraints
        if constraint.__class__.__name__ == "CheckConstraint"
    }
    assert checks["ck_analysis_tasks_status"] == (
        "status IN ('draft', 'queued', 'running', 'completed', 'failed')"
    )
    evidence_checks = {
        constraint.name: str(constraint.sqltext)
        for constraint in evidence.constraints
        if constraint.__class__.__name__ == "CheckConstraint"
    }
    assert evidence_checks["ck_task_evidence_chunk_knowledge_base"] == (
        "chunk_id IS NULL OR knowledge_base_id IS NOT NULL"
    )

    for table in (analysis_tasks, candidates, evidence, reports):
        composite_foreign_keys = {
            (
                tuple(constraint.column_keys),
                tuple(element.target_fullname for element in constraint.elements),
            )
            for constraint in table.constraints
            if isinstance(constraint, ForeignKeyConstraint)
        }
        assert (
            ("space_id", "user_id"),
            ("spaces.id", "spaces.user_id"),
        ) in composite_foreign_keys

    candidate_foreign_keys = {
        (
            tuple(constraint.column_keys),
            tuple(element.target_fullname for element in constraint.elements),
        )
        for constraint in candidates.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }
    assert (
        ("task_id", "space_id", "user_id"),
        ("analysis_tasks.id", "analysis_tasks.space_id", "analysis_tasks.user_id"),
    ) in candidate_foreign_keys
    evidence_foreign_keys = {
        (
            tuple(constraint.column_keys),
            tuple(element.target_fullname for element in constraint.elements),
        )
        for constraint in evidence.constraints
        if isinstance(constraint, ForeignKeyConstraint)
    }
    assert (
        ("document_id", "space_id", "user_id"),
        ("documents.id", "documents.space_id", "documents.user_id"),
    ) in evidence_foreign_keys
    assert (
        ("chunk_id", "space_id", "user_id", "knowledge_base_id"),
        (
            "document_chunks.id",
            "document_chunks.space_id",
            "document_chunks.user_id",
            "document_chunks.knowledge_base_id",
        ),
    ) in evidence_foreign_keys
    assert evidence.c.source_type.type.length == 30
    assert "knowledge_base_id" in evidence.c
    assert "structured_json" in reports.c
