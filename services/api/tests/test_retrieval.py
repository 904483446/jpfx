from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.core.errors import (
    AppError,
    document_content_not_extractable,
    embedding_not_configured,
)


class FakeSession:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.executed: list[object] = []
        self.commits = 0
        self.rollbacks = 0

    def add(self, value: object) -> None:
        self.added.append(value)

    def execute(self, statement: object):
        self.executed.append(statement)
        return SimpleNamespace(all=lambda: [])

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


class FakeEmbeddingProvider:
    def __init__(self, vectors: list[list[float]]) -> None:
        self.vectors = vectors
        self.texts: list[list[str]] = []

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.texts.append(texts)
        return self.vectors


def test_index_document_marks_uploaded_document_indexed_and_replaces_chunks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    from app.services import retrieval_service

    user = SimpleNamespace(id=uuid4())
    document = SimpleNamespace(
        id=uuid4(),
        user_id=user.id,
        space_id=uuid4(),
        knowledge_base_id=uuid4(),
        filename="brief.txt",
        storage_path="source.txt",
        status="uploaded",
        error_message=None,
    )
    (tmp_path / document.storage_path).write_text("可检索正文", encoding="utf-8")
    session = FakeSession()
    provider = FakeEmbeddingProvider([[0.1] * 1024])
    monkeypatch.setattr(retrieval_service, "get_owned_document", lambda *_: document)
    monkeypatch.setattr(
        retrieval_service,
        "chunk_text",
        lambda text: [SimpleNamespace(index=0, content=text)],
    )

    result = retrieval_service.index_document(
        session, user, document.id, tmp_path, provider
    )

    assert result.status == "indexed"
    assert result.error_message is None
    assert provider.texts == [["可检索正文"]]
    assert len(session.added) == 1
    chunk = session.added[0]
    assert chunk.document_id == document.id
    assert chunk.user_id == user.id
    assert chunk.chunk_index == 0
    assert chunk.content == "可检索正文"
    assert session.commits == 1


def test_index_document_marks_failed_and_rolls_back_new_chunks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    from app.services import retrieval_service

    user = SimpleNamespace(id=uuid4())
    document = SimpleNamespace(
        id=uuid4(),
        user_id=user.id,
        space_id=uuid4(),
        knowledge_base_id=uuid4(),
        filename="empty.pdf",
        storage_path="empty.pdf",
        status="uploaded",
        error_message=None,
    )
    session = FakeSession()
    monkeypatch.setattr(retrieval_service, "get_owned_document", lambda *_: document)
    monkeypatch.setattr(
        retrieval_service,
        "read_document_content",
        lambda *_: (_ for _ in ()).throw(document_content_not_extractable()),
    )

    result = retrieval_service.index_document(
        session, user, document.id, tmp_path, FakeEmbeddingProvider([])
    )

    assert result.status == "failed"
    assert result.error_message == "文档未提取到可索引的正文"
    assert session.rollbacks == 1
    assert session.added == []
    assert session.commits == 1


def test_index_document_persists_failed_status_then_reraises_embedding_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    from app.services import retrieval_service

    user = SimpleNamespace(id=uuid4())
    document = SimpleNamespace(
        id=uuid4(),
        user_id=user.id,
        space_id=uuid4(),
        knowledge_base_id=uuid4(),
        filename="brief.txt",
        storage_path="source.txt",
        status="uploaded",
        error_message=None,
    )
    (tmp_path / document.storage_path).write_text("可检索正文", encoding="utf-8")
    session = FakeSession()
    monkeypatch.setattr(retrieval_service, "get_owned_document", lambda *_: document)
    monkeypatch.setattr(
        retrieval_service,
        "chunk_text",
        lambda text: [SimpleNamespace(index=0, content=text)],
    )

    class MissingKeyProvider:
        def embed(self, _texts: list[str]) -> list[list[float]]:
            raise embedding_not_configured()

    with pytest.raises(AppError) as captured:
        retrieval_service.index_document(
            session, user, document.id, tmp_path, MissingKeyProvider()
        )

    assert captured.value.code == "EMBEDDING_NOT_CONFIGURED"
    assert document.status == "failed"
    assert document.error_message == "文档索引失败，请检查文档内容或稍后重试"
    assert session.rollbacks == 1
    assert session.commits == 1


def test_index_document_hides_other_users_document(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    from app.services import retrieval_service

    monkeypatch.setattr(retrieval_service, "get_owned_document", lambda *_: None)

    with pytest.raises(AppError) as captured:
        retrieval_service.index_document(
            FakeSession(),
            SimpleNamespace(id=uuid4()),
            uuid4(),
            tmp_path,
            FakeEmbeddingProvider([]),
        )

    assert captured.value.code == "DOCUMENT_NOT_FOUND"


def test_index_document_rejects_document_already_being_processed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    from app.services import retrieval_service

    user = SimpleNamespace(id=uuid4())
    document = SimpleNamespace(id=uuid4(), status="processing")
    monkeypatch.setattr(retrieval_service, "get_owned_document", lambda *_: document)

    with pytest.raises(AppError) as captured:
        retrieval_service.index_document(
            FakeSession(), user, document.id, tmp_path, FakeEmbeddingProvider([])
        )

    assert captured.value.code == "DOCUMENT_NOT_INDEXABLE"


def test_search_documents_filters_by_current_user_and_space(
    monkeypatch: pytest.MonkeyPatch,
):
    from app.services import retrieval_service

    user = SimpleNamespace(id=uuid4())
    space_id = uuid4()
    session = FakeSession()
    provider = FakeEmbeddingProvider([[0.2] * 1024])
    monkeypatch.setattr(retrieval_service, "get_space", lambda *_: object())
    row = SimpleNamespace(
        content="命中的片段",
        filename="brief.txt",
        chunk_index=3,
        similarity=0.91,
    )
    session.execute = lambda statement: SimpleNamespace(all=lambda: [row])

    results = retrieval_service.search_documents(
        session, user, space_id, "检索问题", provider, top_k=8
    )

    assert provider.texts == [["检索问题"]]
    assert results == [
        retrieval_service.RetrievalResult(
            content="命中的片段",
            filename="brief.txt",
            chunk_index=3,
            similarity=0.91,
        )
    ]


def test_search_documents_persists_vectors_and_orders_by_cosine_similarity(
    database_session,
):
    from app.models import Document, DocumentChunk, KnowledgeBase, Space, User
    from app.services import retrieval_service

    user = User(
        email="vector-search@example.com",
        password_hash="hashed-password",
        display_name="vector-search",
    )
    database_session.add(user)
    database_session.flush()
    space = Space(user_id=user.id, name="向量检索空间")
    database_session.add(space)
    database_session.flush()
    knowledge_base = KnowledgeBase(
        user_id=user.id, space_id=space.id, name="默认知识库"
    )
    database_session.add(knowledge_base)
    database_session.flush()
    document = Document(
        user_id=user.id,
        space_id=space.id,
        knowledge_base_id=knowledge_base.id,
        filename="vectors.txt",
        file_type="txt",
        file_size=1,
        storage_path="vector-test/vectors.txt",
        status="indexed",
    )
    database_session.add(document)
    database_session.flush()
    database_session.add_all(
        [
            DocumentChunk(
                user_id=user.id,
                space_id=space.id,
                knowledge_base_id=knowledge_base.id,
                document_id=document.id,
                chunk_index=0,
                content="最相似的片段",
                embedding=[1.0] + [0.0] * 1023,
                metadata_={},
            ),
            DocumentChunk(
                user_id=user.id,
                space_id=space.id,
                knowledge_base_id=knowledge_base.id,
                document_id=document.id,
                chunk_index=1,
                content="较不相似的片段",
                embedding=[0.0, 1.0] + [0.0] * 1022,
                metadata_={},
            ),
        ]
    )
    database_session.flush()

    results = retrieval_service.search_documents(
        database_session,
        user,
        space.id,
        "检索问题",
        FakeEmbeddingProvider([[1.0] + [0.0] * 1023]),
    )

    assert [result.content for result in results] == ["最相似的片段", "较不相似的片段"]
    assert results[0].similarity == pytest.approx(1.0)


def test_retrieval_endpoints_use_authenticated_service_and_validate_input(
    monkeypatch: pytest.MonkeyPatch,
):
    from app.api.deps import get_current_user
    from app.db.session import get_db_session
    from app.main import app
    from app.services import retrieval_service
    from fastapi.testclient import TestClient

    user = SimpleNamespace(id=uuid4())
    document = SimpleNamespace(
        id=uuid4(),
        filename="brief.txt",
        file_type="txt",
        file_size=12,
        status="indexed",
        error_message=None,
        created_at="2026-07-16T00:00:00Z",
        updated_at="2026-07-16T00:00:00Z",
    )
    space_id = uuid4()
    monkeypatch.setattr("app.api.v1.documents.index_document", lambda *_args: document)
    monkeypatch.setattr(
        "app.api.v1.retrieval.search_documents",
        lambda *_args, **_kwargs: [
            retrieval_service.RetrievalResult(
                content="命中的片段",
                filename="brief.txt",
                chunk_index=0,
                similarity=0.9,
            )
        ],
    )
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db_session] = lambda: object()
    try:
        with TestClient(app) as client:
            indexed = client.post(f"/api/v1/documents/{document.id}/index")
            searched = client.post(
                f"/api/v1/spaces/{space_id}/retrieval/search",
                json={"query": "检索问题"},
            )
            invalid = client.post(
                f"/api/v1/spaces/{space_id}/retrieval/search", json={"query": "  "}
            )
    finally:
        app.dependency_overrides.clear()

    assert indexed.status_code == 200
    assert indexed.json()["status"] == "indexed"
    assert searched.status_code == 200
    assert searched.json()["results"] == [
        {
            "content": "命中的片段",
            "filename": "brief.txt",
            "chunk_index": 0,
            "similarity": 0.9,
        }
    ]
    assert invalid.status_code == 422


def test_index_endpoint_returns_embedding_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
):
    from app.api.deps import get_current_user
    from app.db.session import get_db_session
    from app.main import app
    from fastapi.testclient import TestClient

    user = SimpleNamespace(id=uuid4())
    monkeypatch.setattr(
        "app.api.v1.documents.index_document",
        lambda *_args: (_ for _ in ()).throw(embedding_not_configured()),
    )
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db_session] = lambda: object()
    try:
        response = TestClient(app).post(f"/api/v1/documents/{uuid4()}/index")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "EMBEDDING_NOT_CONFIGURED"
