from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models import User
from app.schemas.model_config import DeepSeekConfigResponse, DeepSeekConfigUpdateRequest
from app.services.model_config_service import get_deepseek_config, save_deepseek_config

router = APIRouter(prefix="/model-configs", tags=["model-configs"])


@router.get("/deepseek", response_model=DeepSeekConfigResponse)
def get_current_user_deepseek_config(
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> DeepSeekConfigResponse:
    return get_deepseek_config(database_session, current_user)


@router.put("/deepseek", response_model=DeepSeekConfigResponse)
def update_current_user_deepseek_config(
    payload: DeepSeekConfigUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> DeepSeekConfigResponse:
    return save_deepseek_config(database_session, current_user, payload.api_key)
