from uuid import UUID

from sqlalchemy import (
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


class CompetitorCandidate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "competitor_candidates"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_competitor_candidates_user_id_users",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["space_id", "user_id"],
            ["spaces.id", "spaces.user_id"],
            name="fk_competitor_candidates_space_owner",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["task_id", "space_id", "user_id"],
            ["analysis_tasks.id", "analysis_tasks.space_id", "analysis_tasks.user_id"],
            name="fk_competitor_candidates_task_owner",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "task_id", "name", name="uq_competitor_candidates_task_id_name"
        ),
        UniqueConstraint(
            "id",
            "task_id",
            "space_id",
            "user_id",
            name="uq_competitor_candidates_id_task_owner",
        ),
        Index("ix_competitor_candidates_task_id", "task_id"),
    )

    user_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    space_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    task_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="manual"
    )
    is_selected: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    sort_order: Mapped[int | None] = mapped_column(Integer)
