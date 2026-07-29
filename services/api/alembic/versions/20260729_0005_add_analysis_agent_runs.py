"""add analysis agent runs

Revision ID: 20260729_0005
Revises: 20260716_0004
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260729_0005"
down_revision: str | Sequence[str] | None = "20260716_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "analysis_agent_runs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("space_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("agent_key", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("error_message", sa.Text()),
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
            name="fk_analysis_agent_runs_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["space_id", "user_id"],
            ["spaces.id", "spaces.user_id"],
            name="fk_analysis_agent_runs_space_owner",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["task_id", "space_id", "user_id"],
            ["analysis_tasks.id", "analysis_tasks.space_id", "analysis_tasks.user_id"],
            name="fk_analysis_agent_runs_task_owner",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "attempt > 0", name="ck_analysis_agent_runs_attempt_positive"
        ),
        sa.CheckConstraint(
            "agent_key IN ('evidence_collection', 'quality_check', 'model_analysis', 'report_generation')",
            name="ck_analysis_agent_runs_agent_key",
        ),
        sa.CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'failed', 'skipped')",
            name="ck_analysis_agent_runs_status",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_analysis_agent_runs"),
        sa.UniqueConstraint(
            "task_id",
            "attempt",
            "agent_key",
            name="uq_analysis_agent_runs_task_attempt_agent",
        ),
    )
    op.create_index(
        "ix_analysis_agent_runs_task_id_attempt",
        "analysis_agent_runs",
        ["task_id", "attempt"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_analysis_agent_runs_task_id_attempt", table_name="analysis_agent_runs"
    )
    op.drop_table("analysis_agent_runs")
