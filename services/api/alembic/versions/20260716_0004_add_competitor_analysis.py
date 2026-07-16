"""add competitor analysis tables

Revision ID: 20260716_0004
Revises: 20260716_0003
Create Date: 2026-07-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260716_0004"
down_revision: str | Sequence[str] | None = "20260716_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def uuid_column(name: str) -> sa.Column[object]:
    return sa.Column(name, postgresql.UUID(as_uuid=True), nullable=False)


def timestamps() -> tuple[sa.Column[object], sa.Column[object]]:
    return (
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
    )


def upgrade() -> None:
    op.create_table(
        "model_configs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        uuid_column("user_id"),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("encrypted_api_key", sa.String(length=1024), nullable=False),
        sa.Column("api_key_hint", sa.String(length=32), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_model_configs_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_model_configs"),
        sa.UniqueConstraint(
            "user_id", "provider", name="uq_model_configs_user_id_provider"
        ),
    )
    op.create_index("ix_model_configs_user_id", "model_configs", ["user_id"])

    op.create_table(
        "analysis_tasks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        uuid_column("user_id"),
        uuid_column("space_id"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("industry", sa.String(length=255), nullable=False),
        sa.Column("product_direction", sa.String(length=255), nullable=False),
        sa.Column(
            "keywords",
            postgresql.JSONB(),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "known_competitors",
            postgresql.JSONB(),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "final_competitors",
            postgresql.JSONB(),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "discovery_mode",
            sa.String(length=20),
            server_default="semi_auto",
            nullable=False,
        ),
        sa.Column(
            "status", sa.String(length=20), server_default="draft", nullable=False
        ),
        sa.Column("stage", sa.String(length=50)),
        sa.Column("error_message", sa.Text()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        *timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_analysis_tasks_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["space_id", "user_id"],
            ["spaces.id", "spaces.user_id"],
            name="fk_analysis_tasks_space_owner",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "discovery_mode IN ('manual', 'semi_auto', 'auto')",
            name="ck_analysis_tasks_discovery_mode",
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'queued', 'running', 'completed', 'failed')",
            name="ck_analysis_tasks_status",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_analysis_tasks"),
        sa.UniqueConstraint(
            "id", "space_id", "user_id", name="uq_analysis_tasks_id_space_id_user_id"
        ),
    )
    op.create_index(
        "ix_analysis_tasks_user_id_space_id_created_at",
        "analysis_tasks",
        ["user_id", "space_id", "created_at"],
    )

    op.create_table(
        "competitor_candidates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        uuid_column("user_id"),
        uuid_column("space_id"),
        uuid_column("task_id"),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column(
            "source_type", sa.String(length=30), server_default="manual", nullable=False
        ),
        sa.Column(
            "is_selected", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("sort_order", sa.Integer()),
        *timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_competitor_candidates_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["space_id", "user_id"],
            ["spaces.id", "spaces.user_id"],
            name="fk_competitor_candidates_space_owner",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["task_id", "space_id", "user_id"],
            ["analysis_tasks.id", "analysis_tasks.space_id", "analysis_tasks.user_id"],
            name="fk_competitor_candidates_task_owner",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_competitor_candidates"),
        sa.UniqueConstraint(
            "task_id", "name", name="uq_competitor_candidates_task_id_name"
        ),
        sa.UniqueConstraint(
            "id",
            "task_id",
            "space_id",
            "user_id",
            name="uq_competitor_candidates_id_task_owner",
        ),
    )
    op.create_index(
        "ix_competitor_candidates_task_id", "competitor_candidates", ["task_id"]
    )

    op.create_unique_constraint(
        "uq_documents_id_space_id_user_id",
        "documents",
        ["id", "space_id", "user_id"],
    )
    op.create_unique_constraint(
        "uq_document_chunks_id_space_id_user_id_knowledge_base_id",
        "document_chunks",
        ["id", "space_id", "user_id", "knowledge_base_id"],
    )

    op.create_table(
        "task_evidence",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        uuid_column("user_id"),
        uuid_column("space_id"),
        uuid_column("task_id"),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True)),
        sa.Column("source_type", sa.String(length=30), nullable=False),
        sa.Column("source_title", sa.String(length=500), nullable=False),
        sa.Column("source_url", sa.String(length=2048)),
        sa.Column("document_id", postgresql.UUID(as_uuid=True)),
        sa.Column("chunk_id", postgresql.UUID(as_uuid=True)),
        sa.Column("knowledge_base_id", postgresql.UUID(as_uuid=True)),
        sa.Column("quote", sa.Text()),
        sa.Column("retrieved_at", sa.DateTime(timezone=True)),
        *timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_task_evidence_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["space_id", "user_id"],
            ["spaces.id", "spaces.user_id"],
            name="fk_task_evidence_space_owner",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["task_id", "space_id", "user_id"],
            ["analysis_tasks.id", "analysis_tasks.space_id", "analysis_tasks.user_id"],
            name="fk_task_evidence_task_owner",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["candidate_id", "task_id", "space_id", "user_id"],
            [
                "competitor_candidates.id",
                "competitor_candidates.task_id",
                "competitor_candidates.space_id",
                "competitor_candidates.user_id",
            ],
            name="fk_task_evidence_candidate_owner",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["document_id", "space_id", "user_id"],
            ["documents.id", "documents.space_id", "documents.user_id"],
            name="fk_task_evidence_document_owner",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["chunk_id", "space_id", "user_id", "knowledge_base_id"],
            [
                "document_chunks.id",
                "document_chunks.space_id",
                "document_chunks.user_id",
                "document_chunks.knowledge_base_id",
            ],
            name="fk_task_evidence_chunk_owner",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "source_type IN ('web', 'private_knowledge', 'model_inference')",
            name="ck_task_evidence_source_type",
        ),
        sa.CheckConstraint(
            "chunk_id IS NULL OR knowledge_base_id IS NOT NULL",
            name="ck_task_evidence_chunk_knowledge_base",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_task_evidence"),
    )
    op.create_index("ix_task_evidence_task_id", "task_evidence", ["task_id"])

    op.create_table(
        "competitor_reports",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        uuid_column("user_id"),
        uuid_column("space_id"),
        uuid_column("task_id"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("structured_json", postgresql.JSONB(), nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_competitor_reports_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["space_id", "user_id"],
            ["spaces.id", "spaces.user_id"],
            name="fk_competitor_reports_space_owner",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["task_id", "space_id", "user_id"],
            ["analysis_tasks.id", "analysis_tasks.space_id", "analysis_tasks.user_id"],
            name="fk_competitor_reports_task_owner",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_competitor_reports"),
        sa.UniqueConstraint("task_id", name="uq_competitor_reports_task_id"),
    )
    op.create_index(
        "ix_competitor_reports_user_id_space_id",
        "competitor_reports",
        ["user_id", "space_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_competitor_reports_user_id_space_id", table_name="competitor_reports"
    )
    op.drop_table("competitor_reports")
    op.drop_index("ix_task_evidence_task_id", table_name="task_evidence")
    op.drop_table("task_evidence")
    op.execute(
        "ALTER TABLE documents "
        "DROP CONSTRAINT IF EXISTS uq_documents_id_space_id_user_id"
    )
    op.execute(
        "ALTER TABLE document_chunks "
        "DROP CONSTRAINT IF EXISTS "
        "uq_document_chunks_id_space_id_user_id_knowledge_base_id"
    )
    op.drop_index(
        "ix_competitor_candidates_task_id", table_name="competitor_candidates"
    )
    op.drop_table("competitor_candidates")
    op.drop_index(
        "ix_analysis_tasks_user_id_space_id_created_at", table_name="analysis_tasks"
    )
    op.drop_table("analysis_tasks")
    op.drop_index("ix_model_configs_user_id", table_name="model_configs")
    op.drop_table("model_configs")
