from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.core.errors import AppError
from app.services.evidence_quality import validate_evidence_quality


def _evidence(source_type: str, **overrides):
    values = {
        "source_type": source_type,
        "source_title": "Traceable source",
        "source_url": None,
        "document_id": None,
        "chunk_id": None,
        "knowledge_base_id": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_validate_evidence_quality_counts_valid_web_and_private_evidence():
    summary = validate_evidence_quality(
        [
            _evidence("web", source_url="https://example.com/source"),
            _evidence(
                "private_knowledge",
                document_id=uuid4(),
                chunk_id=uuid4(),
                knowledge_base_id=uuid4(),
            ),
        ]
    )

    assert summary.model_dump() == {
        "status": "passed",
        "evidence_count": 2,
        "web_evidence_count": 1,
        "private_knowledge_evidence_count": 1,
    }


@pytest.mark.parametrize(
    "source_url", [None, "javascript:alert(1)", "file:///tmp/source", "https://@"]
)
def test_validate_evidence_quality_rejects_untraceable_web_evidence(source_url):
    with pytest.raises(AppError, match="网页证据缺少有效来源链接"):
        validate_evidence_quality([_evidence("web", source_url=source_url)])


def test_validate_evidence_quality_rejects_private_evidence_without_all_links():
    with pytest.raises(AppError, match="私有知识库证据缺少文档关联"):
        validate_evidence_quality([_evidence("private_knowledge", document_id=uuid4())])


def test_validate_evidence_quality_rejects_model_inference_as_traceable_evidence():
    with pytest.raises(AppError, match="没有可追溯证据"):
        validate_evidence_quality([_evidence("model_inference")])
