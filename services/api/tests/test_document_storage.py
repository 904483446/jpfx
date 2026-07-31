from io import BytesIO
from uuid import uuid4

import pytest
from app.core.errors import AppError
from app.services.document_storage import (
    DocumentStorage,
    LocalDocumentStorage,
)
from fastapi import UploadFile


def test_storage_writes_supported_file_under_user_and_space(tmp_path):
    storage = LocalDocumentStorage(tmp_path)
    stored = storage.save(uuid4(), uuid4(), "brief.PDF", b"pdf")

    assert stored.file_type == "pdf"
    assert stored.size == 3
    assert "brief.PDF" not in stored.relative_path
    assert (tmp_path / stored.relative_path).read_bytes() == b"pdf"


def test_local_storage_implements_document_storage_protocol(tmp_path):
    assert isinstance(LocalDocumentStorage(tmp_path), DocumentStorage)


@pytest.mark.parametrize(
    ("filename", "content", "code"),
    [
        ("brief.exe", b"x", "DOCUMENT_TYPE_NOT_SUPPORTED"),
        ("brief.pdf", b"", "DOCUMENT_EMPTY"),
        pytest.param(
            "brief.pdf",
            b"x" * (20 * 1024 * 1024 + 1),
            "DOCUMENT_TOO_LARGE",
            id="too-large",
        ),
    ],
)
def test_storage_rejects_invalid_content(tmp_path, filename, content, code):
    with pytest.raises(AppError) as captured:
        LocalDocumentStorage(tmp_path).save(uuid4(), uuid4(), filename, content)

    assert captured.value.code == code
    assert not list(tmp_path.rglob("*.txt"))


def test_storage_deletes_saved_file(tmp_path):
    storage = LocalDocumentStorage(tmp_path)
    stored = storage.save(uuid4(), uuid4(), "brief.txt", b"content")

    storage.delete(stored.relative_path)

    assert not (tmp_path / stored.relative_path).exists()


def test_storage_reads_saved_file(tmp_path):
    storage = LocalDocumentStorage(tmp_path)
    stored = storage.save(uuid4(), uuid4(), "brief.txt", b"content")

    assert storage.read(stored.relative_path) == b"content"


@pytest.mark.anyio
async def test_storage_streams_upload_and_removes_partial_oversized_file(tmp_path):
    storage = LocalDocumentStorage(tmp_path)
    upload = UploadFile(
        filename="too-large.txt",
        file=BytesIO(b"x" * (20 * 1024 * 1024 + 1)),
    )

    with pytest.raises(AppError) as captured:
        await storage.save_upload(uuid4(), uuid4(), "too-large.txt", upload)

    assert captured.value.code == "DOCUMENT_TOO_LARGE"
    assert not list(tmp_path.rglob("*.txt"))
