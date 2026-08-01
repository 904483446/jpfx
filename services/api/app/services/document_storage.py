from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable
from uuid import UUID, uuid4

import httpx
from fastapi import UploadFile

from app.core.config import Settings, settings
from app.core.errors import (
    AppError,
    document_empty,
    document_storage_error,
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


@runtime_checkable
class DocumentStorage(Protocol):
    def save(
        self, user_id: UUID, space_id: UUID, filename: str, content: bytes
    ) -> StoredDocument: ...

    async def save_upload(
        self, user_id: UUID, space_id: UUID, filename: str, upload: UploadFile
    ) -> StoredDocument: ...

    def read(self, relative_path: str) -> bytes: ...

    def delete(self, relative_path: str) -> None: ...


def create_document_storage(configuration: Settings = settings) -> DocumentStorage:
    if (
        configuration.supabase_url is not None
        and configuration.supabase_secret_key is not None
    ):
        return SupabaseDocumentStorage(
            configuration.supabase_url,
            configuration.supabase_secret_key,
            configuration.supabase_storage_bucket,
        )
    return LocalDocumentStorage(configuration.document_storage_root)


def get_document_storage() -> DocumentStorage:
    return create_document_storage()


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

    async def save_upload(
        self, user_id: UUID, space_id: UUID, filename: str, upload: UploadFile
    ) -> StoredDocument:
        file_type = Path(filename).suffix.lower().lstrip(".")
        if file_type not in SUPPORTED_DOCUMENT_TYPES:
            raise document_type_not_supported()
        relative_path = (
            Path(str(user_id)) / str(space_id) / f"{uuid4().hex}.{file_type}"
        )
        target = self.root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        size = 0
        try:
            with target.open("wb") as destination:
                while chunk := await upload.read(64 * 1024):
                    size += len(chunk)
                    if size > MAX_DOCUMENT_SIZE:
                        raise document_too_large()
                    destination.write(chunk)
            if size == 0:
                raise document_empty()
        except Exception:
            target.unlink(missing_ok=True)
            raise
        return StoredDocument(str(relative_path), file_type, size)

    def delete(self, relative_path: str) -> None:
        target = (self.root / relative_path).resolve()
        if not target.is_relative_to(self.root):
            return
        target.unlink(missing_ok=True)

    def read(self, relative_path: str) -> bytes:
        target = (self.root / relative_path).resolve()
        if not target.is_relative_to(self.root):
            raise FileNotFoundError(relative_path)
        return target.read_bytes()


class SupabaseDocumentStorage:
    def __init__(
        self,
        url: str,
        key: str,
        bucket: str,
        *,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.url = url.rstrip("/")
        self.key = key
        self.bucket = bucket
        self.timeout = timeout
        self.transport = transport

    def save(
        self, user_id: UUID, space_id: UUID, filename: str, content: bytes
    ) -> StoredDocument:
        file_type = self._validate_content(filename, content)
        relative_path = self._new_relative_path(user_id, space_id, file_type)
        try:
            with self._client() as client:
                response = client.post(
                    self._object_url(relative_path),
                    content=content,
                    headers=self._headers(),
                )
            self._raise_for_unsuccessful_response(response)
        except AppError:
            self._cleanup_failed_upload(relative_path)
            raise
        except httpx.HTTPError as error:
            self._cleanup_failed_upload(relative_path)
            raise document_storage_error() from error
        return StoredDocument(relative_path, file_type, len(content))

    async def save_upload(
        self, user_id: UUID, space_id: UUID, filename: str, upload: UploadFile
    ) -> StoredDocument:
        file_type = Path(filename).suffix.lower().lstrip(".")
        if file_type not in SUPPORTED_DOCUMENT_TYPES:
            raise document_type_not_supported()

        relative_path = self._new_relative_path(user_id, space_id, file_type)
        size = 0

        async def content_chunks():
            nonlocal size
            while chunk := await upload.read(64 * 1024):
                size += len(chunk)
                if size > MAX_DOCUMENT_SIZE:
                    raise document_too_large()
                yield chunk
            if size == 0:
                raise document_empty()

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                transport=self.transport,
            ) as client:
                response = await client.post(
                    self._object_url(relative_path),
                    content=content_chunks(),
                    headers=self._headers(),
                )
            self._raise_for_unsuccessful_response(response)
        except httpx.HTTPError as error:
            self._cleanup_failed_upload(relative_path)
            raise document_storage_error() from error
        except Exception:
            self._cleanup_failed_upload(relative_path)
            raise
        return StoredDocument(relative_path, file_type, size)

    def read(self, relative_path: str) -> bytes:
        try:
            with self._client() as client:
                response = client.get(
                    self._object_url(relative_path), headers=self._headers()
                )
            self._raise_for_unsuccessful_response(response)
        except AppError:
            raise
        except httpx.HTTPError as error:
            raise document_storage_error() from error
        return response.content

    def delete(self, relative_path: str) -> None:
        try:
            with self._client() as client:
                response = client.delete(
                    self._object_url(relative_path), headers=self._headers()
                )
            if response.status_code == 404:
                return
            self._raise_for_unsuccessful_response(response)
        except AppError:
            raise
        except httpx.HTTPError as error:
            raise document_storage_error() from error

    def _client(self) -> httpx.Client:
        return httpx.Client(timeout=self.timeout, transport=self.transport)

    def _headers(self) -> dict[str, str]:
        return {
            "apikey": self.key,
            "Content-Type": "application/octet-stream",
        }

    def _new_relative_path(self, user_id: UUID, space_id: UUID, file_type: str) -> str:
        return str(Path(str(user_id)) / str(space_id) / f"{uuid4().hex}.{file_type}")

    def _cleanup_failed_upload(self, relative_path: str) -> None:
        try:
            self.delete(relative_path)
        except AppError:
            pass

    def _object_url(self, relative_path: str) -> str:
        return f"{self.url}/storage/v1/object/{self.bucket}/{relative_path}"

    @staticmethod
    def _validate_content(filename: str, content: bytes) -> str:
        file_type = Path(filename).suffix.lower().lstrip(".")
        if file_type not in SUPPORTED_DOCUMENT_TYPES:
            raise document_type_not_supported()
        if not content:
            raise document_empty()
        if len(content) > MAX_DOCUMENT_SIZE:
            raise document_too_large()
        return file_type

    @staticmethod
    def _raise_for_unsuccessful_response(response: httpx.Response) -> None:
        if not response.is_success:
            raise document_storage_error()
