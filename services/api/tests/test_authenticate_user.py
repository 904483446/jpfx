from unittest.mock import Mock

import app.services.auth_service as auth_service
import pytest
from app.core.errors import AppError
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import authenticate_user, register_user


def create_user(database_session):
    return register_user(
        database_session,
        RegisterRequest(
            email="login@example.com",
            password="correct-password",
            display_name="登录用户",
        ),
    )


def test_authenticate_user_accepts_correct_credentials(database_session):
    user = create_user(database_session)

    authenticated = authenticate_user(
        database_session,
        LoginRequest(
            email="  LOGIN@EXAMPLE.COM  ",
            password="correct-password",
        ),
    )

    assert authenticated.id == user.id


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("missing@example.com", "correct-password"),
        ("login@example.com", "wrong-password"),
    ],
)
def test_authenticate_user_hides_failure_reason(
    database_session,
    email: str,
    password: str,
):
    create_user(database_session)

    with pytest.raises(AppError) as captured:
        authenticate_user(
            database_session,
            LoginRequest(email=email, password=password),
        )

    assert captured.value.status_code == 401
    assert captured.value.code == "INVALID_CREDENTIALS"
    assert captured.value.message == "邮箱或密码错误"


def test_missing_user_still_verifies_a_password_hash(
    database_session,
    monkeypatch: pytest.MonkeyPatch,
):
    verifier = Mock(return_value=False)
    monkeypatch.setattr(auth_service, "verify_password", verifier)

    with pytest.raises(AppError):
        authenticate_user(
            database_session,
            LoginRequest(
                email="missing@example.com",
                password="correct-password",
            ),
        )

    verifier.assert_called_once()
