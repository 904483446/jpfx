from pydantic import BaseModel, ConfigDict, Field, field_validator


class RetrievalSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=8, ge=1, le=20)

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("检索问题不能为空")
        return value


class RetrievalResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    content: str
    filename: str
    chunk_index: int
    similarity: float


class RetrievalSearchResponse(BaseModel):
    results: list[RetrievalResultResponse]
