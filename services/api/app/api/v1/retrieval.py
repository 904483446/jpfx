from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models import User
from app.schemas.retrieval import RetrievalSearchRequest, RetrievalSearchResponse
from app.services.embedding_provider import DashScopeEmbeddingProvider
from app.services.retrieval_service import search_documents

router = APIRouter(prefix="/spaces", tags=["retrieval"])


@router.post("/{space_id}/retrieval/search", response_model=RetrievalSearchResponse)
def search_space_documents(
    space_id: UUID,
    payload: RetrievalSearchRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> RetrievalSearchResponse:
    results = search_documents(
        database_session,
        current_user,
        space_id,
        payload.query,
        DashScopeEmbeddingProvider(),
        top_k=payload.top_k,
    )
    return RetrievalSearchResponse(results=results)
