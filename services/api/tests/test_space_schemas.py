import pytest
from app.schemas.space import SpaceCreateRequest
from pydantic import ValidationError


def test_space_create_normalizes_optional_fields_to_none():
    payload = SpaceCreateRequest(
        name="  企业知识库 Copilot  ",
        industry="  ",
        product_direction=" AI 知识库 ",
        description="  ",
    )

    assert payload.name == "企业知识库 Copilot"
    assert payload.industry is None
    assert payload.product_direction == "AI 知识库"
    assert payload.description is None


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "   "},
        {"name": "x" * 201},
        {"name": "valid", "industry": "x" * 201},
        {"name": "valid", "product_direction": "x" * 201},
    ],
)
def test_space_create_rejects_invalid_text_lengths(payload: dict[str, str]):
    with pytest.raises(ValidationError):
        SpaceCreateRequest(**payload)
