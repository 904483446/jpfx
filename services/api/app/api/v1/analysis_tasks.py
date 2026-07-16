from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models import User
from app.schemas.analysis_task import (
    AnalysisTaskCreateRequest,
    AnalysisTaskResponse,
    CandidateResponse,
    CompetitorSelectionRequest,
)
from app.services.analysis_runner import run_analysis_task
from app.services.analysis_task_service import (
    auto_select_competitors,
    create_analysis_task,
    discover_task_candidates,
    get_analysis_task,
    list_task_candidates,
    queue_analysis_task,
    retry_analysis_task,
    select_competitors,
)
from app.services.bocha_search_provider import BochaSearchProvider

spaces_router = APIRouter(prefix="/spaces", tags=["analysis-tasks"])
tasks_router = APIRouter(prefix="/analysis-tasks", tags=["analysis-tasks"])


def _task_response(database_session: Session, task) -> AnalysisTaskResponse:
    response = AnalysisTaskResponse.model_validate(task)
    response.candidates = [
        CandidateResponse.model_validate(candidate)
        for candidate in list_task_candidates(database_session, task)
    ]
    return response


@spaces_router.post(
    "/{space_id}/analysis-tasks",
    response_model=AnalysisTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    space_id: UUID,
    payload: AnalysisTaskCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> AnalysisTaskResponse:
    task = create_analysis_task(database_session, current_user, space_id, payload)
    return _task_response(database_session, task)


@tasks_router.post(
    "/{task_id}/candidates/discover", response_model=AnalysisTaskResponse
)
def discover_candidates(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> AnalysisTaskResponse:
    task = discover_task_candidates(
        database_session, current_user, task_id, BochaSearchProvider()
    )
    return _task_response(database_session, task)


@tasks_router.put("/{task_id}/competitors", response_model=AnalysisTaskResponse)
def confirm_competitors(
    task_id: UUID,
    payload: CompetitorSelectionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> AnalysisTaskResponse:
    task = select_competitors(
        database_session, current_user, task_id, payload.candidate_ids
    )
    return _task_response(database_session, task)


@tasks_router.post(
    "/{task_id}/competitors/auto-select", response_model=AnalysisTaskResponse
)
def auto_select(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> AnalysisTaskResponse:
    task = auto_select_competitors(database_session, current_user, task_id)
    return _task_response(database_session, task)


@tasks_router.post(
    "/{task_id}/run",
    response_model=AnalysisTaskResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def run_task(
    task_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> AnalysisTaskResponse:
    task = queue_analysis_task(database_session, current_user, task_id)
    background_tasks.add_task(run_analysis_task, task.id)
    return _task_response(database_session, task)


@tasks_router.get("/{task_id}", response_model=AnalysisTaskResponse)
def get_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> AnalysisTaskResponse:
    task = get_analysis_task(database_session, current_user, task_id)
    return _task_response(database_session, task)


@tasks_router.post("/{task_id}/retry", response_model=AnalysisTaskResponse)
def retry_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> AnalysisTaskResponse:
    task = retry_analysis_task(database_session, current_user, task_id)
    return _task_response(database_session, task)
