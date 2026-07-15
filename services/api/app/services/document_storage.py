from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

from app.core.errors import (
    document_empty,
    document_too_large,
    document_type_not_supported,
)

MAX_DOCUMENT_SIZE = 20 * 1024 * 1024
SUPPORTED_DOCUMENT_TYPES = {"pdf", "docx", "txt", "md"}


@dataclass(frozen=True)
class StoredDocument:
    relative_path: str
    file_type: str
    size: int


class LocalDocumentStorage:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def save(
        self, user_id: UUID, space_id: UUID, filename: str, content: bytes
    ) -> StoredDocument:
        file_type = Path(filename).suffix.lower().lstrip(".")
        if file_type not in SUPPORTED_DOCUMENT_TYPES:
            raise document_type_not_supported()
        if not content:
            raise document_empty()
        if len(content) > MAX_DOCUMENT_SIZE:
            raise document_too_large()

        relative_path = (
            Path(str(user_id)) / str(space_id) / f"{uuid4().hex}.{file_type}"
        )
        target = self.root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return StoredDocument(str(relative_path), file_type, len(content))

    def delete(self, relative_path: str) -> None:
        target = (self.root / relative_path).resolve()
        if not target.is_relative_to(self.root):
            return
        target.unlink(missing_ok=True)
