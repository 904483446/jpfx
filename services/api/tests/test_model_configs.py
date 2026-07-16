from collections.abc import Generator

import pytest
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import app
from app.models import ModelConfig, User
from app.schemas.auth import RegisterRequest
from app.services.auth_service import register_user
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

TEST_SECRET = "test-secret-with-at-least-32-bytes"
ENCRYPTION_SECRET = "test-encryption-secret-with-enough-entropy"


@pytest.fixture
def client(
    database_session: Session, monkeypatch: pytest.MonkeyPatch
) -> Generator[TestClient, None, None]:
    def override_database_session() -> Generator[Session, None, None]:
        yield database_session

    monkeypatch.setattr(settings, "jwt_secret", TEST_SECRET)
    monkeypatch.setattr(settings, "api_key_encryption_secret", ENCRYPTION_SECRET)
    app.dependency_overrides[get_db_session] = override_database_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def authenticate(client: TestClient, database_session: Session, email: str) -> User:
    user = register_user(
        database_session,
        RegisterRequest(
            email=email,
            password="valid-password",
            display_name="模型配置用户",
        ),
    )
    client.cookies.set(settings.auth_cookie_name, create_access_token(user.id))
    return user


def test_model_config_endpoints_require_authentication(client: TestClient):
    assert client.get("/api/v1/model-configs/deepseek").status_code == 401
    assert (
        client.put(
            "/api/v1/model-configs/deepseek",
            json={"api_key": "sk-secret-value"},
        ).status_code
        == 401
    )


def test_deepseek_config_put_allows_cors_preflight(client: TestClient):
    response = client.options(
        "/api/v1/model-configs/deepseek",
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "PUT",
        },
    )

    assert response.status_code == 200
    assert "PUT" in response.headers["access-control-allow-methods"]


def test_get_unconfigured_deepseek_returns_safe_default(
    client: TestClient, database_session: Session
):
    authenticate(client, database_session, "unconfigured@example.com")

    response = client.get("/api/v1/model-configs/deepseek")

    assert response.status_code == 200
    assert response.json() == {
        "is_configured": False,
        "api_key_hint": None,
        "default_model": "deepseek-chat",
    }


def test_put_deepseek_config_returns_mask_only_and_encrypts_at_rest(
    client: TestClient, database_session: Session
):
    user = authenticate(client, database_session, "configured@example.com")

    response = client.put(
        "/api/v1/model-configs/deepseek",
        json={"api_key": "sk-secret-value"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "is_configured": True,
        "api_key_hint": "sk-********alue",
        "default_model": "deepseek-chat",
    }
    assert "sk-secret-value" not in response.text
    stored_config = database_session.scalar(
        select(ModelConfig).where(
            ModelConfig.user_id == user.id,
            ModelConfig.provider == "deepseek",
        )
    )
    assert stored_config is not None
    assert stored_config.encrypted_api_key != "sk-secret-value"
    assert stored_config.api_key_hint == "sk-********alue"


def test_put_deepseek_config_upserts_current_users_config(
    client: TestClient, database_session: Session
):
    user = authenticate(client, database_session, "upsert@example.com")
    client.put(
        "/api/v1/model-configs/deepseek",
        json={"api_key": "sk-first-secret"},
    )
    first_config = database_session.scalar(
        select(ModelConfig).where(
            ModelConfig.user_id == user.id,
            ModelConfig.provider == "deepseek",
        )
    )
    assert first_config is not None
    first_updated_at = first_config.updated_at

    response = client.put(
        "/api/v1/model-configs/deepseek",
        json={"api_key": "sk-second-secret"},
    )

    database_session.expire_all()
    stored_configs = list(
        database_session.scalars(
            select(ModelConfig).where(
                ModelConfig.user_id == user.id,
                ModelConfig.provider == "deepseek",
            )
        )
    )
    assert response.status_code == 200
    assert len(stored_configs) == 1
    assert stored_configs[0].api_key_hint == "sk-********cret"
    assert stored_configs[0].updated_at > first_updated_at


def test_short_api_key_hint_does_not_expose_the_full_key(
    client: TestClient, database_session: Session
):
    authenticate(client, database_session, "short-key@example.com")

    response = client.put(
        "/api/v1/model-configs/deepseek",
        json={"api_key": "abc"},
    )

    assert response.status_code == 200
    assert "abc" not in response.text
    assert response.json()["api_key_hint"] == "********"


def test_users_cannot_read_each_others_model_config(
    client: TestClient, database_session: Session
):
    owner = authenticate(client, database_session, "owner@example.com")
    client.put(
        "/api/v1/model-configs/deepseek",
        json={"api_key": "sk-owner-secret"},
    )
    other_user = register_user(
        database_session,
        RegisterRequest(
            email="other@example.com",
            password="valid-password",
            display_name="其他用户",
        ),
    )
    client.cookies.set(settings.auth_cookie_name, create_access_token(other_user.id))

    response = client.get("/api/v1/model-configs/deepseek")

    assert owner.id != other_user.id
    assert response.status_code == 200
    assert response.json()["is_configured"] is False
    assert response.json()["api_key_hint"] is None


def test_missing_encryption_secret_returns_chinese_uniform_error(
    client: TestClient, database_session: Session, monkeypatch: pytest.MonkeyPatch
):
    authenticate(client, database_session, "missing-secret@example.com")
    monkeypatch.setattr(settings, "api_key_encryption_secret", None)

    response = client.put(
        "/api/v1/model-configs/deepseek",
        json={"api_key": "sk-secret-value"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "MODEL_CONFIG_ENCRYPTION_NOT_CONFIGURED",
            "message": "模型配置密钥加密未配置",
            "details": {},
        }
    }
