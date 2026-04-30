from fastapi import APIRouter, Depends

from app.schemas import AnalysisRequest
from app.services.analysis_service import run_analysis
from app.services.security import current_user
from app.services.session_service import save_session

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/run")
def run(payload: AnalysisRequest, user=Depends(current_user)):
    result = run_analysis(payload.dataset_id, payload.question, payload.mode)
    if payload.save_session and result.get("charts"):
        first_chart = next((chart for chart in result["charts"] if chart.get("chart_json")), result["charts"][0])
        saved = save_session(
            user["id"],
            {
                "title": payload.title or result.get("summary", {}).get("title") or payload.question[:80],
                "dataset_metadata": result["profile"],
                "question": payload.question,
                "chart_type": first_chart.get("chart_type", "dashboard"),
                "chart_config": first_chart.get("chart_json") or "{}",
                "insight": "\n".join(result.get("summary", {}).get("key_insights", [])) or first_chart.get("explanation", ""),
            },
        )
        result["saved_session"] = saved
    return result
