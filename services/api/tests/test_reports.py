from collections.abc import Generator
from datetime import UTC, datetime
from io import BytesIO

import pytest
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db_session
from app.main import app
from app.models import AnalysisTask, CompetitorReport, Space, TaskEvidence, User
from app.schemas.auth import RegisterRequest
from app.services.auth_service import register_user
from docx import Document
from fastapi.testclient import TestClient
from pypdf import PdfReader
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


def _authenticate(client: TestClient, database_session: Session, email: str) -> User:
    user = register_user(
        database_session,
        RegisterRequest(
            email=email,
            password="valid-password",
            display_name="Report User",
        ),
    )
    client.cookies.set(settings.auth_cookie_name, create_access_token(user.id))
    return user


def _create_report(database_session: Session, user: User) -> CompetitorReport:
    space = Space(user_id=user.id, name="Report space")
    database_session.add(space)
    database_session.flush()
    task = AnalysisTask(
        user_id=user.id,
        space_id=space.id,
        title="AI knowledge base competitor report",
        industry="AI",
        product_direction="Knowledge base",
        keywords=[],
        known_competitors=[],
        final_competitors=["Competitor A"],
        discovery_mode="manual",
        status="completed",
    )
    database_session.add(task)
    database_session.flush()
    report = CompetitorReport(
        user_id=user.id,
        space_id=space.id,
        task_id=task.id,
        title="AI knowledge base competitor report",
        structured_json={
            "competitors": [
                {
                    "name": "Competitor A",
                    "positioning": "Knowledge base assistant",
                    "core_features": ["Retrieval", "Citations"],
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
        },
    )
    database_session.add(report)
    database_session.flush()
    for source_type, title, url in [
        ("web", "Web source", "https://example.com/web"),
        ("private_knowledge", "Private brief", None),
        ("model_inference", "Inference", None),
    ]:
        database_session.add(
            TaskEvidence(
                user_id=user.id,
                space_id=space.id,
                task_id=task.id,
                source_type=source_type,
                source_title=title,
                source_url=url,
                quote="Evidence quote",
                retrieved_at=datetime.now(UTC),
            )
        )
    database_session.commit()
    return report


def test_report_detail_returns_json_source_of_truth_and_evidence(
    client, database_session
):
    user = _authenticate(client, database_session, "reports-owner@example.com")
    report = _create_report(database_session, user)

    response = client.get(f"/api/v1/reports/{report.id}")

    assert response.status_code == 200
    assert response.json()["structured_json"] == report.structured_json
    evidence = client.get(f"/api/v1/reports/{report.id}/evidence")
    assert evidence.status_code == 200
    assert {item["source_type"] for item in evidence.json()} == {
        "web",
        "private_knowledge",
        "model_inference",
    }


@pytest.mark.parametrize(
    ("export_format", "content_type", "extension"),
    [
        ("pdf", "application/pdf", ".pdf"),
        (
            "docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".docx",
        ),
    ],
)
def test_report_exports_are_attachments_with_safe_filename(
    client, database_session, export_format, content_type, extension
):
    user = _authenticate(
        client, database_session, f"reports-{export_format}@example.com"
    )
    report = _create_report(database_session, user)

    response = client.get(f"/api/v1/reports/{report.id}/export/{export_format}")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(content_type)
    disposition = response.headers["content-disposition"]
    assert "attachment" in disposition
    assert "\r" not in disposition and "\n" not in disposition
    assert extension in disposition
    assert response.content
    if export_format == "pdf":
        text = "".join(
            page.extract_text() or ""
            for page in PdfReader(BytesIO(response.content)).pages
        )
        assert report.title in text
    else:
        document = Document(BytesIO(response.content))
        assert document.paragraphs[0].text == report.title


def test_other_user_cannot_read_or_download_report(client, database_session):
    owner = _authenticate(client, database_session, "reports-private@example.com")
    report = _create_report(database_session, owner)
    _authenticate(client, database_session, "reports-other@example.com")

    for endpoint in (
        f"/api/v1/reports/{report.id}",
        f"/api/v1/reports/{report.id}/evidence",
        f"/api/v1/reports/{report.id}/export/pdf",
        f"/api/v1/reports/{report.id}/export/docx",
    ):
        response = client.get(endpoint)
        assert response.status_code == 404


def test_pdf_export_escapes_untrusted_report_and_evidence_text(
    client, database_session
):
    user = _authenticate(client, database_session, "reports-xml@example.com")
    report = _create_report(database_session, user)
    report.title = "<unclosed report>"
    report.structured_json["executive_summary"] = "<b>summary</b> & details"
    report.structured_json["competitors"][0]["name"] = "<b>Competitor</b>"
    report.structured_json["competitors"][0]["recommendations"] = ["<unclosed"]
    evidence = (
        database_session.query(TaskEvidence).filter_by(task_id=report.task_id).first()
    )
    assert evidence is not None
    evidence.source_title = "<b>web evidence</b>"
    evidence.source_url = "https://example.com/?q=<unclosed"
    database_session.commit()

    response = client.get(f"/api/v1/reports/{report.id}/export/pdf")

    assert response.status_code == 200
    text = "".join(
        page.extract_text() or "" for page in PdfReader(BytesIO(response.content)).pages
    )
    assert "<unclosed report>" in text
    assert "<b>Competitor</b>" in text
    assert "<unclosed" in text


@pytest.mark.parametrize(
    "unsafe_url",
    [
        "javascript:alert(1)",
        "file:///etc/passwd",
        "data:text/html,unsafe",
        "http://:80",
        "https://@",
    ],
)
def test_pdf_export_does_not_create_links_for_unsafe_evidence_urls(
    client, database_session, unsafe_url
):
    user = _authenticate(client, database_session, f"reports-url-{len(unsafe_url)}@example.com")
    report = _create_report(database_session, user)
    evidence = database_session.query(TaskEvidence).filter_by(task_id=report.task_id).first()
    assert evidence is not None
    evidence.source_url = unsafe_url
    database_session.commit()

    response = client.get(f"/api/v1/reports/{report.id}/export/pdf")

    assert response.status_code == 200
    reader = PdfReader(BytesIO(response.content))
    annotations = [annotation.get_object() for page in reader.pages for annotation in page.get("/Annots", [])]
    assert all(annotation.get("/A", {}).get("/URI") != unsafe_url for annotation in annotations)
