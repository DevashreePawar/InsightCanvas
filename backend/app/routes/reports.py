from fastapi import APIRouter, Depends, Response

from app.schemas import ExportReportRequest
from app.services.report_service import build_html_report, build_pdf_report
from app.services.security import current_user
from app.services.session_service import get_session

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/export")
def export_report(payload: ExportReportRequest, user=Depends(current_user)):
    session = get_session(user["id"], payload.session_id)
    if payload.format == "pdf":
        return Response(
            build_pdf_report(session),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{session["title"]}.pdf"'},
        )
    return Response(
        build_html_report(session),
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{session["title"]}.html"'},
    )
