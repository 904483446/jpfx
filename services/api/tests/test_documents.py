from collections.abc import Generator

import pytest
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import app
from app.schemas.auth import RegisterRequest
from app.schemas.space import SpaceCreateRequest
from app.services.auth_service import register_user
from app.services.document_storage import LocalDocumentStorage, get_document_storage
from app.services.space_service import create_space
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

TEST_SECRET = "test-secret-with-at-least-32-bytes"


@pytest.fixture
def client(
    database_session: Session, monkeypatch: pytest.MonkeyPatch, tmp_path
) -> Generator[TestClient, None, None]:
    def override_database_session() -> Generator[Session, None, None]:
        yield database_session

    monkeypatch.setattr(settings, "jwt_secret", TEST_SECRET)
    monkeypatch.setattr(settings, "document_storage_root", tmp_path)
    app.dependency_overrides[get_db_session] = override_database_session
    app.dependency_overrides[get_document_storage] = lambda: LocalDocumentStorage(
        tmp_path
    )
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def authenticate(client: TestClient, database_session: Session, email: str):
    user = register_user(
        database_session,
        RegisterRequest(
            email=email,
            password="valid-password",
            display_name="文档测试用户",
        ),
    )
    client.cookies.set(settings.auth_cookie_name, create_access_token(user.id))
    return user


def test_current_user_can_upload_list_and_delete_own_document(
    client: TestClient, database_session: Session
):
    user = authenticate(client, database_session, "documents@example.com")
    space = create_space(database_session, user, SpaceCreateRequest(name="文档空间"))

    uploaded = client.post(
        f"/api/v1/spaces/{space.id}/documents",
        files={"file": ("brief.txt", b"knowledge base", "text/plain")},
    )

    assert uploaded.status_code == 201
    document = uploaded.json()
    assert document["filename"] == "brief.txt"
    assert document["file_type"] == "txt"
    assert document["file_size"] == 14
    assert document["status"] == "uploaded"
    assert document["error_message"] is None
    assert "storage_path" not in document
    assert client.get(f"/api/v1/spaces/{space.id}/documents").json() == [document]
    assert client.delete(f"/api/v1/documents/{document['id']}").status_code == 204
    assert client.get(f"/api/v1/spaces/{space.id}/documents").json() == []


def test_document_upload_rejects_invalid_file(
    client: TestClient, database_session: Session
):
    user = authenticate(client, database_session, "invalid-document@example.com")
    space = create_space(database_session, user, SpaceCreateRequest(name="校验空间"))

    response = client.post(
        f"/api/v1/spaces/{space.id}/documents",
        files={"file": ("brief.exe", b"x", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert response.json()["error"] == {
        "code": "DOCUMENT_TYPE_NOT_SUPPORTED",
        "message": "仅支持 PDF、DOCX、TXT 和 MD 文档",
        "details": {},
    }


def test_document_client_fixture_overrides_and_cleans_up_document_storage(
    monkeypatch: pytest.MonkeyPatch, tmp_path
):
    fixture = client.__wrapped__(object(), monkeypatch, tmp_path)

    next(fixture)
    storage = app.dependency_overrides[get_document_storage]()

    assert isinstance(storage, LocalDocumentStorage)
    assert storage.root == tmp_path.resolve()

    with pytest.raises(StopIteration):
        next(fixture)

    assert get_document_storage not in app.dependency_overrides
