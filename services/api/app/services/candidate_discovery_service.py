from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from typing import Protocol
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analysis_task import AnalysisTask
from app.models.competitor_candidate import CompetitorCandidate
from app.models.task_evidence import TaskEvidence
from app.models.user import User
from app.services.bocha_search_provider import SearchResult


class SearchProvider(Protocol):
    def search(self, query: str, *, limit: int = 10) -> Sequence[SearchResult]: ...


def discover_candidates(
    database_session: Session,
    user: User,
    task: AnalysisTask,
    search_provider: SearchProvider,
) -> list[CompetitorCandidate]:
    """Discover and persist public-web candidates within the task owner boundary."""
    _validate_task_owner(user, task)
    existing_names, existing_urls = _existing_dedup_keys(database_session, task)
    candidates: list[CompetitorCandidate] = []

    for query in _build_queries(task):
        for result in search_provider.search(query):
            name = _normalize_name(result.title)
            url = _normalize_url(result.url)
            if (
                not name
                or not url
                or name.casefold() in existing_names
                or url in existing_urls
            ):
                continue

            candidate = CompetitorCandidate(
                user_id=task.user_id,
                space_id=task.space_id,
                task_id=task.id,
                name=name,
                description=result.summary.strip() or None,
                source_type="web",
            )
            database_session.add(candidate)
            database_session.flush()
            database_session.add(
                TaskEvidence(
                    user_id=task.user_id,
                    space_id=task.space_id,
                    task_id=task.id,
                    candidate_id=candidate.id,
                    source_type="web",
                    source_title=name,
                    source_url=url,
                    quote=result.summary.strip() or None,
                    retrieved_at=datetime.now(UTC),
                )
            )
            candidates.append(candidate)
            existing_names.add(name.casefold())
            existing_urls.add(url)

    database_session.commit()
    for candidate in candidates:
        database_session.refresh(candidate)
    return candidates


def _build_queries(task: AnalysisTask) -> list[str]:
    primary_query = " ".join(
        value.strip()
        for value in (task.industry, task.product_direction, *task.keywords)
        if value and value.strip()
    )
    return _unique_non_empty([primary_query, *task.known_competitors])


def _existing_dedup_keys(
    database_session: Session, task: AnalysisTask
) -> tuple[set[str], set[str]]:
    candidates = database_session.scalars(
        select(CompetitorCandidate).where(CompetitorCandidate.task_id == task.id)
    )
    names = {_normalize_name(candidate.name).casefold() for candidate in candidates}
    urls = set(
        database_session.scalars(
            select(TaskEvidence.source_url).where(
                TaskEvidence.task_id == task.id,
                TaskEvidence.source_type == "web",
                TaskEvidence.source_url.is_not(None),
            )
        )
    )
    return names, {_normalize_url(url) for url in urls if url}


def _normalize_name(value: str) -> str:
    return " ".join(value.split())


def _normalize_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    if not parsed.scheme or not parsed.netloc:
        return ""
    query = urlencode(
        [
            (key, item)
            for key, item in parse_qsl(parsed.query, keep_blank_values=True)
            if not key.lower().startswith("utm_")
        ]
    )
    path = parsed.path.rstrip("/") or ""
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path, query, ""))


def _unique_non_empty(values: Iterable[str]) -> list[str]:
    queries: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = " ".join(value.split())
        if normalized and normalized.casefold() not in seen:
            queries.append(normalized)
            seen.add(normalized.casefold())
    return queries


def _validate_task_owner(user: User, task: AnalysisTask) -> None:
    if task.user_id != user.id:
        raise ValueError("Analysis task does not belong to the current user")
