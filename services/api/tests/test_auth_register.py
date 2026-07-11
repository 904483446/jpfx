import pytest
from app.db.session import get_db_session
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def client(database_session: Session):
    def override_database_session():
        yield database_session

    app.dependency_overrides[get_db_session] = override_database_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_register_returns_created_user_without_password(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "  ApiUser@Example.com  ",
            "password": "valid-password",
            "display_name": "  API 用户  ",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["email"] == "apiuser@example.com"
    assert payload["display_name"] == "API 用户"
    assert payload["is_admin"] is False
    assert payload["id"]
    assert payload["created_at"]
    assert payload["updated_at"]
    assert "password" not in payload
    assert "password_hash" not in payload


def test_register_rejects_case_insensitive_duplicate(client: TestClient):
    first = {
        "email": "duplicate@example.com",
        "password": "valid-password",
        "display_name": "用户一",
    }
    assert client.post("/api/v1/auth/register", json=first).status_code == 201

    second = {
        **first,
        "email": "  DUPLICATE@EXAMPLE.COM  ",
        "display_name": "用户二",
    }
    response = client.post("/api/v1/auth/register", json=second)

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "EMAIL_ALREADY_REGISTERED",
            "message": "该邮箱已注册",
            "details": {},
        }
    }


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
def test_register_rejects_invalid_payload(
    client: TestClient,
    field: str,
    value: str,
):
    request_body = {
        "email": "validation@example.com",
        "password": "valid-password",
        "display_name": "校验用户",
    }
    request_body[field] = value

    response = client.post("/api/v1/auth/register", json=request_body)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.json()["error"]["message"] == "请求参数校验失败"
