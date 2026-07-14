import pytest
from app import main as main_module
from app.core.config import Settings
from fastapi.testclient import TestClient

ALLOWED_ORIGIN = "http://127.0.0.1:3000"


def test_preflight_allows_configured_local_credentialed_frontend():
    response = TestClient(main_module.create_app()).options(
        "/api/v1/auth/login",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "POST" in response.headers["access-control-allow-methods"]
    assert "content-type" in response.headers["access-control-allow-headers"].lower()


def test_preflight_does_not_allow_unconfigured_origin():
    response = TestClient(main_module.create_app()).options(
        "/api/v1/auth/login",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert "access-control-allow-origin" not in response.headers


@pytest.mark.parametrize("origins", ["*", " , "])
def test_cors_settings_reject_unsafe_or_empty_origins(origins: str):
    with pytest.raises(ValueError):
        Settings(_env_file=None, cors_allowed_origins=origins)


@pytest.mark.parametrize(
    "origin",
    ["http://127.0.0.1:3000", "http://localhost:3000"],
)
def test_preflight_allows_each_origin_from_comma_separated_settings(
    monkeypatch: pytest.MonkeyPatch,
    origin: str,
):
    monkeypatch.setattr(
        main_module,
        "settings",
        Settings(
            _env_file=None,
            cors_allowed_origins=" http://127.0.0.1:3000, , http://localhost:3000 ",
        ),
    )

    response = TestClient(main_module.create_app()).options(
        "/api/v1/auth/login",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert response.headers["access-control-allow-origin"] == origin


def test_preflight_does_not_allow_unknown_origin_from_comma_separated_settings(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        main_module,
        "settings",
        Settings(
            _env_file=None,
            cors_allowed_origins="http://127.0.0.1:3000, http://localhost:3000",
        ),
    )

    response = TestClient(main_module.create_app()).options(
        "/api/v1/auth/login",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert "access-control-allow-origin" not in response.headers
