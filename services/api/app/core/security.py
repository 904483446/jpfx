from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.core.config import Settings
from app.core.config import settings as app_settings

password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, encoded_password: str) -> bool:
    return password_hash.verify(plain_password, encoded_password)


def create_access_token(
    user_id: UUID,
    *,
    settings: Settings = app_settings,
    now: datetime | None = None,
) -> str:
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET 未配置")
    if len(settings.jwt_secret.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET 至少需要 32 字节")
    issued_at = now or datetime.now(UTC)
    expires_at = issued_at + timedelta(days=settings.access_token_expire_days)
    return jwt.encode(
        {"sub": str(user_id), "iat": issued_at, "exp": expires_at},
        settings.jwt_secret,
        algorithm="HS256",
    )
