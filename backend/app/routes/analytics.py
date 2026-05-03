from fastapi import APIRouter, Query

from app.schemas import AnalyticsEventRequest
from app.services.analytics_service import analytics_summary, record_event

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/event")
def create_analytics_event(payload: AnalyticsEventRequest):
    return record_event(payload.visitor_id, payload.event_name, payload.page, payload.metadata)


@router.get("/summary")
def get_analytics_summary(days: int = Query(default=30, ge=1, le=365)):
    return analytics_summary(days)
