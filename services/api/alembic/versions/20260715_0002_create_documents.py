"""create documents table

Revision ID: 20260715_0002
Revises: 20260710_0001
Create Date: 2026-07-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260715_0002"
down_revision: str | Sequence[str] | None = "20260710_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_knowledge_bases_id_space_id_user_id",
        "knowledge_bases",
        ["id", "space_id", "user_id"],
    )
    op.create_table(
        "documents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("space_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("knowledge_base_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=10), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=False),
        sa.Column(
            "status", sa.String(length=20), server_default="uploaded", nullable=False
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
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
        sa.CheckConstraint(
            "status IN ('uploaded', 'processing', 'indexed', 'failed')",
            name="ck_documents_status",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_documents_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["space_id", "user_id"],
            ["spaces.id", "spaces.user_id"],
            name="fk_documents_space_owner",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["knowledge_base_id", "space_id", "user_id"],
            [
                "knowledge_bases.id",
                "knowledge_bases.space_id",
                "knowledge_bases.user_id",
            ],
            name="fk_documents_knowledge_base_owner",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_documents"),
        sa.UniqueConstraint("storage_path", name="uq_documents_storage_path"),
    )
    op.create_index(
        "ix_documents_user_id_space_id_created_at",
        "documents",
        ["user_id", "space_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_documents_user_id_space_id_created_at", table_name="documents")
    op.drop_table("documents")
    op.drop_constraint(
        "uq_knowledge_bases_id_space_id_user_id",
        "knowledge_bases",
        type_="unique",
    )
