from collections.abc import Sequence
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel

from app.core.errors import evidence_quality_failed
from app.models import TaskEvidence


class EvidenceQualitySummary(BaseModel):
    status: Literal["passed"] = "passed"
    evidence_count: int
    web_evidence_count: int
    private_knowledge_evidence_count: int


def validate_evidence_quality(
    evidence: Sequence[TaskEvidence],
) -> EvidenceQualitySummary:
    traceable_evidence = [
        item for item in evidence if item.source_type in {"web", "private_knowledge"}
    ]
    if not traceable_evidence:
        raise evidence_quality_failed("没有可追溯证据")

    web_evidence_count = 0
    private_knowledge_evidence_count = 0
    for item in traceable_evidence:
        if not item.source_title.strip():
            raise evidence_quality_failed("证据缺少来源标题")
        if item.source_type == "web":
            if not _is_safe_external_url(item.source_url):
                raise evidence_quality_failed("网页证据缺少有效来源链接")
            web_evidence_count += 1
        else:
            if not all((item.document_id, item.chunk_id, item.knowledge_base_id)):
                raise evidence_quality_failed("私有知识库证据缺少文档关联")
            private_knowledge_evidence_count += 1

    return EvidenceQualitySummary(
        evidence_count=len(traceable_evidence),
        web_evidence_count=web_evidence_count,
        private_knowledge_evidence_count=private_knowledge_evidence_count,
    )


def _is_safe_external_url(url: str | None) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme.lower() in {"http", "https"} and bool(parsed.hostname)
    except ValueError:
        return False
