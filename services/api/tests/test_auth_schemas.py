import importlib

import pytest
from pydantic import ValidationError


def register_request_type():
    return importlib.import_module("app.schemas.auth").RegisterRequest


def test_register_request_normalizes_email_and_display_name():
    payload = register_request_type()(
        email="  User@Example.COM  ",
        password="valid-password",
        display_name="  示例用户  ",
    )

    assert str(payload.email) == "user@example.com"
    assert payload.display_name == "示例用户"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("email", ""),
        ("email", "not-an-email"),
        ("password", "short"),
        ("password", "x" * 129),
        ("display_name", "   "),
        ("display_name", "名" * 101),
    ],
)
def test_register_request_rejects_invalid_fields(field: str, value: str):
    data = {
        "email": "user@example.com",
        "password": "valid-password",
        "display_name": "示例用户",
    }
    data[field] = value

    with pytest.raises(ValidationError):
        register_request_type()(**data)
