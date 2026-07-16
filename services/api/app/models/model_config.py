from uuid import UUID

from sqlalchemy import ForeignKeyConstraint, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ModelConfig(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "model_configs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_model_configs_user_id_users",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "user_id", "provider", name="uq_model_configs_user_id_provider"
        ),
        Index("ix_model_configs_user_id", "user_id"),
    )

    user_id: Mapped[UUID] = mapped_column(PostgreSQLUUID(as_uuid=True), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    encrypted_api_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    api_key_hint: Mapped[str] = mapped_column(String(32), nullable=False)
