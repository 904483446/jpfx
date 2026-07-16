from pydantic import BaseModel, Field, field_validator


class DeepSeekConfigUpdateRequest(BaseModel):
    api_key: str = Field(min_length=1, max_length=512)

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value: str) -> str:
        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError("API Key 不能为空")
        return normalized_value


class DeepSeekConfigResponse(BaseModel):
    is_configured: bool
    api_key_hint: str | None
    default_model: str = "deepseek-chat"
