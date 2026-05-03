from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class AuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    token: str
    user: Dict[str, Any]


class QuestionRequest(BaseModel):
    dataset_id: str
    question: str = Field(min_length=3, max_length=500)


class ChartRequest(QuestionRequest):
    save_session: bool = False
    title: Optional[str] = None


class AnalysisRequest(ChartRequest):
    mode: str = Field(default="quick", pattern="^(quick|dashboard)$")


class Interpretation(BaseModel):
    intent: str
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    aggregation: str = "none"
    chart_type: str
    filters: List[Dict[str, Any]] = Field(default_factory=list)
    reasoning_steps: List[str] = Field(default_factory=list)
    preprocessing_steps: List[str] = Field(default_factory=list)
    data_quality_warnings: List[str] = Field(default_factory=list)
    suggested_alternatives: List[str] = Field(default_factory=list)
    explanation: str


class SaveSessionRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    dataset_metadata: Dict[str, Any]
    question: str
    chart_type: str
    chart_config: Dict[str, Any]
    insight: str


class ExportReportRequest(BaseModel):
    session_id: str
    format: str = Field(pattern="^(html|pdf)$")


class AnalyticsEventRequest(BaseModel):
    visitor_id: str = Field(min_length=8, max_length=80)
    event_name: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9_]+$")
    page: Optional[str] = Field(default=None, max_length=120)
    metadata: Dict[str, Any] = Field(default_factory=dict)
