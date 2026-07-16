from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class AnalysisTask(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "analysis_tasks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_analysis_tasks_user_id_users",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["space_id", "user_id"],
            ["spaces.id", "spaces.user_id"],
            name="fk_analysis_tasks_space_owner",
            ondelete="CASCADE",
        ),
        CheckConstraint(
            "discovery_mode IN ('manual', 'semi_auto', 'auto')",
            name="ck_analysis_tasks_discovery_mode",
        ),
        CheckConstraint(
            "status IN ('draft', 'queued', 'running', 'completed', 'failed')",
            name="ck_analysis_tasks_status",
        ),
        UniqueConstraint(
            "id", "space_id", "user_id", name="uq_analysis_tasks_id_space_id_user_id"
        ),
        Index(
            "ix_analysis_tasks_user_id_space_id_created_at",
            "user_id",
            "space_id",
            "created_at",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    space_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(255), nullable=False)
    product_direction: Mapped[str] = mapped_column(String(255), nullable=False)
    keywords: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    known_competitors: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    final_competitors: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default="[]"
    )
    discovery_mode: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="semi_auto"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="draft"
    )
    stage: Mapped[str | None] = mapped_column(String(50))
    error_message: Mapped[str | None] = mapped_column(Text)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
