from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from app.core.config import Settings
from app.models import KnowledgeBase, Space, User
from sqlalchemy import create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

API_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def migrated_database_url() -> Generator[str, None, None]:
    database_url = Settings().test_database_url
    assert database_url is not None
    configuration = Config(str(API_ROOT / "alembic.ini"))
    configuration.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(configuration, "head")
    yield database_url


@pytest.fixture
def database_session(
    migrated_database_url: str,
) -> Generator[Session, None, None]:
    engine = create_engine(migrated_database_url)
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False)
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()
        engine.dispose()


def create_user(database_session: Session, email: str) -> User:
    user = User(
        email=email,
        password_hash="hashed-password",
        display_name=email.split("@", maxsplit=1)[0],
    )
    database_session.add(user)
    database_session.flush()
    return user


def create_space(database_session: Session, user: User, name: str) -> Space:
    space = Space(user_id=user.id, name=name)
    database_session.add(space)
    database_session.flush()
    return space


def test_email_must_be_unique(database_session: Session):
    create_user(database_session, "duplicate@example.com")
    database_session.add(
        User(
            email="duplicate@example.com",
            password_hash="another-hash",
            display_name="duplicate",
        )
    )

    with pytest.raises(IntegrityError):
        database_session.flush()


def test_space_can_have_only_one_knowledge_base(database_session: Session):
    user = create_user(database_session, "one-kb@example.com")
    space = create_space(database_session, user, "单知识库空间")
    database_session.add(
        KnowledgeBase(user_id=user.id, space_id=space.id, name="默认知识库")
    )
    database_session.flush()
    database_session.add(
        KnowledgeBase(user_id=user.id, space_id=space.id, name="重复知识库")
    )

    with pytest.raises(IntegrityError):
        database_session.flush()


def test_knowledge_base_owner_must_match_space_owner(database_session: Session):
    space_owner = create_user(database_session, "space-owner@example.com")
    other_user = create_user(database_session, "other-user@example.com")
    space = create_space(database_session, space_owner, "隔离测试空间")
    database_session.add(
        KnowledgeBase(
            user_id=other_user.id,
            space_id=space.id,
            name="非法跨用户知识库",
        )
    )

    with pytest.raises(IntegrityError):
        database_session.flush()


def test_deleting_user_cascades_to_spaces_and_knowledge_bases(
    database_session: Session,
):
    user = create_user(database_session, "cascade@example.com")
    space = create_space(database_session, user, "级联测试空间")
    knowledge_base = KnowledgeBase(
        user_id=user.id,
        space_id=space.id,
        name="级联测试知识库",
    )
    database_session.add(knowledge_base)
    database_session.flush()

    database_session.delete(user)
    database_session.flush()

    assert database_session.scalar(select(func.count()).select_from(User)) == 0
    assert database_session.scalar(select(func.count()).select_from(Space)) == 0
    assert database_session.scalar(select(func.count()).select_from(KnowledgeBase)) == 0


def test_physically_deleting_space_cascades_to_knowledge_base(
    database_session: Session,
):
    user = create_user(database_session, "space-cascade@example.com")
    space = create_space(database_session, user, "空间级联测试")
    database_session.add(
        KnowledgeBase(
            user_id=user.id,
            space_id=space.id,
            name="随空间删除的知识库",
        )
    )
    database_session.flush()

    database_session.delete(space)
    database_session.flush()

    assert database_session.scalar(select(func.count()).select_from(User)) == 1
    assert database_session.scalar(select(func.count()).select_from(Space)) == 0
    assert database_session.scalar(select(func.count()).select_from(KnowledgeBase)) == 0
