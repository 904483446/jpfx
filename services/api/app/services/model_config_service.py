from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import ModelConfig, User
from app.schemas.model_config import DeepSeekConfigResponse
from app.services.key_cipher import KeyCipher

DEEPSEEK_PROVIDER = "deepseek"
DEEPSEEK_DEFAULT_MODEL = "deepseek-chat"


def get_deepseek_config(
    database_session: Session,
    user: User,
) -> DeepSeekConfigResponse:
    model_config = database_session.scalar(
        select(ModelConfig).where(
            ModelConfig.user_id == user.id,
            ModelConfig.provider == DEEPSEEK_PROVIDER,
        )
    )
    return DeepSeekConfigResponse(
        is_configured=model_config is not None,
        api_key_hint=model_config.api_key_hint if model_config else None,
        default_model=DEEPSEEK_DEFAULT_MODEL,
    )


def save_deepseek_config(
    database_session: Session,
    user: User,
    api_key: str,
) -> DeepSeekConfigResponse:
    encrypted_api_key = KeyCipher.from_settings().encrypt(api_key)
    api_key_hint = _api_key_hint(api_key)
    statement = insert(ModelConfig).values(
        user_id=user.id,
        provider=DEEPSEEK_PROVIDER,
        encrypted_api_key=encrypted_api_key,
        api_key_hint=api_key_hint,
    )
    statement = statement.on_conflict_do_update(
        constraint="uq_model_configs_user_id_provider",
        set_={
            "encrypted_api_key": statement.excluded.encrypted_api_key,
            "api_key_hint": statement.excluded.api_key_hint,
            "updated_at": func.clock_timestamp(),
        },
    )
    try:
        database_session.execute(statement)
        database_session.commit()
    except Exception:
        database_session.rollback()
        raise
    return DeepSeekConfigResponse(
        is_configured=True,
        api_key_hint=api_key_hint,
        default_model=DEEPSEEK_DEFAULT_MODEL,
    )


def _api_key_hint(api_key: str) -> str:
    if len(api_key) <= 7:
        return "********"
    return f"{api_key[:3]}********{api_key[-4:]}"
