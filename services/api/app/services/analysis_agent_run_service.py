from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AnalysisAgentRun, AnalysisTask
from app.models.analysis_agent_run import AGENT_KEYS


def create_agent_run_attempt(
    database_session: Session, task: AnalysisTask
) -> list[AnalysisAgentRun]:
    previous_attempt = database_session.scalar(
        select(func.max(AnalysisAgentRun.attempt)).where(
            AnalysisAgentRun.task_id == task.id,
            AnalysisAgentRun.user_id == task.user_id,
            AnalysisAgentRun.space_id == task.space_id,
        )
    )
    attempt = (previous_attempt or 0) + 1
    runs = [
        AnalysisAgentRun(
            task_id=task.id,
            user_id=task.user_id,
            space_id=task.space_id,
            attempt=attempt,
            agent_key=agent_key,
            status="queued",
        )
        for agent_key in AGENT_KEYS
    ]
    database_session.add_all(runs)
    return runs


def list_agent_runs(
    database_session: Session, task: AnalysisTask
) -> list[AnalysisAgentRun]:
    runs = list(
        database_session.scalars(
            select(AnalysisAgentRun).where(
                AnalysisAgentRun.task_id == task.id,
                AnalysisAgentRun.user_id == task.user_id,
                AnalysisAgentRun.space_id == task.space_id,
            )
        )
    )
    key_position = {
        agent_key: position for position, agent_key in enumerate(AGENT_KEYS)
    }
    return sorted(runs, key=lambda run: (run.attempt, key_position[run.agent_key]))


def start_agent_run(
    database_session: Session, task: AnalysisTask, agent_key: str
) -> None:
    _current_agent_run(database_session, task, agent_key).status = "running"
    _current_agent_run(database_session, task, agent_key).started_at = datetime.now(UTC)


def complete_agent_run(
    database_session: Session, task: AnalysisTask, agent_key: str
) -> None:
    run = _current_agent_run(database_session, task, agent_key)
    run.status = "completed"
    run.completed_at = datetime.now(UTC)


def fail_agent_run(
    database_session: Session, task: AnalysisTask, agent_key: str, message: str
) -> None:
    run = _current_agent_run(database_session, task, agent_key)
    run.status = "failed"
    run.completed_at = datetime.now(UTC)
    run.error_message = message
    database_session.query(AnalysisAgentRun).filter(
        AnalysisAgentRun.task_id == task.id,
        AnalysisAgentRun.user_id == task.user_id,
        AnalysisAgentRun.space_id == task.space_id,
        AnalysisAgentRun.attempt == run.attempt,
        AnalysisAgentRun.status == "queued",
    ).update({"status": "skipped", "completed_at": datetime.now(UTC)})


def _current_agent_run(
    database_session: Session, task: AnalysisTask, agent_key: str
) -> AnalysisAgentRun:
    attempt = database_session.scalar(
        select(func.max(AnalysisAgentRun.attempt)).where(
            AnalysisAgentRun.task_id == task.id,
            AnalysisAgentRun.user_id == task.user_id,
            AnalysisAgentRun.space_id == task.space_id,
        )
    )
    assert attempt is not None
    run = database_session.scalar(
        select(AnalysisAgentRun).where(
            AnalysisAgentRun.task_id == task.id,
            AnalysisAgentRun.user_id == task.user_id,
            AnalysisAgentRun.space_id == task.space_id,
            AnalysisAgentRun.attempt == attempt,
            AnalysisAgentRun.agent_key == agent_key,
        )
    )
    assert run is not None
    return run
