from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnalysisTaskCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    industry: str = Field(min_length=1, max_length=255)
    product_direction: str = Field(min_length=1, max_length=255)
    keywords: list[str] = Field(default_factory=list, max_length=20)
    known_competitors: list[str] = Field(default_factory=list, max_length=3)
    discovery_mode: Literal["manual", "semi_auto", "auto"] = "semi_auto"

    @field_validator("title", "industry", "product_direction")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("字段不能为空")
        return value

    @field_validator("keywords", "known_competitors")
    @classmethod
    def strip_list_items(cls, values: list[str]) -> list[str]:
        return [value.strip() for value in values if value.strip()]


class CandidateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    source_type: str
    is_selected: bool
    sort_order: int | None


class CompetitorSelectionRequest(BaseModel):
    candidate_ids: list[UUID] = Field(min_length=1, max_length=3)


class AnalysisTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    space_id: UUID
    title: str
    industry: str
    product_direction: str
    keywords: list[str]
    known_competitors: list[str]
    discovery_mode: str
    status: str
    stage: str | None
    completed_at: datetime | None
    final_competitors: list[str]
    candidates: list[CandidateResponse] = Field(default_factory=list)
