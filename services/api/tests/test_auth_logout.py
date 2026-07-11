import pytest
from app.core.config import settings
from app.main import app
from fastapi.testclient import TestClient


@pytest.mark.parametrize("has_cookie", [False, True])
def test_logout_is_idempotent_and_clears_cookie(has_cookie: bool):
    client = TestClient(app)
    if has_cookie:
        client.cookies.set(settings.auth_cookie_name, "opaque-test-token")

    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 204
    assert response.content == b""
    set_cookie = response.headers["set-cookie"]
    assert f"{settings.auth_cookie_name}=" in set_cookie
    assert "Max-Age=0" in set_cookie
    assert "Path=/" in set_cookie
