from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
import pytest
from app.core.config import settings
from app.db.session import get_db_session
from app.main import app
from app.schemas.auth import RegisterRequest
from app.services.auth_service import register_user
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

TEST_SECRET = "test-secret-with-at-least-32-bytes"
OTHER_SECRET = "other-secret-with-at-least-32-bytes"
UNAUTHORIZED_RESPONSE = {
    "error": {
        "code": "UNAUTHORIZED",
        "message": "登录状态无效或已过期",
        "details": {},
    }
}


def issue_token(
    claims: dict[str, object],
    *,
    secret: str = TEST_SECRET,
) -> str:
    return jwt.encode(claims, secret, algorithm="HS256")


def valid_claims(user_id: UUID) -> dict[str, object]:
    now = datetime.now(UTC)
    return {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(days=1),
    }


@pytest.fixture
def client(
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    def override_database_session() -> Generator[Session, None, None]:
        yield database_session

    monkeypatch.setattr(settings, "jwt_secret", TEST_SECRET)
    monkeypatch.setattr(settings, "auth_cookie_secure", False)
    app.dependency_overrides[get_db_session] = override_database_session
    register_user(
        database_session,
        RegisterRequest(
            email="me@example.com",
            password="correct-password",
            display_name="当前用户",
        ),
    )
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_me_returns_logged_in_user_without_sensitive_fields(client: TestClient):
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "correct-password"},
    )
    assert login_response.status_code == 200

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"
    assert response.json()["display_name"] == "当前用户"
    assert response.json()["is_admin"] is False
    assert "password" not in response.text
    assert "password_hash" not in response.text
    assert "access_token" not in response.text
    assert "set-cookie" not in response.headers


@pytest.mark.parametrize(
    "token",
    [
        None,
        issue_token(valid_claims(uuid4()), secret=OTHER_SECRET),
        issue_token(
            {
                "sub": str(uuid4()),
                "exp": datetime.now(UTC) - timedelta(seconds=1),
            }
        ),
        issue_token({"exp": datetime.now(UTC) + timedelta(days=1)}),
        issue_token(
            {
                "sub": "not-a-uuid",
                "exp": datetime.now(UTC) + timedelta(days=1),
            }
        ),
        issue_token(
            {
                "sub": str(uuid4()),
                "exp": datetime.now(UTC) + timedelta(days=1),
            }
        ),
    ],
)
def test_me_returns_uniform_error_for_invalid_authentication(
    client: TestClient,
    token: str | None,
):
    if token is not None:
        client.cookies.set(settings.auth_cookie_name, token)

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json() == UNAUTHORIZED_RESPONSE
    assert "set-cookie" not in response.headers
