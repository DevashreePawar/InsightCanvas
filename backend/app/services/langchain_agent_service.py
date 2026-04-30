from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, Field

from app.config import OPENAI_API_KEY, OPENAI_MODEL, USE_LANGCHAIN

logger = logging.getLogger(__name__)


class LangChainFilter(BaseModel):
    column: str
    operator: str = Field(description="One of eq, neq, gt, gte, lt, lte, contains")
    value: str


class LangChainDerivedFeature(BaseModel):
    name: str
    numerator: str
    denominator: str | None = None
    operation: str = Field(description="One of ratio, difference, sum, product, bin")


class LangChainAgentPlan(BaseModel):
    intent: str
    x_axis: str | None = None
    y_axis: str | None = None
    aggregation: str
    chart_type: str
    filters: list[LangChainFilter] = Field(default_factory=list)
    derived_feature: LangChainDerivedFeature | None = None
    sort: str | None = None
    limit: int | None = Field(default=None, ge=1, le=50)
    anomaly_detection: bool = False
    preprocessing_steps: list[str] = Field(default_factory=list)
    reasoning_steps: list[str] = Field(default_factory=list)
    explanation: str


class LangChainQuestionSuggestions(BaseModel):
    questions: list[str] = Field(min_length=3, max_length=6)


def langchain_available() -> bool:
    return bool(OPENAI_API_KEY and USE_LANGCHAIN)


def _llm():
    # Imported lazily so the backend can still run without LangChain installed.
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY, temperature=0)


def _compact_profile(profile: dict) -> dict:
    """Keep the LLM context focused on schema and EDA signals, not raw data."""
    return {
        "dataset_metadata": profile.get("dataset_metadata", {}),
        "row_count": profile.get("row_count"),
        "column_names": profile.get("column_names", []),
        "data_types": profile.get("data_types", {}),
        "logical_types": profile.get("logical_types", {}),
        "semantic_schema": profile.get("semantic_schema", {}),
        "missing_value_percentage": profile.get("missing_value_percentage", {}),
        "unique_counts": profile.get("unique_counts", {}),
        "possible_id_columns": profile.get("possible_id_columns", []),
        "sensitive_columns": profile.get("sensitive_columns", {}),
        "multi_value_columns": profile.get("multi_value_columns", []),
        "date_columns": profile.get("date_columns", []),
        "numeric_summary_statistics": profile.get("numeric_summary_statistics", {}),
        "categorical_summaries": profile.get("categorical_summaries", {}),
        "data_quality_warnings": profile.get("data_quality_warnings", []),
    }


def interpret_with_langchain(
    question: str,
    profile: dict,
    rag_context: list[dict] | None,
    valid_chart_types: set[str],
    valid_aggregations: set[str],
) -> dict[str, Any] | None:
    if not langchain_available():
        return None

    try:
        structured_llm = _llm().with_structured_output(LangChainAgentPlan)
        messages = [
            (
                "system",
                (
                    "You are the LangChain reasoning layer for InsightCanvas, an AI data analyst. "
                    "Return a structured visualization and analysis plan. Use only columns that exist "
                    "in the uploaded dataset profile. Never invent dataset-specific assumptions. "
                    "Avoid sensitive columns and likely identifier columns unless the plan is explaining "
                    "why they are not analytically useful. Choose chart types based on statistical suitability: "
                    "histogram for numeric distributions, bar for categorical counts/comparisons/rankings, "
                    "scatter for two numeric relationships, heatmap for broad numeric correlation scans, "
                    "line for time trends, box for outliers or numeric comparison across groups. "
                    "For feature engineering requests, create a derived_feature. For bins or buckets, use "
                    "derived_feature.operation='bin'. For rates based on 0/1 outcomes, use aggregation='mean'. "
                    "Include preprocessing_steps and reasoning_steps that explain the plan in plain English."
                ),
            ),
            (
                "human",
                json.dumps(
                    {
                        "question": question,
                        "dataset_profile": _compact_profile(profile),
                        "retrieved_context": rag_context or [],
                        "allowed_chart_types": sorted(valid_chart_types),
                        "allowed_aggregations": sorted(valid_aggregations),
                    },
                    ensure_ascii=False,
                ),
            ),
        ]
        plan = structured_llm.invoke(messages)
        payload = plan.model_dump()
        payload["explanation"] = f"LangChain planned this from the dataset profile and retrieved context. {payload['explanation']}"
        return payload
    except ImportError as exc:
        logger.warning("LangChain packages are not installed; falling back to existing planner: %s", exc)
    except Exception as exc:
        logger.warning("LangChain interpretation failed; falling back to existing planner: %s", exc)
    return None


def suggest_questions_with_langchain(profile: dict) -> list[str] | None:
    if not langchain_available():
        return None

    try:
        structured_llm = _llm().with_structured_output(LangChainQuestionSuggestions)
        messages = [
            (
                "system",
                (
                    "Generate practical natural-language analysis questions for a tabular dataset. "
                    "Questions should be useful for charts and EDA, concise, and understandable to "
                    "non-technical users. Use only columns that exist in the dataset profile."
                ),
            ),
            (
                "human",
                json.dumps({"dataset_profile": _compact_profile(profile), "desired_count": 4}, ensure_ascii=False),
            ),
        ]
        parsed = structured_llm.invoke(messages)
        questions = [question.strip() for question in parsed.questions if question.strip()]
        return questions[:4] or None
    except ImportError as exc:
        logger.warning("LangChain packages are not installed; using fallback questions: %s", exc)
    except Exception as exc:
        logger.warning("LangChain question suggestions failed; using fallback questions: %s", exc)
    return None
