from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import hash_password, verify_password
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest

EMAIL_UNIQUE_CONSTRAINT = "uq_users_email"
DUMMY_PASSWORD_HASH = hash_password("dummy-password-for-login-timing")


def email_already_registered() -> AppError:
    return AppError(
        status_code=409,
        code="EMAIL_ALREADY_REGISTERED",
        message="该邮箱已注册",
    )


def invalid_credentials() -> AppError:
    return AppError(
        status_code=401,
        code="INVALID_CREDENTIALS",
        message="邮箱或密码错误",
    )


def integrity_constraint_name(exc: IntegrityError) -> str | None:
    diagnostic = getattr(exc.orig, "diag", None)
    return getattr(diagnostic, "constraint_name", None)


def register_user(database_session: Session, payload: RegisterRequest) -> User:
    email = str(payload.email)
    existing_user = database_session.scalar(select(User).where(User.email == email))
    if existing_user is not None:
        raise email_already_registered()

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
    )
    database_session.add(user)
    try:
        database_session.commit()
    except IntegrityError as exc:
        database_session.rollback()
        if integrity_constraint_name(exc) == EMAIL_UNIQUE_CONSTRAINT:
            raise email_already_registered() from exc
        raise

    database_session.refresh(user)
    return user


def authenticate_user(database_session: Session, payload: LoginRequest) -> User:
    user = database_session.scalar(select(User).where(User.email == str(payload.email)))
    encoded_password = user.password_hash if user is not None else DUMMY_PASSWORD_HASH
    password_matches = verify_password(payload.password, encoded_password)
    if user is None or not password_matches:
        raise invalid_credentials()
    return user
