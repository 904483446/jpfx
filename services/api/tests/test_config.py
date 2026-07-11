from app.core.config import Settings


def test_auth_settings_have_safe_development_defaults():
    settings = Settings(
        _env_file=None,
        jwt_secret="test-secret",
    )

    assert settings.jwt_secret == "test-secret"
    assert settings.access_token_expire_days == 7
    assert settings.auth_cookie_name == "access_token"
    assert settings.auth_cookie_secure is False
