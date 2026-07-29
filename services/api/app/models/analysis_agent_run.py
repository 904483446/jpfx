from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

AGENT_KEYS = (
    "evidence_collection",
    "quality_check",
    "model_analysis",
    "report_generation",
)
AGENT_RUN_STATUSES = ("queued", "running", "completed", "failed", "skipped")


class AnalysisAgentRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "analysis_agent_runs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_analysis_agent_runs_user_id_users",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["space_id", "user_id"],
            ["spaces.id", "spaces.user_id"],
            name="fk_analysis_agent_runs_space_owner",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["task_id", "space_id", "user_id"],
            ["analysis_tasks.id", "analysis_tasks.space_id", "analysis_tasks.user_id"],
            name="fk_analysis_agent_runs_task_owner",
            ondelete="CASCADE",
        ),
        CheckConstraint("attempt > 0", name="ck_analysis_agent_runs_attempt_positive"),
        CheckConstraint(
            "agent_key IN ('evidence_collection', 'quality_check', 'model_analysis', 'report_generation')",
            name="ck_analysis_agent_runs_agent_key",
        ),
        CheckConstraint(
            "status IN ('queued', 'running', 'completed', 'failed', 'skipped')",
            name="ck_analysis_agent_runs_status",
        ),
        UniqueConstraint(
            "task_id",
            "attempt",
            "agent_key",
            name="uq_analysis_agent_runs_task_attempt_agent",
        ),
        Index("ix_analysis_agent_runs_task_id_attempt", "task_id", "attempt"),
    )

    user_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    space_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    task_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False)
    agent_key: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
