from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
import pytest
from app.core.config import Settings
from app.core.security import create_access_token, get_jwt_secret

USER_ID = UUID("11111111-1111-1111-1111-111111111111")
NOW = datetime(2026, 7, 11, tzinfo=UTC)
TEST_SECRET = "test-secret-with-at-least-32-bytes"


def test_get_jwt_secret_returns_configured_secret():
    assert get_jwt_secret(Settings(_env_file=None, jwt_secret=TEST_SECRET)) == TEST_SECRET


@pytest.mark.parametrize(
    ("secret", "message"),
    [
        (None, "JWT_SECRET 未配置"),
        ("x" * 31, "JWT_SECRET 至少需要 32 字节"),
    ],
)
def test_get_jwt_secret_rejects_missing_or_weak_secret(
    secret: str | None,
    message: str,
):
    with pytest.raises(RuntimeError, match=message):
        get_jwt_secret(Settings(_env_file=None, jwt_secret=secret))


def test_create_access_token_has_expected_claims():
    token = create_access_token(
        USER_ID,
        settings=Settings(
            _env_file=None,
            jwt_secret=TEST_SECRET,
            access_token_expire_days=7,
        ),
        now=NOW,
    )

    claims = jwt.decode(token, TEST_SECRET, algorithms=["HS256"])
    assert claims["sub"] == str(USER_ID)
    assert datetime.fromtimestamp(claims["iat"], UTC) == NOW
    assert datetime.fromtimestamp(claims["exp"], UTC) == NOW + timedelta(days=7)


def test_create_access_token_requires_secret():
    with pytest.raises(RuntimeError, match="JWT_SECRET 未配置"):
        create_access_token(
            USER_ID,
            settings=Settings(_env_file=None, jwt_secret=None),
            now=NOW,
        )


@pytest.mark.parametrize("weak_secret", ["change-me", "x" * 31])
def test_create_access_token_rejects_weak_secret(weak_secret: str):
    with pytest.raises(RuntimeError, match="JWT_SECRET 至少需要 32 字节"):
        create_access_token(
            USER_ID,
            settings=Settings(_env_file=None, jwt_secret=weak_secret),
            now=NOW,
        )
