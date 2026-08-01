import pytest
from app.core.config import Settings
from pydantic import ValidationError


def test_auth_settings_have_safe_development_defaults():
    settings = Settings(
        _env_file=None,
        jwt_secret="test-secret",
    )

    assert settings.jwt_secret == "test-secret"
    assert settings.access_token_expire_days == 7
    assert settings.auth_cookie_name == "access_token"
    assert settings.auth_cookie_secure is False
    assert settings.supabase_storage_bucket == "jpfx-documents"


@pytest.mark.parametrize(
    ("supabase_url", "supabase_secret_key"),
    [
        ("https://project.supabase.co", None),
        (None, "test-service-role-key"),
    ],
)
def test_storage_settings_require_supabase_url_and_secret_key_together(
    supabase_url, supabase_secret_key
):
    with pytest.raises(ValidationError) as captured:
        Settings(
            _env_file=None,
            supabase_url=supabase_url,
            supabase_secret_key=supabase_secret_key,
        )

    error = str(captured.value)
    assert "Supabase URL 与 Secret Key 必须同时配置或同时缺失" in error
    assert "project.supabase.co" not in error
    assert "test-service-role-key" not in error
