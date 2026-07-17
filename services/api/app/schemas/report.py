from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    space_id: UUID
    task_id: UUID
    title: str
    structured_json: dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime


class ReportEvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_type: str
    source_title: str
    source_url: str | None
    quote: str | None
    retrieved_at: datetime | None
