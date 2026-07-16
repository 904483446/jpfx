from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class TaskEvidence(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "task_evidence"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_task_evidence_user_id_users",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["space_id", "user_id"],
            ["spaces.id", "spaces.user_id"],
            name="fk_task_evidence_space_owner",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["task_id", "space_id", "user_id"],
            ["analysis_tasks.id", "analysis_tasks.space_id", "analysis_tasks.user_id"],
            name="fk_task_evidence_task_owner",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
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
        ForeignKeyConstraint(
            ["document_id", "space_id", "user_id"],
            ["documents.id", "documents.space_id", "documents.user_id"],
            name="fk_task_evidence_document_owner",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
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
        CheckConstraint(
            "source_type IN ('web', 'private_knowledge', 'model_inference')",
            name="ck_task_evidence_source_type",
        ),
        CheckConstraint(
            "chunk_id IS NULL OR knowledge_base_id IS NOT NULL",
            name="ck_task_evidence_chunk_knowledge_base",
        ),
        Index("ix_task_evidence_task_id", "task_id"),
    )

    user_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    space_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    task_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    candidate_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True))
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(2048))
    document_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True))
    chunk_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True))
    knowledge_base_id: Mapped[UUID | None] = mapped_column(PostgreSQLUUID(as_uuid=True))
    quote: Mapped[str | None] = mapped_column(Text)
    retrieved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
