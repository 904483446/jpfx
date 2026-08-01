from io import BytesIO
from uuid import uuid4

import httpx
import pytest
from app.core.errors import AppError
from app.services.document_storage import DocumentStorage, SupabaseDocumentStorage
from fastapi import UploadFile


def test_supabase_storage_uploads_private_object_with_safe_path_and_headers():
    captured_request: httpx.Request | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request
        captured_request = request
        return httpx.Response(200)

    storage = SupabaseDocumentStorage(
        "https://project.supabase.co/",
        "test-storage-key",
        "documents",
        transport=httpx.MockTransport(handler),
    )
    user_id, space_id = uuid4(), uuid4()

    stored = storage.save(user_id, space_id, "brief.PDF", b"pdf")

    assert isinstance(storage, DocumentStorage)
    assert stored.file_type == "pdf"
    assert stored.size == 3
    assert captured_request is not None
    assert captured_request.method == "POST"
    assert (
        captured_request.url.path
        == f"/storage/v1/object/documents/{stored.relative_path}"
    )
    assert captured_request.headers["apikey"] == "test-storage-key"
    assert "authorization" not in captured_request.headers
    assert captured_request.content == b"pdf"


def test_supabase_storage_reads_and_deletes_private_object():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, content=b"content")

    storage = SupabaseDocumentStorage(
        "https://project.supabase.co",
        "test-storage-key",
        "documents",
        transport=httpx.MockTransport(handler),
    )

    assert storage.read("user/space/document.txt") == b"content"
    storage.delete("user/space/document.txt")

    assert [(request.method, request.url.path) for request in requests] == [
        ("GET", "/storage/v1/object/documents/user/space/document.txt"),
        ("DELETE", "/storage/v1/object/documents/user/space/document.txt"),
    ]


def test_supabase_storage_ignores_delete_not_found():
    storage = SupabaseDocumentStorage(
        "https://project.supabase.co",
        "test-storage-key",
        "documents",
        transport=httpx.MockTransport(lambda request: httpx.Response(404)),
    )

    storage.delete("user/space/missing.txt")


@pytest.mark.parametrize(
    ("filename", "content", "code"),
    [
        pytest.param(
            "brief.exe", b"x", "DOCUMENT_TYPE_NOT_SUPPORTED", id="unsupported-type"
        ),
        pytest.param("brief.pdf", b"", "DOCUMENT_EMPTY", id="empty"),
        pytest.param(
            "brief.pdf",
            b"x" * (20 * 1024 * 1024 + 1),
            "DOCUMENT_TOO_LARGE",
            id="too-large",
        ),
    ],
)
def test_supabase_storage_preserves_local_validation(filename, content, code):
    storage = SupabaseDocumentStorage(
        "https://project.supabase.co",
        "test-storage-key",
        "documents",
        transport=httpx.MockTransport(lambda request: httpx.Response(200)),
    )

    with pytest.raises(AppError) as captured:
        storage.save(uuid4(), uuid4(), filename, content)

    assert captured.value.code == code


def test_supabase_storage_converts_failed_upload_to_safe_app_error():
    secret = "test-storage-key"
    storage = SupabaseDocumentStorage(
        "https://project.supabase.co",
        secret,
        "documents",
        transport=httpx.MockTransport(
            lambda request: httpx.Response(503, text="secret body")
        ),
    )

    with pytest.raises(AppError) as captured:
        storage.save(uuid4(), uuid4(), "brief.txt", b"content")

    assert captured.value.code == "DOCUMENT_STORAGE_ERROR"
    assert secret not in str(captured.value)
    assert "project.supabase.co" not in str(captured.value)
    assert "secret body" not in str(captured.value)


def test_supabase_storage_cleans_up_after_sync_upload_failure():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(503 if request.method == "POST" else 200)

    storage = SupabaseDocumentStorage(
        "https://project.supabase.co",
        "test-storage-key",
        "documents",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(AppError, match="文档存储服务暂时不可用"):
        storage.save(uuid4(), uuid4(), "brief.txt", b"content")

    assert [request.method for request in requests] == ["POST", "DELETE"]


def test_supabase_storage_cleans_up_after_sync_upload_transport_error():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "POST":
            raise httpx.ConnectError("unavailable", request=request)
        return httpx.Response(200)

    storage = SupabaseDocumentStorage(
        "https://project.supabase.co",
        "test-storage-key",
        "documents",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(AppError, match="文档存储服务暂时不可用"):
        storage.save(uuid4(), uuid4(), "brief.txt", b"content")

    assert [request.method for request in requests] == ["POST", "DELETE"]


@pytest.mark.anyio
async def test_supabase_storage_streams_upload_and_removes_created_object_on_failure():
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200)

    storage = SupabaseDocumentStorage(
        "https://project.supabase.co",
        "test-storage-key",
        "documents",
        transport=httpx.MockTransport(handler),
    )
    upload = UploadFile(
        filename="too-large.txt",
        file=BytesIO(b"x" * (20 * 1024 * 1024 + 1)),
    )

    with pytest.raises(AppError) as captured:
        await storage.save_upload(uuid4(), uuid4(), "too-large.txt", upload)

    assert captured.value.code == "DOCUMENT_TOO_LARGE"
    assert [request.method for request in requests] == ["DELETE"]
