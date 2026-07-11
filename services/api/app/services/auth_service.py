from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import hash_password
from app.models import User
from app.schemas.auth import RegisterRequest

EMAIL_UNIQUE_CONSTRAINT = "uq_users_email"


def email_already_registered() -> AppError:
    return AppError(
        status_code=409,
        code="EMAIL_ALREADY_REGISTERED",
        message="该邮箱已注册",
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
