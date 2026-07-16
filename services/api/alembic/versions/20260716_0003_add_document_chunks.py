"""add document chunks

Revision ID: 20260716_0003
Revises: 20260715_0002
Create Date: 2026-07-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import UserDefinedType

revision: str = "20260716_0003"
down_revision: str | Sequence[str] | None = "20260715_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


class Vector(UserDefinedType[list[float]]):
    cache_ok = True

    def get_col_spec(self, **_kw: object) -> str:
        return "vector(1024)"


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_unique_constraint(
        "uq_documents_id_space_id_user_id_knowledge_base_id",
        "documents",
        ["id", "space_id", "user_id", "knowledge_base_id"],
    )
    op.create_table(
        "document_chunks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("space_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("knowledge_base_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_document_chunks_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["space_id", "user_id"],
            ["spaces.id", "spaces.user_id"],
            name="fk_document_chunks_space_owner",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["knowledge_base_id", "space_id", "user_id"],
            [
                "knowledge_bases.id",
                "knowledge_bases.space_id",
                "knowledge_bases.user_id",
            ],
            name="fk_document_chunks_knowledge_base_owner",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["document_id", "space_id", "user_id", "knowledge_base_id"],
            [
                "documents.id",
                "documents.space_id",
                "documents.user_id",
                "documents.knowledge_base_id",
            ],
            name="fk_document_chunks_document_owner",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_document_chunks"),
        sa.UniqueConstraint(
            "document_id",
            "chunk_index",
            name="uq_document_chunks_document_id_chunk_index",
        ),
    )
    op.create_index(
        "ix_document_chunks_user_id_space_id",
        "document_chunks",
        ["user_id", "space_id"],
    )
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.drop_index("ix_document_chunks_embedding_hnsw", table_name="document_chunks")
    op.drop_index("ix_document_chunks_user_id_space_id", table_name="document_chunks")
    op.drop_table("document_chunks")
    op.drop_constraint(
        "uq_documents_id_space_id_user_id_knowledge_base_id",
        "documents",
        type_="unique",
    )
