from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.auth import RegisterRequest, UserResponse
from app.services.auth_service import register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    database_session: Annotated[Session, Depends(get_db_session)],
) -> UserResponse:
    user = register_user(database_session, payload)
    return UserResponse.model_validate(user)
