from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models import User
from app.schemas.space import SpaceCreateRequest, SpaceResponse
from app.services.space_service import create_space, get_space, list_spaces

router = APIRouter(prefix="/spaces", tags=["spaces"])


@router.get("", response_model=list[SpaceResponse])
def list_current_user_spaces(
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> list[SpaceResponse]:
    return [
        SpaceResponse.model_validate(space)
        for space in list_spaces(database_session, current_user)
    ]


@router.post("", response_model=SpaceResponse, status_code=status.HTTP_201_CREATED)
def create_current_user_space(
    payload: SpaceCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> SpaceResponse:
    return SpaceResponse.model_validate(
        create_space(database_session, current_user, payload)
    )


@router.get("/{space_id}", response_model=SpaceResponse)
def get_current_user_space(
    space_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> SpaceResponse:
    return SpaceResponse.model_validate(
        get_space(database_session, current_user, space_id)
    )
