from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.errors import AppError, document_not_found, document_not_indexable
from app.models import Document, DocumentChunk, User
from app.services.document_parser import extract_text
from app.services.space_service import get_space
from app.services.text_chunker import chunk_text


class EmbeddingProvider(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


@dataclass(frozen=True)
class RetrievalResult:
    content: str
    filename: str
    chunk_index: int
    similarity: float


def get_owned_document(
    database_session: Session, user: User, document_id: UUID
) -> Document | None:
    return database_session.scalar(
        select(Document).where(Document.id == document_id, Document.user_id == user.id)
    )


def read_document_content(storage_root: Path, storage_path: str) -> bytes:
    root = storage_root.resolve()
    source = (root / storage_path).resolve()
    if not source.is_relative_to(root):
        raise FileNotFoundError(storage_path)
    return source.read_bytes()


def index_document(
    database_session: Session,
    user: User,
    document_id: UUID,
    storage_root: Path,
    embedding_provider: EmbeddingProvider,
) -> Document:
    document = get_owned_document(database_session, user, document_id)
    if document is None:
        raise document_not_found()
    if document.status not in {"uploaded", "failed"}:
        raise document_not_indexable()

    try:
        document.status = "processing"
        document.error_message = None
        content = read_document_content(storage_root, document.storage_path)
        chunks = chunk_text(extract_text(document.filename, content))
        vectors = embedding_provider.embed([chunk.content for chunk in chunks])
        if len(vectors) != len(chunks) or any(
            len(vector) != 1024 for vector in vectors
        ):
            raise ValueError("embedding vector count or dimensions are invalid")

        database_session.execute(
            delete(DocumentChunk).where(
                DocumentChunk.document_id == document.id,
                DocumentChunk.user_id == user.id,
                DocumentChunk.space_id == document.space_id,
            )
        )
        for chunk, vector in zip(chunks, vectors, strict=True):
            database_session.add(
                DocumentChunk(
                    user_id=user.id,
                    space_id=document.space_id,
                    knowledge_base_id=document.knowledge_base_id,
                    document_id=document.id,
                    chunk_index=chunk.index,
                    content=chunk.content,
                    embedding=vector,
                    metadata_={},
                )
            )
        document.status = "indexed"
        database_session.commit()
    except AppError as error:
        database_session.rollback()
        document.status = "failed"
        document.error_message = (
            "文档未提取到可索引的正文"
            if error.code == "DOCUMENT_CONTENT_NOT_EXTRACTABLE"
            else "文档索引失败，请检查文档内容或稍后重试"
        )
        database_session.commit()
    except Exception:
        database_session.rollback()
        document.status = "failed"
        document.error_message = "文档索引失败，请检查文档内容或稍后重试"
        database_session.commit()
    return document


def search_documents(
    database_session: Session,
    user: User,
    space_id: UUID,
    query: str,
    embedding_provider: EmbeddingProvider,
    *,
    top_k: int = 8,
) -> list[RetrievalResult]:
    get_space(database_session, user, space_id)
    vector = embedding_provider.embed([query])[0]
    if len(vector) != 1024:
        raise ValueError("embedding vector dimensions are invalid")

    distance = DocumentChunk.embedding.op("<=>")(vector)
    similarity = (1 - distance).label("similarity")
    statement = (
        select(
            DocumentChunk.content,
            Document.filename,
            DocumentChunk.chunk_index,
            similarity,
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .where(
            DocumentChunk.user_id == user.id,
            DocumentChunk.space_id == space_id,
            Document.user_id == user.id,
            Document.space_id == space_id,
            Document.status == "indexed",
        )
        .order_by(distance)
        .limit(top_k)
    )
    return [
        RetrievalResult(
            content=row.content,
            filename=row.filename,
            chunk_index=row.chunk_index,
            similarity=float(row.similarity),
        )
        for row in database_session.execute(statement).all()
    ]
