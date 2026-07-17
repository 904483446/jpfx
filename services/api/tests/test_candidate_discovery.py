from collections.abc import Sequence

from app.models.analysis_task import AnalysisTask
from app.models.competitor_candidate import CompetitorCandidate
from app.models.space import Space
from app.models.task_evidence import TaskEvidence
from app.models.user import User
from app.services.bocha_search_provider import SearchResult
from app.services.candidate_discovery_service import discover_candidates
from sqlalchemy import select


class FakeSearchProvider:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def search(self, query: str, *, limit: int = 10) -> Sequence[SearchResult]:
        self.queries.append(query)
        return [
            SearchResult(
                title="  Example AI  ",
                url="HTTPS://Example.com/product/?utm_source=search",
                summary="A product discovered from public web search.",
            ),
            SearchResult(
                title="Example AI",
                url="https://example.com/product",
                summary="Duplicate result from another query.",
            ),
        ]


def test_discovery_saves_deduplicated_candidates_with_web_evidence(database_session):
    user = User(
        email="candidate-discovery@example.com",
        password_hash="hash",
        display_name="Candidate Discovery",
    )
    database_session.add(user)
    database_session.flush()
    space = Space(user_id=user.id, name="Discovery Space")
    database_session.add(space)
    database_session.flush()
    task = AnalysisTask(
        user_id=user.id,
        space_id=space.id,
        title="AI writing competitors",
        industry="AI",
        product_direction="writing assistant",
        keywords=["collaboration", "content"],
        known_competitors=["Known Product"],
    )
    database_session.add(task)
    database_session.flush()

    provider = FakeSearchProvider()
    candidates = discover_candidates(database_session, user, task, provider)

    assert [candidate.name for candidate in candidates] == ["Example AI"]
    assert candidates[0].source_type == "web"
    assert set(provider.queries) >= {
        "AI writing assistant collaboration content",
        "Known Product",
    }
    evidence = database_session.scalar(
        select(TaskEvidence).where(TaskEvidence.candidate_id == candidates[0].id)
    )
    assert evidence is not None
    assert evidence.source_type == "web"
    assert evidence.source_title == "Example AI"
    assert evidence.source_url == "https://example.com/product"
    assert evidence.quote == "A product discovered from public web search."
    assert evidence.retrieved_at is not None
    assert database_session.scalars(select(CompetitorCandidate)).all() == candidates
