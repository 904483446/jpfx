from datetime import UTC, datetime
from uuid import uuid4

import pytest
from app.core.errors import AppError
from app.models import KnowledgeBase
from app.schemas.auth import RegisterRequest
from app.schemas.space import SpaceCreateRequest
from app.services.auth_service import register_user
from app.services.space_service import create_space, get_space, list_spaces
from sqlalchemy import select
from sqlalchemy.orm import Session


def create_user(database_session: Session, email: str):
    return register_user(
        database_session,
        RegisterRequest(
            email=email,
            password="valid-password",
            display_name="空间测试用户",
        ),
    )


def test_create_space_creates_default_knowledge_base(database_session: Session):
    user = create_user(database_session, "space-owner@example.com")

    space = create_space(
        database_session,
        user,
        SpaceCreateRequest(name="企业知识库 Copilot"),
    )

    knowledge_base = database_session.scalar(
        select(KnowledgeBase).where(KnowledgeBase.space_id == space.id)
    )
    assert space.user_id == user.id
    assert knowledge_base is not None
    assert (knowledge_base.user_id, knowledge_base.name) == (user.id, "默认知识库")


def test_list_spaces_only_returns_current_user_spaces(database_session: Session):
    user_a = create_user(database_session, "space-a@example.com")
    user_b = create_user(database_session, "space-b@example.com")
    create_space(database_session, user_a, SpaceCreateRequest(name="A 空间"))
    create_space(database_session, user_b, SpaceCreateRequest(name="B 空间"))

    assert [space.name for space in list_spaces(database_session, user_a)] == ["A 空间"]


@pytest.mark.parametrize("space_id", [uuid4()])
def test_get_space_hides_missing_and_other_user_spaces(
    database_session: Session,
    space_id,
):
    user_a = create_user(database_session, "detail-a@example.com")
    user_b = create_user(database_session, "detail-b@example.com")
    other_space = create_space(
        database_session, user_b, SpaceCreateRequest(name="B 空间")
    )

    for requested_space_id in (space_id, other_space.id):
        with pytest.raises(AppError) as captured:
            get_space(database_session, user_a, requested_space_id)
        assert (captured.value.status_code, captured.value.code) == (
            404,
            "SPACE_NOT_FOUND",
        )


def test_get_space_hides_soft_deleted_space(database_session: Session):
    user = create_user(database_session, "deleted-space@example.com")
    space = create_space(database_session, user, SpaceCreateRequest(name="已删除空间"))
    space.deleted_at = datetime.now(UTC)
    database_session.commit()

    with pytest.raises(AppError, match="产品空间不存在"):
        get_space(database_session, user, space.id)
