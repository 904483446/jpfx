from collections.abc import Generator
from uuid import uuid4

import pytest
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import app
from app.models import AnalysisTask, CompetitorCandidate, TaskEvidence, User
from app.schemas.auth import RegisterRequest
from app.services.auth_service import register_user
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

TEST_SECRET = "test-secret-with-at-least-32-bytes"


@pytest.fixture
def client(
    database_session: Session, monkeypatch: pytest.MonkeyPatch
) -> Generator[TestClient, None, None]:
    def override_database_session() -> Generator[Session, None, None]:
        yield database_session

    monkeypatch.setattr(settings, "jwt_secret", TEST_SECRET)
    app.dependency_overrides[get_db_session] = override_database_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def authenticate(client: TestClient, database_session: Session, email: str) -> User:
    user = register_user(
        database_session,
        RegisterRequest(
            email=email, password="valid-password", display_name="Analysis User"
        ),
    )
    client.cookies.set(settings.auth_cookie_name, create_access_token(user.id))
    return user


def create_space(client: TestClient) -> dict:
    response = client.post("/api/v1/spaces", json={"name": "Analysis Space"})
    assert response.status_code == 201
    return response.json()


def create_task(client: TestClient, space_id: str) -> dict:
    response = client.post(
        f"/api/v1/spaces/{space_id}/analysis-tasks",
        json={
            "title": "Writing assistant landscape",
            "industry": "AI",
            "product_direction": "Writing assistant",
            "keywords": ["collaboration"],
            "known_competitors": [],
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_task_accepts_zero_to_three_known_competitors_and_is_space_scoped(
    client: TestClient, database_session: Session
):
    authenticate(client, database_session, "task-owner@example.com")
    space = create_space(client)

    task = create_task(client, space["id"])

    assert task["space_id"] == space["id"]
    assert task["status"] == "draft"
    assert task["known_competitors"] == []
    assert client.get(f"/api/v1/analysis-tasks/{task['id']}").json()["id"] == task["id"]
    too_many = client.post(
        f"/api/v1/spaces/{space['id']}/analysis-tasks",
        json={
            "title": "Too many",
            "industry": "AI",
            "product_direction": "Writing",
            "known_competitors": ["A", "B", "C", "D"],
        },
    )
    assert too_many.status_code == 422

    other_user = authenticate(client, database_session, "task-other@example.com")
    assert other_user.id
    assert client.get(f"/api/v1/analysis-tasks/{task['id']}").status_code == 404


def test_manual_selection_requires_one_to_three_candidates_owned_by_task(
    client: TestClient, database_session: Session
):
    user = authenticate(client, database_session, "selection-owner@example.com")
    space = create_space(client)
    task_payload = create_task(client, space["id"])
    task = database_session.get(AnalysisTask, task_payload["id"])
    assert task is not None
    candidate = CompetitorCandidate(
        user_id=user.id,
        space_id=task.space_id,
        task_id=task.id,
        name="Candidate A",
        source_type="manual",
    )
    database_session.add(candidate)
    database_session.commit()

    selected = client.put(
        f"/api/v1/analysis-tasks/{task.id}/competitors",
        json={"candidate_ids": [str(candidate.id)]},
    )

    assert selected.status_code == 200
    assert selected.json()["final_competitors"] == ["Candidate A"]
    assert selected.json()["candidates"][0]["is_selected"] is True
    assert (
        client.put(
            f"/api/v1/analysis-tasks/{task.id}/competitors",
            json={"candidate_ids": []},
        ).status_code
        == 422
    )
    assert (
        client.put(
            f"/api/v1/analysis-tasks/{task.id}/competitors",
            json={"candidate_ids": [str(uuid4()) for _ in range(4)]},
        ).status_code
        == 422
    )


def test_auto_selects_at_most_three_candidates_with_web_evidence_and_retry_is_guarded(
    client: TestClient, database_session: Session, monkeypatch: pytest.MonkeyPatch
):
    from app.api.v1 import analysis_tasks

    user = authenticate(client, database_session, "auto-owner@example.com")
    space = create_space(client)
    task_payload = create_task(client, space["id"])
    task = database_session.get(AnalysisTask, task_payload["id"])
    assert task is not None
    evidenced_candidates = []
    for index in range(4):
        candidate = CompetitorCandidate(
            user_id=user.id,
            space_id=task.space_id,
            task_id=task.id,
            name=f"Web Candidate {index}",
            source_type="web",
        )
        database_session.add(candidate)
        database_session.flush()
        database_session.add(
            TaskEvidence(
                user_id=user.id,
                space_id=task.space_id,
                task_id=task.id,
                candidate_id=candidate.id,
                source_type="web",
                source_title=candidate.name,
                source_url=f"https://example.com/{index}",
            )
        )
        evidenced_candidates.append(candidate)
    no_evidence = CompetitorCandidate(
        user_id=user.id,
        space_id=task.space_id,
        task_id=task.id,
        name="No Evidence",
        source_type="manual",
    )
    database_session.add(no_evidence)
    database_session.commit()

    auto_selected = client.post(
        f"/api/v1/analysis-tasks/{task.id}/competitors/auto-select"
    )

    assert auto_selected.status_code == 200
    final_competitors = auto_selected.json()["final_competitors"]
    assert len(final_competitors) == 3
    assert set(final_competitors).issubset(
        {candidate.name for candidate in evidenced_candidates}
    )
    assert "No Evidence" not in final_competitors

    task.status = "failed"
    database_session.commit()
    monkeypatch.setattr(analysis_tasks, "run_analysis_task", lambda task_id: None)
    retried = client.post(f"/api/v1/analysis-tasks/{task.id}/retry")
    assert retried.status_code == 200
    assert retried.json()["status"] == "queued"
    assert client.post(f"/api/v1/analysis-tasks/{task.id}/retry").status_code == 409


@pytest.mark.parametrize("task_status", ["queued", "running", "completed", "failed"])
def test_non_draft_task_cannot_mutate_candidates(
    client: TestClient, database_session: Session, task_status: str
):
    user = authenticate(client, database_session, f"locked-{task_status}@example.com")
    space = create_space(client)
    task_payload = create_task(client, space["id"])
    task = database_session.get(AnalysisTask, task_payload["id"])
    assert task is not None
    candidate = CompetitorCandidate(
        user_id=user.id,
        space_id=task.space_id,
        task_id=task.id,
        name="Locked candidate",
        source_type="manual",
    )
    database_session.add(candidate)
    task.status = task_status
    database_session.commit()

    responses = [
        client.post(f"/api/v1/analysis-tasks/{task.id}/candidates/discover"),
        client.put(
            f"/api/v1/analysis-tasks/{task.id}/competitors",
            json={"candidate_ids": [str(candidate.id)]},
        ),
        client.post(f"/api/v1/analysis-tasks/{task.id}/competitors/auto-select"),
    ]

    assert [response.status_code for response in responses] == [409, 409, 409]
    database_session.refresh(task)
    database_session.refresh(candidate)
    assert task.final_competitors == []
    assert candidate.is_selected is False


def test_run_queues_task_and_schedules_background_work_by_task_id(
    client: TestClient, database_session: Session, monkeypatch: pytest.MonkeyPatch
):
    from app.api.v1 import analysis_tasks

    user = authenticate(client, database_session, "run-owner@example.com")
    space = create_space(client)
    task_payload = create_task(client, space["id"])
    task = database_session.get(AnalysisTask, task_payload["id"])
    assert task is not None
    candidate = CompetitorCandidate(
        user_id=user.id,
        space_id=task.space_id,
        task_id=task.id,
        name="Runnable candidate",
        source_type="manual",
        is_selected=True,
        sort_order=0,
    )
    database_session.add(candidate)
    task.final_competitors = [candidate.name]
    database_session.commit()
    scheduled_task_ids = []
    monkeypatch.setattr(
        analysis_tasks,
        "run_analysis_task",
        lambda task_id: scheduled_task_ids.append(task_id),
    )

    response = client.post(f"/api/v1/analysis-tasks/{task.id}/run")

    assert response.status_code == 202
    assert response.json()["status"] == "queued"
    assert scheduled_task_ids == [task.id]


def test_retry_queues_failed_task_and_schedules_background_work_by_task_id(
    client: TestClient, database_session: Session, monkeypatch: pytest.MonkeyPatch
):
    from app.api.v1 import analysis_tasks

    authenticate(client, database_session, "retry-owner@example.com")
    space = create_space(client)
    task_payload = create_task(client, space["id"])
    task = database_session.get(AnalysisTask, task_payload["id"])
    assert task is not None
    task.status = "failed"
    database_session.commit()
    scheduled_task_ids = []
    monkeypatch.setattr(
        analysis_tasks,
        "run_analysis_task",
        lambda task_id: scheduled_task_ids.append(task_id),
    )

    response = client.post(f"/api/v1/analysis-tasks/{task.id}/retry")

    assert response.status_code == 200
    assert response.json()["status"] == "queued"
    assert scheduled_task_ids == [task.id]
