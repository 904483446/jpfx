from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.core.config import Settings
from app.services.document_storage import StoredDocument
from fastapi import UploadFile


class RecordingStorage:
    def __init__(self, content: bytes = b"indexable content") -> None:
        self.content = content
        self.deleted: list[str] = []
        self.read_paths: list[str] = []

    def save(self, user_id, space_id, filename, content):
        return StoredDocument("user/space/document.txt", "txt", len(content))

    async def save_upload(self, user_id, space_id, filename, upload):
        return StoredDocument("user/space/document.txt", "txt", len(self.content))

    def read(self, relative_path: str) -> bytes:
        self.read_paths.append(relative_path)
        return self.content

    def delete(self, relative_path: str) -> None:
        self.deleted.append(relative_path)


def test_document_storage_factory_uses_supabase_only_with_complete_configuration(
    tmp_path: Path,
):
    from app.services.document_storage import (
        LocalDocumentStorage,
        SupabaseDocumentStorage,
        create_document_storage,
    )

    local = create_document_storage(
        Settings(_env_file=None, document_storage_root=tmp_path)
    )
    remote = create_document_storage(
        Settings(
            _env_file=None,
            document_storage_root=tmp_path,
            supabase_url="https://project.supabase.co",
            supabase_service_role_key="test-service-role-key",
            supabase_storage_bucket="test-documents",
        )
    )

    assert isinstance(local, LocalDocumentStorage)
    assert isinstance(remote, SupabaseDocumentStorage)
    assert remote.url == "https://project.supabase.co"
    assert remote.key == "test-service-role-key"
    assert remote.bucket == "test-documents"


@pytest.mark.anyio
async def test_upload_endpoint_passes_injected_factory_storage_to_document_service(
    monkeypatch: pytest.MonkeyPatch,
):
    from app.api.v1 import documents

    storage = RecordingStorage()
    captured: dict[str, object] = {}
    user = SimpleNamespace(id=uuid4())
    document = SimpleNamespace(
        id=uuid4(),
        user_id=user.id,
        space_id=uuid4(),
        knowledge_base_id=uuid4(),
        filename="brief.txt",
        file_type="txt",
        file_size=4,
        storage_path="user/space/document.txt",
        status="uploaded",
        error_message=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    async def fake_create_uploaded_document(*args):
        captured["storage"] = args[-1]
        return document

    monkeypatch.setattr(
        documents, "create_uploaded_document", fake_create_uploaded_document
    )
    result = await documents.upload_document(
        document.space_id,
        UploadFile(filename="brief.txt", file=BytesIO(b"test")),
        user,
        object(),
        storage,
    )

    assert captured["storage"] is storage
    assert result.filename == "brief.txt"


def test_delete_endpoint_passes_injected_factory_storage_to_document_service(
    monkeypatch: pytest.MonkeyPatch,
):
    from app.api.v1 import documents

    storage = RecordingStorage()
    captured: dict[str, object] = {}

    def fake_delete_document(*args):
        captured["storage"] = args[-1]

    monkeypatch.setattr(documents, "delete_document", fake_delete_document)
    documents.remove_document(uuid4(), SimpleNamespace(id=uuid4()), object(), storage)

    assert captured["storage"] is storage


def test_create_document_deletes_stored_object_when_database_commit_fails():
    from app.services.document_service import create_document

    user = SimpleNamespace(id=uuid4())
    space = SimpleNamespace(id=uuid4())
    storage = RecordingStorage()

    class FailingSession:
        def __init__(self) -> None:
            self.rolled_back = False

        def scalar(self, statement):
            return SimpleNamespace(id=uuid4())

        def add(self, document):
            pass

        def commit(self):
            raise RuntimeError("database unavailable")

        def rollback(self):
            self.rolled_back = True

    session = FailingSession()

    with pytest.raises(RuntimeError, match="database unavailable"):
        create_document(session, user, space.id, "brief.txt", b"test", storage)

    assert session.rolled_back is True
    assert storage.deleted == ["user/space/document.txt"]


def test_index_document_reads_bytes_from_injected_storage(
    monkeypatch: pytest.MonkeyPatch,
):
    from app.services import retrieval_service

    user = SimpleNamespace(id=uuid4())
    document = SimpleNamespace(
        id=uuid4(),
        user_id=user.id,
        space_id=uuid4(),
        knowledge_base_id=uuid4(),
        filename="brief.txt",
        storage_path="user/space/document.txt",
        status="uploaded",
        error_message=None,
    )
    storage = RecordingStorage(b"indexable content")

    class Session:
        def add(self, value):
            pass

        def execute(self, statement):
            pass

        def commit(self):
            pass

        def rollback(self):
            pass

    class Provider:
        def embed(self, texts):
            return [[0.1] * 1024]

    monkeypatch.setattr(retrieval_service, "get_owned_document", lambda *_: document)
    monkeypatch.setattr(
        retrieval_service,
        "chunk_text",
        lambda text: [SimpleNamespace(index=0, content=text)],
    )

    result = retrieval_service.index_document(
        Session(), user, document.id, storage, Provider()
    )

    assert result.status == "indexed"
    assert storage.read_paths == ["user/space/document.txt"]
