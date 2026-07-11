import pytest
from app.schemas.auth import LoginRequest
from pydantic import ValidationError


def test_login_request_normalizes_email():
    payload = LoginRequest(
        email="  User@Example.COM  ",
        password="valid-password",
    )

    assert str(payload.email) == "user@example.com"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("email", ""),
        ("email", "not-an-email"),
        ("password", "short"),
        ("password", "x" * 129),
    ],
)
def test_login_request_rejects_invalid_fields(field: str, value: str):
    data = {"email": "user@example.com", "password": "valid-password"}
    data[field] = value

    with pytest.raises(ValidationError):
        LoginRequest(**data)
