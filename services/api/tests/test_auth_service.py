import importlib
from unittest.mock import create_autospec

import pytest
from app.core.errors import AppError
from app.core.security import verify_password
from app.schemas.auth import RegisterRequest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


class FakeDiagnostic:
    def __init__(self, constraint_name: str) -> None:
        self.constraint_name = constraint_name


class FakeDatabaseError(Exception):
    def __init__(self, constraint_name: str) -> None:
        self.diag = FakeDiagnostic(constraint_name)


def integrity_error(constraint_name: str) -> IntegrityError:
    return IntegrityError(
        "INSERT INTO users",
        {},
        FakeDatabaseError(constraint_name),
    )


def registration_payload() -> RegisterRequest:
    return RegisterRequest(
        email="race@example.com",
        password="valid-password",
        display_name="竞争测试用户",
    )


def test_register_user_persists_normalized_user(database_session: Session):
    register_user = importlib.import_module("app.services.auth_service").register_user

    user = register_user(
        database_session,
        RegisterRequest(
            email="User@Example.com",
            password="valid-password",
            display_name="示例用户",
        ),
    )

    assert user.email == "user@example.com"
    assert user.password_hash != "valid-password"
    assert verify_password("valid-password", user.password_hash)


def test_register_user_rejects_existing_email(database_session: Session):
    register_user = importlib.import_module("app.services.auth_service").register_user
    payload = RegisterRequest(
        email="duplicate@example.com",
        password="valid-password",
        display_name="用户一",
    )
    register_user(database_session, payload)

    with pytest.raises(AppError) as captured:
        register_user(
            database_session,
            payload.model_copy(update={"display_name": "用户二"}),
        )

    assert captured.value.status_code == 409
    assert captured.value.code == "EMAIL_ALREADY_REGISTERED"


def test_register_user_converts_email_unique_race_to_app_error():
    register_user = importlib.import_module("app.services.auth_service").register_user
    session = create_autospec(Session, instance=True)
    session.scalar.return_value = None
    session.commit.side_effect = integrity_error("uq_users_email")

    with pytest.raises(AppError) as captured:
        register_user(session, registration_payload())

    assert captured.value.status_code == 409
    assert captured.value.code == "EMAIL_ALREADY_REGISTERED"
    session.rollback.assert_called_once_with()


def test_register_user_reraises_unrelated_integrity_error():
    register_user = importlib.import_module("app.services.auth_service").register_user
    session = create_autospec(Session, instance=True)
    session.scalar.return_value = None
    unexpected = integrity_error("other_constraint")
    session.commit.side_effect = unexpected

    with pytest.raises(IntegrityError) as captured:
        register_user(session, registration_payload())

    assert captured.value is unexpected
    session.rollback.assert_called_once_with()
