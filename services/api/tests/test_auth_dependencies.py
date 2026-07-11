from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID, uuid4

import jwt
import pytest
from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db_session
from app.main import create_app
from app.models import User
from app.schemas.auth import RegisterRequest
from app.services.auth_service import register_user
from fastapi import Depends, FastAPI
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
def application(
    database_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[FastAPI, None, None]:
    monkeypatch.setattr(settings, "jwt_secret", TEST_SECRET)
    application = create_app()

    def override_database_session() -> Generator[Session, None, None]:
        yield database_session

    @application.get("/protected-probe")
    def protected_probe(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> dict[str, str]:
        return {"user_id": str(current_user.id)}

    application.dependency_overrides[get_db_session] = override_database_session
    try:
        yield application
    finally:
        application.dependency_overrides.clear()


def test_get_current_user_returns_database_user(
    application: FastAPI,
    database_session: Session,
):
    user = register_user(
        database_session,
        RegisterRequest(
            email="dependency@example.com",
            password="valid-password",
            display_name="依赖用户",
        ),
    )

    client = TestClient(application)
    client.cookies.set(settings.auth_cookie_name, issue_token(valid_claims(user.id)))

    response = client.get("/protected-probe")

    assert response.status_code == 200
    assert response.json() == {"user_id": str(user.id)}


@pytest.mark.parametrize(
    "token",
    [
        None,
        "not.a.jwt",
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
def test_protected_probe_returns_uniform_error_for_invalid_authentication(
    application: FastAPI,
    token: str | None,
):
    client = TestClient(application)
    if token is not None:
        client.cookies.set(settings.auth_cookie_name, token)

    response = client.get("/protected-probe")

    assert response.status_code == 401
    assert response.json() == UNAUTHORIZED_RESPONSE


def test_weak_jwt_secret_is_a_server_configuration_error(
    application: FastAPI,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(settings, "jwt_secret", "x" * 31)
    token = issue_token(valid_claims(uuid4()))

    client = TestClient(application, raise_server_exceptions=False)
    client.cookies.set(settings.auth_cookie_name, token)

    response = client.get("/protected-probe")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"
