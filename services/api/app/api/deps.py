from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Cookie, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import unauthorized
from app.core.security import get_jwt_secret
from app.db.session import get_db_session
from app.models import User


def get_current_user(
    database_session: Annotated[Session, Depends(get_db_session)],
    access_token: Annotated[
        str | None,
        Cookie(alias=settings.auth_cookie_name),
    ] = None,
) -> User:
    if access_token is None:
        raise unauthorized()

    try:
        payload = jwt.decode(
            access_token,
            get_jwt_secret(),
            algorithms=["HS256"],
        )
        user_id = UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise unauthorized() from None

    user = database_session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise unauthorized()
    return user
