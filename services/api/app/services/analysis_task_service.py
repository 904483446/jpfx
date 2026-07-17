from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import (
    analysis_task_not_found,
    invalid_competitor_selection,
    invalid_task_state,
)
from app.models import AnalysisTask, CompetitorCandidate, TaskEvidence, User
from app.schemas.analysis_task import AnalysisTaskCreateRequest
from app.services.candidate_discovery_service import SearchProvider, discover_candidates
from app.services.space_service import get_space

_ALLOWED_TRANSITIONS = {
    "draft": {"queued"},
    "queued": {"running"},
    "running": {"completed", "failed"},
    "failed": {"queued"},
    "completed": set(),
}


def create_analysis_task(
    database_session: Session,
    user: User,
    space_id: UUID,
    payload: AnalysisTaskCreateRequest,
) -> AnalysisTask:
    space = get_space(database_session, user, space_id)
    task = AnalysisTask(
        user_id=user.id,
        space_id=space.id,
        title=payload.title,
        industry=payload.industry,
        product_direction=payload.product_direction,
        keywords=payload.keywords,
        known_competitors=payload.known_competitors,
        discovery_mode=payload.discovery_mode,
    )
    database_session.add(task)
    database_session.commit()
    database_session.refresh(task)
    return task


def get_analysis_task(
    database_session: Session, user: User, task_id: UUID
) -> AnalysisTask:
    task = database_session.scalar(
        select(AnalysisTask).where(
            AnalysisTask.id == task_id,
            AnalysisTask.user_id == user.id,
        )
    )
    if task is None:
        raise analysis_task_not_found()
    get_space(database_session, user, task.space_id)
    return task


def discover_task_candidates(
    database_session: Session,
    user: User,
    task_id: UUID,
    search_provider: SearchProvider,
) -> AnalysisTask:
    task = get_analysis_task(database_session, user, task_id)
    _require_draft_candidate_mutation(task)
    discover_candidates(database_session, user, task, search_provider)
    return task


def select_competitors(
    database_session: Session,
    user: User,
    task_id: UUID,
    candidate_ids: Sequence[UUID],
) -> AnalysisTask:
    task = get_analysis_task(database_session, user, task_id)
    _require_draft_candidate_mutation(task)
    if not 1 <= len(candidate_ids) <= 3 or len(set(candidate_ids)) != len(
        candidate_ids
    ):
        raise invalid_competitor_selection()
    candidates = list(
        database_session.scalars(
            select(CompetitorCandidate).where(
                CompetitorCandidate.id.in_(candidate_ids),
                CompetitorCandidate.task_id == task.id,
                CompetitorCandidate.space_id == task.space_id,
                CompetitorCandidate.user_id == user.id,
            )
        )
    )
    if len(candidates) != len(candidate_ids):
        raise invalid_competitor_selection()
    _set_selected_candidates(database_session, task, candidates, candidate_ids)
    return task


def auto_select_competitors(
    database_session: Session, user: User, task_id: UUID
) -> AnalysisTask:
    task = get_analysis_task(database_session, user, task_id)
    _require_draft_candidate_mutation(task)
    rows = database_session.execute(
        select(CompetitorCandidate)
        .join(TaskEvidence, TaskEvidence.candidate_id == CompetitorCandidate.id)
        .where(
            CompetitorCandidate.task_id == task.id,
            CompetitorCandidate.space_id == task.space_id,
            CompetitorCandidate.user_id == user.id,
            TaskEvidence.task_id == task.id,
            TaskEvidence.space_id == task.space_id,
            TaskEvidence.user_id == user.id,
            TaskEvidence.source_type == "web",
        )
        .order_by(CompetitorCandidate.created_at, CompetitorCandidate.id)
    )
    candidates: list[CompetitorCandidate] = []
    seen: set[UUID] = set()
    for candidate in rows.scalars():
        if candidate.id not in seen:
            candidates.append(candidate)
            seen.add(candidate.id)
        if len(candidates) == 3:
            break
    _set_selected_candidates(
        database_session, task, candidates, [candidate.id for candidate in candidates]
    )
    return task


def retry_analysis_task(
    database_session: Session, user: User, task_id: UUID
) -> AnalysisTask:
    task = get_analysis_task(database_session, user, task_id)
    transition_task(task, "queued")
    task.error_message = None
    task.stage = None
    database_session.commit()
    database_session.refresh(task)
    return task


def queue_analysis_task(
    database_session: Session, user: User, task_id: UUID
) -> AnalysisTask:
    task = get_analysis_task(database_session, user, task_id)
    if not 1 <= len(task.final_competitors) <= 3:
        raise invalid_competitor_selection()
    transition_task(task, "queued")
    task.error_message = None
    task.stage = "queued"
    database_session.commit()
    database_session.refresh(task)
    return task


def transition_task(task: AnalysisTask, target: str) -> None:
    if target not in _ALLOWED_TRANSITIONS.get(task.status, set()):
        raise invalid_task_state()
    task.status = target


def _require_draft_candidate_mutation(task: AnalysisTask) -> None:
    if task.status != "draft":
        raise invalid_task_state()


def list_task_candidates(
    database_session: Session, task: AnalysisTask
) -> list[CompetitorCandidate]:
    return list(
        database_session.scalars(
            select(CompetitorCandidate)
            .where(
                CompetitorCandidate.task_id == task.id,
                CompetitorCandidate.space_id == task.space_id,
                CompetitorCandidate.user_id == task.user_id,
            )
            .order_by(CompetitorCandidate.created_at, CompetitorCandidate.id)
        )
    )


def _set_selected_candidates(
    database_session: Session,
    task: AnalysisTask,
    selected: Sequence[CompetitorCandidate],
    selected_ids: Sequence[UUID],
) -> None:
    for candidate in list_task_candidates(database_session, task):
        candidate.is_selected = candidate.id in selected_ids
        candidate.sort_order = (
            selected_ids.index(candidate.id) if candidate.is_selected else None
        )
    task.final_competitors = [candidate.name for candidate in selected]
    database_session.commit()
    database_session.refresh(task)
