from collections.abc import Generator
from uuid import uuid4

import pytest
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import app
from app.schemas.auth import RegisterRequest
from app.services.auth_service import register_user
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

TEST_SECRET = "test-secret-with-at-least-32-bytes"


@pytest.fixture
def client(
    database_session: Session, monkeypatch: pytest.MonkeyPatch
) -> Generator[TestClient, None, None]:
    def override_database_session() -> Generator[Session, None, None]:
        yield database_session

    monkeypatch.setattr(settings, "jwt_secret", TEST_SECRET)
    app.dependency_overrides[get_db_session] = override_database_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def authenticate(client: TestClient, database_session: Session, email: str):
    user = register_user(
        database_session,
        RegisterRequest(
            email=email, password="valid-password", display_name="空间用户"
        ),
    )
    client.cookies.set(settings.auth_cookie_name, create_access_token(user.id))
    return user


def test_spaces_require_authentication(client: TestClient):
    assert client.get("/api/v1/spaces").status_code == 401
    assert client.post("/api/v1/spaces", json={"name": "空间"}).status_code == 401
    assert client.get(f"/api/v1/spaces/{uuid4()}").status_code == 401


def test_create_list_and_get_current_user_space(
    client: TestClient, database_session: Session
):
    authenticate(client, database_session, "spaces@example.com")
    created = client.post(
        "/api/v1/spaces", json={"name": " 企业知识库 Copilot ", "industry": "  "}
    )
    assert created.status_code == 201
    payload = created.json()
    assert payload["name"] == "企业知识库 Copilot"
    assert payload["industry"] is None
    assert "user_id" not in payload and "deleted_at" not in payload
    assert client.get("/api/v1/spaces").json() == [payload]
    assert client.get(f"/api/v1/spaces/{payload['id']}").json() == payload


def test_current_user_cannot_read_another_users_space(
    client: TestClient,
    database_session: Session,
):
    owner = authenticate(client, database_session, "owner@example.com")
    owner_space = client.post("/api/v1/spaces", json={"name": "Owner 空间"}).json()
    other_user = register_user(
        database_session,
        RegisterRequest(
            email="other@example.com",
            password="valid-password",
            display_name="其他用户",
        ),
    )
    client.cookies.set(settings.auth_cookie_name, create_access_token(other_user.id))

    response = client.get(f"/api/v1/spaces/{owner_space['id']}")

    assert owner.id != other_user.id
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "SPACE_NOT_FOUND",
            "message": "产品空间不存在",
            "details": {},
        }
    }


def test_space_detail_rejects_invalid_uuid(
    client: TestClient, database_session: Session
):
    authenticate(client, database_session, "uuid@example.com")

    response = client.get("/api/v1/spaces/not-a-uuid")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
