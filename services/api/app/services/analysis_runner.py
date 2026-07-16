from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.errors import AppError, analysis_pipeline_error, deepseek_not_configured
from app.db.session import get_session_factory
from app.models import (
    AnalysisTask,
    CompetitorCandidate,
    CompetitorReport,
    ModelConfig,
    TaskEvidence,
    User,
)
from app.services.deepseek_provider import DeepSeekProvider
from app.services.embedding_provider import DashScopeEmbeddingProvider
from app.services.key_cipher import KeyCipher
from app.services.retrieval_service import EmbeddingProvider, search_documents


class ReportCompetitor(BaseModel):
    name: str
    positioning: str
    core_features: list[str]
    target_users: list[str]
    business_model: str
    ai_capabilities: list[str]
    strengths: list[str]
    weaknesses: list[str]
    differentiation_opportunities: list[str]
    recommendations: list[str]
    risks: list[str]


class ReportContent(BaseModel):
    competitors: list[ReportCompetitor] = Field(min_length=1, max_length=3)
    executive_summary: str
    information_sources: list[str]


class JsonCompletionProvider(Protocol):
    def complete_json(
        self, system_prompt: str, user_prompt: str
    ) -> dict[str, object]: ...


def get_deepseek_api_key(database_session: Session, user: User) -> str:
    model_config = database_session.scalar(
        select(ModelConfig).where(
            ModelConfig.user_id == user.id,
            ModelConfig.provider == "deepseek",
        )
    )
    if model_config is None:
        raise deepseek_not_configured()
    return KeyCipher.from_settings().decrypt(model_config.encrypted_api_key)


def run_analysis_task(
    task_id: UUID,
    *,
    session_factory: Callable[[], Session] | sessionmaker[Session] | None = None,
    embedding_provider: EmbeddingProvider | None = None,
    provider_factory: Callable[[str], JsonCompletionProvider] = DeepSeekProvider,
) -> None:
    factory = session_factory or get_session_factory()
    with factory() as database_session:
        task = database_session.get(AnalysisTask, task_id)
        if task is None:
            return
        owner = database_session.get(User, task.user_id)
        if owner is None:
            return
        _execute_analysis_task(
            database_session,
            owner,
            task,
            embedding_provider or DashScopeEmbeddingProvider(),
            provider_factory,
        )


def _execute_analysis_task(
    database_session: Session,
    owner: User,
    task: AnalysisTask,
    embedding_provider: EmbeddingProvider,
    provider_factory: Callable[[str], JsonCompletionProvider],
) -> None:
    if task.status != "queued":
        return
    task.status = "running"
    task.stage = "retrieving_private_knowledge"
    task.error_message = None
    database_session.commit()

    try:
        api_key = get_deepseek_api_key(database_session, owner)
        private_context = search_documents(
            database_session,
            owner,
            task.space_id,
            _retrieval_query(task),
            embedding_provider,
            top_k=8,
        )
        _persist_private_evidence(database_session, task, private_context)
        task.stage = "analyzing"
        database_session.commit()

        selected_competitors = list(
            database_session.scalars(
                select(CompetitorCandidate)
                .where(
                    CompetitorCandidate.task_id == task.id,
                    CompetitorCandidate.user_id == owner.id,
                    CompetitorCandidate.space_id == task.space_id,
                    CompetitorCandidate.is_selected.is_(True),
                )
                .order_by(CompetitorCandidate.sort_order)
            )
        )
        web_evidence = list(
            database_session.scalars(
                select(TaskEvidence).where(
                    TaskEvidence.task_id == task.id,
                    TaskEvidence.user_id == owner.id,
                    TaskEvidence.space_id == task.space_id,
                    TaskEvidence.source_type == "web",
                )
            )
        )
        content = ReportContent.model_validate(
            provider_factory(api_key).complete_json(
                _system_prompt(),
                _user_prompt(task, selected_competitors, private_context, web_evidence),
            )
        )
        database_session.add(
            CompetitorReport(
                user_id=owner.id,
                space_id=task.space_id,
                task_id=task.id,
                title=task.title,
                structured_json=content.model_dump(mode="json"),
            )
        )
        task.status = "completed"
        task.stage = "completed"
        task.completed_at = datetime.now(UTC)
        database_session.commit()
    except AppError:
        _persist_failure(database_session, task)
        raise
    except Exception as error:
        _persist_failure(database_session, task)
        raise analysis_pipeline_error() from error


def _persist_private_evidence(
    database_session: Session, task: AnalysisTask, results: list[object]
) -> None:
    for result in results:
        database_session.add(
            TaskEvidence(
                user_id=task.user_id,
                space_id=task.space_id,
                task_id=task.id,
                source_type="private_knowledge",
                source_title=f"私有知识库：{result.filename}",
                quote=result.content,
                retrieved_at=datetime.now(UTC),
            )
        )


def _persist_failure(database_session: Session, task: AnalysisTask) -> None:
    database_session.rollback()
    task.status = "failed"
    task.stage = "failed"
    task.error_message = "分析任务失败，请检查模型配置或稍后重试"
    database_session.commit()


def _retrieval_query(task: AnalysisTask) -> str:
    return " ".join(
        [task.industry, task.product_direction, *task.keywords, *task.final_competitors]
    )


def _system_prompt() -> str:
    return "你是严谨的竞品分析助手。仅依据提供证据输出中文 JSON，不得编造来源。"


def _user_prompt(
    task: AnalysisTask,
    competitors: list[CompetitorCandidate],
    private_context: list[object],
    web_evidence: list[TaskEvidence],
) -> str:
    competitor_names = [competitor.name for competitor in competitors]
    web_sources = [
        {
            "title": evidence.source_title,
            "url": evidence.source_url,
            "quote": evidence.quote,
        }
        for evidence in web_evidence
    ]
    private_sources = [
        {"filename": result.filename, "content": result.content}
        for result in private_context
    ]
    return (
        f"任务：{task.title}\n"
        f"行业：{task.industry}\n"
        f"方向：{task.product_direction}\n"
        f"最终竞品：{competitor_names}\n"
        f"网页证据：{web_sources}\n"
        f"私有知识库证据：{private_sources}\n"
        "输出 competitors、executive_summary 和 information_sources 字段。"
    )
