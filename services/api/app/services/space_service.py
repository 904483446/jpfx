from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import space_not_found
from app.models import KnowledgeBase, Space, User
from app.schemas.space import SpaceCreateRequest

DEFAULT_KNOWLEDGE_BASE_NAME = "默认知识库"


def list_spaces(database_session: Session, user: User) -> list[Space]:
    statement = (
        select(Space)
        .where(Space.user_id == user.id, Space.deleted_at.is_(None))
        .order_by(Space.created_at.desc())
    )
    return list(database_session.scalars(statement))


def get_space(database_session: Session, user: User, space_id: UUID) -> Space:
    statement = select(Space).where(
        Space.id == space_id,
        Space.user_id == user.id,
        Space.deleted_at.is_(None),
    )
    space = database_session.scalar(statement)
    if space is None:
        raise space_not_found()
    return space


def create_space(
    database_session: Session,
    user: User,
    payload: SpaceCreateRequest,
) -> Space:
    space = Space(user_id=user.id, **payload.model_dump())
    database_session.add(space)
    try:
        database_session.flush()
        database_session.add(
            KnowledgeBase(
                user_id=user.id,
                space_id=space.id,
                name=DEFAULT_KNOWLEDGE_BASE_NAME,
            )
        )
        database_session.commit()
    except Exception:
        database_session.rollback()
        raise
    database_session.refresh(space)
    return space
