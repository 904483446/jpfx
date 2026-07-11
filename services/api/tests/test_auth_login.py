import pytest
from app.core.config import settings
from app.db.session import get_db_session
from app.main import app
from app.schemas.auth import RegisterRequest
from app.services.auth_service import register_user
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


@pytest.fixture
def client(database_session: Session, monkeypatch: pytest.MonkeyPatch):
    def override_database_session():
        yield database_session

    monkeypatch.setattr(
        settings,
        "jwt_secret",
        "test-secret-with-at-least-32-bytes",
    )
    monkeypatch.setattr(settings, "auth_cookie_secure", False)
    app.dependency_overrides[get_db_session] = override_database_session
    register_user(
        database_session,
        RegisterRequest(
            email="login@example.com",
            password="correct-password",
            display_name="登录用户",
        ),
    )
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_login_returns_user_and_http_only_cookie(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "  LOGIN@EXAMPLE.COM  ",
            "password": "correct-password",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "login@example.com"
    assert "password_hash" not in response.text
    set_cookie = response.headers["set-cookie"]
    assert "access_token=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie
    assert "Path=/" in set_cookie
    assert "Max-Age=604800" in set_cookie
    assert "Secure" not in set_cookie


def test_login_sets_secure_cookie_when_configured(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(settings, "auth_cookie_secure", True)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "correct-password"},
    )

    assert "Secure" in response.headers["set-cookie"]


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("missing@example.com", "correct-password"),
        ("login@example.com", "wrong-password"),
    ],
)
def test_login_hides_invalid_credential_reason(
    client: TestClient,
    email: str,
    password: str,
):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )

    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "INVALID_CREDENTIALS",
            "message": "邮箱或密码错误",
            "details": {},
        }
    }


def test_login_rejects_invalid_payload(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "not-an-email", "password": "short"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.json()["error"]["message"] == "请求参数校验失败"
