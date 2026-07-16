from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import document_not_found
from app.models import Document, KnowledgeBase, User
from app.services.document_storage import LocalDocumentStorage
from app.services.space_service import get_space


def create_document(
    database_session: Session,
    user: User,
    space_id: UUID,
    filename: str,
    content: bytes,
    storage: LocalDocumentStorage,
) -> Document:
    space = get_space(database_session, user, space_id)
    knowledge_base = database_session.scalar(
        select(KnowledgeBase).where(
            KnowledgeBase.space_id == space.id,
            KnowledgeBase.user_id == user.id,
        )
    )
    if knowledge_base is None:
        raise document_not_found()

    stored = storage.save(user.id, space.id, filename, content)
    document = Document(
        user_id=user.id,
        space_id=space.id,
        knowledge_base_id=knowledge_base.id,
        filename=filename,
        file_type=stored.file_type,
        file_size=stored.size,
        storage_path=stored.relative_path,
    )
    database_session.add(document)
    try:
        database_session.commit()
    except Exception:
        database_session.rollback()
        storage.delete(stored.relative_path)
        raise
    database_session.refresh(document)
    return document


async def create_uploaded_document(
    database_session: Session,
    user: User,
    space_id: UUID,
    filename: str,
    upload,
    storage: LocalDocumentStorage,
) -> Document:
    space = get_space(database_session, user, space_id)
    knowledge_base = database_session.scalar(
        select(KnowledgeBase).where(
            KnowledgeBase.space_id == space.id, KnowledgeBase.user_id == user.id
        )
    )
    if knowledge_base is None:
        raise document_not_found()
    stored = await storage.save_upload(user.id, space.id, filename, upload)
    document = Document(
        user_id=user.id,
        space_id=space.id,
        knowledge_base_id=knowledge_base.id,
        filename=filename,
        file_type=stored.file_type,
        file_size=stored.size,
        storage_path=stored.relative_path,
    )
    database_session.add(document)
    try:
        database_session.commit()
    except Exception:
        database_session.rollback()
        storage.delete(stored.relative_path)
        raise
    database_session.refresh(document)
    return document


def list_documents(
    database_session: Session, user: User, space_id: UUID
) -> list[Document]:
    get_space(database_session, user, space_id)
    statement = (
        select(Document)
        .where(Document.user_id == user.id, Document.space_id == space_id)
        .order_by(Document.created_at.desc())
    )
    return list(database_session.scalars(statement))


def delete_document(
    database_session: Session,
    user: User,
    document_id: UUID,
    storage: LocalDocumentStorage,
) -> None:
    document = database_session.scalar(
        select(Document).where(Document.id == document_id, Document.user_id == user.id)
    )
    if document is None:
        raise document_not_found()
    storage.delete(document.storage_path)
    database_session.delete(document)
    database_session.commit()
