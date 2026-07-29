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
