from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import AppError
from app.db.session import get_db_session
from app.models import CompetitorReport, TaskEvidence, User
from app.schemas.report import ReportEvidenceResponse, ReportResponse
from app.services.report_export_service import build_docx, build_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


def _owned_report(session: Session, user: User, report_id: UUID) -> CompetitorReport:
    report = session.scalar(
        select(CompetitorReport).where(
            CompetitorReport.id == report_id, CompetitorReport.user_id == user.id
        )
    )
    if report is None:
        raise AppError(status_code=404, code="REPORT_NOT_FOUND", message="报告不存在")
    return report


def _evidence(
    session: Session, user: User, report: CompetitorReport
) -> list[TaskEvidence]:
    return list(
        session.scalars(
            select(TaskEvidence)
            .where(
                TaskEvidence.task_id == report.task_id,
                TaskEvidence.user_id == user.id,
                TaskEvidence.space_id == report.space_id,
            )
            .order_by(TaskEvidence.created_at)
        )
    )


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> ReportResponse:
    return ReportResponse.model_validate(
        _owned_report(database_session, current_user, report_id)
    )


@router.get("/{report_id}/evidence", response_model=list[ReportEvidenceResponse])
def get_evidence(
    report_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> list[ReportEvidenceResponse]:
    report = _owned_report(database_session, current_user, report_id)
    return [
        ReportEvidenceResponse.model_validate(item)
        for item in _evidence(database_session, current_user, report)
    ]


@router.get("/{report_id}/export/{export_format}")
def export_report(
    report_id: UUID,
    export_format: Literal["pdf", "docx"],
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> StreamingResponse:
    report = _owned_report(database_session, current_user, report_id)
    content = (
        build_pdf(report, _evidence(database_session, current_user, report))
        if export_format == "pdf"
        else build_docx(report, _evidence(database_session, current_user, report))
    )
    media_type = (
        "application/pdf"
        if export_format == "pdf"
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    return StreamingResponse(
        iter([content]),
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="competitor-report-{report.id}.{export_format}"'
        },
    )
