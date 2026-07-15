from uuid import uuid4

import pytest
from app.core.errors import AppError
from app.services.document_storage import LocalDocumentStorage


def test_storage_writes_supported_file_under_user_and_space(tmp_path):
    storage = LocalDocumentStorage(tmp_path)
    stored = storage.save(uuid4(), uuid4(), "brief.PDF", b"pdf")

    assert stored.file_type == "pdf"
    assert stored.size == 3
    assert "brief.PDF" not in stored.relative_path
    assert (tmp_path / stored.relative_path).read_bytes() == b"pdf"


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
    assert list(tmp_path.rglob("*")) == []


def test_storage_deletes_saved_file(tmp_path):
    storage = LocalDocumentStorage(tmp_path)
    stored = storage.save(uuid4(), uuid4(), "brief.txt", b"content")

    storage.delete(stored.relative_path)

    assert not (tmp_path / stored.relative_path).exists()
