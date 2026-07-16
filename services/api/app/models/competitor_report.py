from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class CompetitorReport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "competitor_reports"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_competitor_reports_user_id_users",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["space_id", "user_id"],
            ["spaces.id", "spaces.user_id"],
            name="fk_competitor_reports_space_owner",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["task_id", "space_id", "user_id"],
            ["analysis_tasks.id", "analysis_tasks.space_id", "analysis_tasks.user_id"],
            name="fk_competitor_reports_task_owner",
            ondelete="CASCADE",
        ),
        UniqueConstraint("task_id", name="uq_competitor_reports_task_id"),
        Index("ix_competitor_reports_user_id_space_id", "user_id", "space_id"),
    )

    user_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    space_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    task_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    structured_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
