from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_optional_text(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip() or None
    return value


class SpaceCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    industry: str | None = Field(default=None, max_length=200)
    product_direction: str | None = Field(default=None, max_length=200)
    description: str | None = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value

    @field_validator("industry", "product_direction", "description", mode="before")
    @classmethod
    def normalize_optional_fields(cls, value: Any) -> Any:
        return normalize_optional_text(value)


class SpaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    industry: str | None
    product_direction: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime
