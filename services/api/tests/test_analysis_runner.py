from datetime import UTC, datetime

import pytest
from app.core.errors import AppError
from app.models import (
    AnalysisTask,
    CompetitorCandidate,
    CompetitorReport,
    Space,
    TaskEvidence,
    User,
)
from app.services.analysis_runner import ReportContent, run_analysis_task
from app.services.retrieval_service import RetrievalResult
from sqlalchemy.orm import sessionmaker


class FakeDeepSeekProvider:
    def __init__(self) -> None:
        self.prompts: list[tuple[str, str]] = []

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, object]:
        self.prompts.append((system_prompt, user_prompt))
        return {
            "competitors": [
                {
                    "name": "Competitor A",
                    "positioning": "Knowledge base assistant",
                    "core_features": ["Retrieval"],
                    "target_users": ["Teams"],
                    "business_model": "SaaS",
                    "ai_capabilities": ["RAG"],
                    "strengths": ["Fast setup"],
                    "weaknesses": ["Limited customization"],
                    "differentiation_opportunities": ["Chinese workflow"],
                    "recommendations": ["Prioritize citations"],
                    "risks": ["Public information may change"],
                }
            ],
            "executive_summary": "A concise Chinese analysis.",
            "information_sources": ["https://example.com/competitor-a", "brief.txt"],
        }


def _create_queued_task(database_session, user, space):
    task = AnalysisTask(
        user_id=user.id,
        space_id=space.id,
        title="Competitor analysis",
        industry="AI",
        product_direction="Knowledge base",
        keywords=["RAG"],
        known_competitors=[],
        final_competitors=["Competitor A"],
        discovery_mode="semi_auto",
        status="queued",
    )
    database_session.add(task)
    database_session.flush()
    candidate = CompetitorCandidate(
        user_id=user.id,
        space_id=space.id,
        task_id=task.id,
        name="Competitor A",
        source_type="web",
        is_selected=True,
        sort_order=0,
    )
    database_session.add(candidate)
    database_session.add(
        TaskEvidence(
            user_id=user.id,
            space_id=space.id,
            task_id=task.id,
            candidate_id=candidate.id,
            source_type="web",
            source_title="Competitor home page",
            source_url="https://example.com/competitor-a",
            quote="Public product description",
            retrieved_at=datetime.now(UTC),
        )
    )
    database_session.commit()
    return task


def _create_owner_and_space(database_session):
    user = User(
        email="analysis-runner@example.com",
        password_hash="hashed-password",
        display_name="Analysis Runner",
    )
    database_session.add(user)
    database_session.flush()
    space = Space(user_id=user.id, name="Analysis space")
    database_session.add(space)
    database_session.commit()
    return user, space


def _background_session_factory(database_session):
    return sessionmaker(
        bind=database_session.connection(),
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )


def test_analysis_runner_uses_only_task_owner_context_and_persists_report_and_evidence(
    database_session, monkeypatch
):
    user, space = _create_owner_and_space(database_session)
    task = _create_queued_task(database_session, user, space)
    provider = FakeDeepSeekProvider()
    monkeypatch.setattr(
        "app.services.analysis_runner.get_deepseek_api_key", lambda *_: "test-key"
    )
    monkeypatch.setattr(
        "app.services.analysis_runner.search_documents",
        lambda *_args, **_kwargs: [
            RetrievalResult(
                content="Private indexed context",
                filename="brief.txt",
                chunk_index=0,
                similarity=0.9,
            )
        ],
    )

    run_analysis_task(
        task.id,
        session_factory=_background_session_factory(database_session),
        embedding_provider=object(),
        provider_factory=lambda _key: provider,
    )

    database_session.expire_all()
    task = database_session.get(AnalysisTask, task.id)
    assert task is not None
    report = database_session.query(CompetitorReport).filter_by(task_id=task.id).one()
    evidence = database_session.query(TaskEvidence).filter_by(task_id=task.id).all()
    assert task.status == "completed"
    assert task.completed_at is not None
    assert report.structured_json == ReportContent.model_validate(
        provider.complete_json("", "")
    ).model_dump(mode="json")
    assert {item.source_type for item in evidence} == {"web", "private_knowledge"}
    assert provider.prompts


def test_analysis_runner_persists_safe_failure_before_reraising_app_error(
    database_session, monkeypatch
):
    user, space = _create_owner_and_space(database_session)
    task = _create_queued_task(database_session, user, space)
    monkeypatch.setattr(
        "app.services.analysis_runner.get_deepseek_api_key",
        lambda *_: (_ for _ in ()).throw(
            AppError(
                status_code=409,
                code="DEEPSEEK_NOT_CONFIGURED",
                message="DeepSeek API Key is not configured",
            )
        ),
    )

    with pytest.raises(AppError) as captured:
        run_analysis_task(
            task.id,
            session_factory=_background_session_factory(database_session),
        )

    database_session.expire_all()
    task = database_session.get(AnalysisTask, task.id)
    assert task is not None
    assert captured.value.code == "DEEPSEEK_NOT_CONFIGURED"
    assert task.status == "failed"
    assert task.error_message == "分析任务失败，请检查模型配置或稍后重试"
