from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db_session
from app.models import User
from app.schemas.document import DocumentResponse
from app.services.document_service import (
    create_document,
    delete_document,
    list_documents,
)
from app.services.document_storage import LocalDocumentStorage

spaces_router = APIRouter(prefix="/spaces", tags=["documents"])
documents_router = APIRouter(prefix="/documents", tags=["documents"])


@spaces_router.post(
    "/{space_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    space_id: UUID,
    file: Annotated[UploadFile, File()],
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> DocumentResponse:
    document = create_document(
        database_session,
        current_user,
        space_id,
        file.filename or "",
        await file.read(),
        LocalDocumentStorage(settings.document_storage_root),
    )
    return DocumentResponse.model_validate(document)


@spaces_router.get("/{space_id}/documents", response_model=list[DocumentResponse])
def get_documents(
    space_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> list[DocumentResponse]:
    return [
        DocumentResponse.model_validate(document)
        for document in list_documents(database_session, current_user, space_id)
    ]


@documents_router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(
    document_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> None:
    delete_document(
        database_session,
        current_user,
        document_id,
        LocalDocumentStorage(settings.document_storage_root),
    )
