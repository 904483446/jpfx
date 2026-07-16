from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Document(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_documents_user_id_users",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["space_id", "user_id"],
            ["spaces.id", "spaces.user_id"],
            name="fk_documents_space_owner",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["knowledge_base_id", "space_id", "user_id"],
            [
                "knowledge_bases.id",
                "knowledge_bases.space_id",
                "knowledge_bases.user_id",
            ],
            name="fk_documents_knowledge_base_owner",
            ondelete="CASCADE",
        ),
        CheckConstraint(
            "status IN ('uploaded', 'processing', 'indexed', 'failed')",
            name="ck_documents_status",
        ),
        UniqueConstraint("storage_path", name="uq_documents_storage_path"),
        UniqueConstraint(
            "id",
            "space_id",
            "user_id",
            "knowledge_base_id",
            name="uq_documents_id_space_id_user_id_knowledge_base_id",
        ),
        UniqueConstraint(
            "id",
            "space_id",
            "user_id",
            name="uq_documents_id_space_id_user_id",
        ),
        Index(
            "ix_documents_user_id_space_id_created_at",
            "user_id",
            "space_id",
            "created_at",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    space_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    knowledge_base_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="uploaded", server_default="uploaded"
    )
    error_message: Mapped[str | None] = mapped_column(Text)
