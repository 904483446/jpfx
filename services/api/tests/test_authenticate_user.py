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
