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

    assert set(tables) == {"users", "spaces", "knowledge_bases"}
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
