from __future__ import annotations

from dataclasses import dataclass

from app.services.chart_service import generate_chart
from app.services.csv_service import get_dataset, get_dataset_metadata
from app.services.data_quality_service import build_data_quality_report
from app.services.profile_service import profile_dataset
from app.services.quality_service import alternative_questions
from app.services.rag_service import retrieve_dataset_context
from app.services.statistics_service import build_statistical_summary


@dataclass
class ChartPlan:
    title: str
    question: str
    intent: str
    chart_type: str
    x_axis: str | None = None
    y_axis: str | None = None
    aggregation: str = "none"
    sort: str | None = None
    limit: int | None = None
    anomaly_detection: bool = False


def _fields(profile: dict) -> tuple[list[str], list[str], list[str], list[str]]:
    sensitive = set(profile.get("sensitive_columns", {}).keys())
    identifiers = set(profile.get("possible_id_columns", []))
    excluded = sensitive | identifiers
    logical_types = profile.get("logical_types", {})
    numeric = [
        column
        for column, dtype in profile.get("data_types", {}).items()
        if ("int" in dtype or "float" in dtype)
        and column not in excluded
        and logical_types.get(column) not in {"identifier", "sensitive_identifier", "categorical_numeric"}
    ]
    categorical = [
        column
        for column in profile.get("column_names", [])
        if column not in excluded and logical_types.get(column) in {"categorical", "categorical_numeric", "multi_value_categorical"}
    ]
    dates = [column for column in profile.get("date_columns", []) if column not in excluded]
    multi_value = [column for column in profile.get("multi_value_columns", []) if column not in excluded]
    return numeric, categorical, dates, multi_value


def _default_metric(numeric: list[str], profile: dict) -> str | None:
    summaries = profile.get("numeric_summary_statistics", {})
    ranked = sorted(
        numeric,
        key=lambda column: (
            profile.get("missing_value_percentage", {}).get(column, 0) or 0,
            -abs((summaries.get(column, {}) or {}).get("std", 0) or 0),
        ),
    )
    return ranked[0] if ranked else None


def _result_to_card(result: dict, plan: ChartPlan) -> dict:
    return {
        "id": plan.title.lower().replace(" ", "-"),
        "title": plan.title,
        "question": plan.question,
        "chart_type": result.get("chart_type"),
        "chart_json": result.get("chart_json"),
        "explanation": result.get("insight"),
        "warnings": result.get("data_quality_warnings", []),
        "reasoning": result.get("reasoning", []),
        "recommendation": result.get("recommendation", {}),
    }


def _plan_to_interpretation(plan: ChartPlan) -> dict:
    return {
        "intent": plan.intent,
        "x_axis": plan.x_axis,
        "y_axis": plan.y_axis,
        "aggregation": plan.aggregation,
        "chart_type": plan.chart_type,
        "filters": [],
        "derived_feature": None,
        "sort": plan.sort,
        "limit": plan.limit,
        "anomaly_detection": plan.anomaly_detection,
        "preprocessing_steps": ["Clean missing-like values", "Use non-sensitive, non-identifier columns"],
        "reasoning_steps": [
            f"Planned analysis: {plan.intent}",
            f"Selected {plan.chart_type} because it matches the available column types",
            f"Columns: x={plan.x_axis}, y={plan.y_axis}",
        ],
        "explanation": "Planned automatically from the uploaded dataset profile.",
    }


def _dashboard_plans(profile: dict, question: str) -> list[ChartPlan]:
    numeric, categorical, dates, multi_value = _fields(profile)
    metric = _default_metric(numeric, profile)
    group = (multi_value or categorical or [None])[0]
    plans: list[ChartPlan] = []

    if metric:
        plans.append(
            ChartPlan(
                title=f"Distribution of {metric}",
                question=f"Show the distribution of {metric}",
                intent="distribution",
                chart_type="histogram",
                x_axis=metric,
            )
        )
    if group:
        plans.append(
            ChartPlan(
                title=f"Records by {group}",
                question=f"Show the count of records by {group}",
                intent="count",
                chart_type="bar",
                x_axis=group,
                aggregation="count",
                sort="desc",
                limit=12,
            )
        )
    if group and metric:
        plans.append(
            ChartPlan(
                title=f"Average {metric} by {group}",
                question=f"Compare average {metric} by {group}",
                intent="comparison",
                chart_type="bar",
                x_axis=group,
                y_axis=metric,
                aggregation="mean",
                sort="desc",
                limit=12,
            )
        )
    if len(numeric) >= 2:
        plans.append(
            ChartPlan(
                title="Numeric relationships",
                question=f"What factors seem related to {metric or numeric[0]}?",
                intent="correlation",
                chart_type="heatmap",
                x_axis=metric or numeric[0],
            )
        )
    if dates and metric:
        plans.append(
            ChartPlan(
                title=f"{metric} over time",
                question=f"Show {metric} over {dates[0]}",
                intent="time_series",
                chart_type="line",
                x_axis=dates[0],
                y_axis=metric,
                aggregation="mean",
            )
        )
    if metric:
        plans.append(
            ChartPlan(
                title=f"Outliers in {metric}",
                question=f"Find unusual values in {metric}",
                intent="anomaly_detection",
                chart_type="box",
                x_axis=group,
                y_axis=metric,
                anomaly_detection=True,
            )
        )

    return plans[:6]


def _quick_plans(profile: dict, question: str) -> list[ChartPlan | None]:
    numeric, categorical, _dates, multi_value = _fields(profile)
    metric = _default_metric(numeric, profile)
    group = (multi_value or categorical or [None])[0]
    plans: list[ChartPlan | None] = [None]
    if group and metric:
        plans.append(
            ChartPlan(
                title=f"Related comparison: {metric} by {group}",
                question=f"Compare average {metric} by {group}",
                intent="comparison",
                chart_type="bar",
                x_axis=group,
                y_axis=metric,
                aggregation="mean",
                sort="desc",
                limit=10,
            )
        )
    elif len(numeric) >= 2:
        plans.append(
            ChartPlan(
                title="Related numeric relationship",
                question=f"Find the relationship between {numeric[0]} and {numeric[1]}",
                intent="correlation",
                chart_type="scatter",
                x_axis=numeric[0],
                y_axis=numeric[1],
            )
        )
    return plans[:2]


def _follow_up_questions(profile: dict) -> list[str]:
    numeric, categorical, _dates, multi_value = _fields(profile)
    group = (multi_value or categorical or [None])[0]
    questions = []
    if numeric and group:
        questions.append(f"Do {numeric[0]} values vary by {group}?")
    if numeric:
        questions.append(f"Which records look unusual for {numeric[0]}?")
    if len(numeric) >= 2:
        questions.append(f"Is {numeric[0]} related to {numeric[1]}?")
    questions.extend(alternative_questions(profile))
    return list(dict.fromkeys(question for question in questions if question))[:3]


def _summary_from_cards(cards: list[dict], profile: dict, mode: str) -> dict:
    explanations = [card.get("explanation") for card in cards if card.get("explanation")]
    warnings = []
    for card in cards:
        warnings.extend(card.get("warnings", []))
    if not cards:
        key_insights = ["There was not enough suitable data to create a reliable chart."]
    else:
        key_insights = explanations[:3]
    return {
        "title": "Mini analysis report" if mode == "dashboard" else "Quick insight",
        "key_insights": key_insights,
        "patterns": explanations[3:5],
        "anomalies": [warning for warning in dict.fromkeys(warnings)][:3],
        "dataset_notes": profile.get("data_quality_warnings", []),
    }


def run_analysis(dataset_id: str, question: str, mode: str = "quick") -> dict:
    mode = mode if mode in {"quick", "dashboard"} else "quick"
    df = get_dataset(dataset_id)
    metadata = get_dataset_metadata(dataset_id)
    profile = profile_dataset(df, metadata)
    quality_report = build_data_quality_report(df, profile)
    statistical_summary = build_statistical_summary(df, profile)
    context = retrieve_dataset_context(dataset_id, question)

    plans = _dashboard_plans(profile, question) if mode == "dashboard" else _quick_plans(profile, question)
    cards = []
    for plan in plans:
        if plan is None:
            result = generate_chart(df, question, metadata, context)
            title = result.get("chart_type", "Chart").replace("_", " ").title()
            cards.append(_result_to_card(result, ChartPlan(title=title, question=question, intent=result.get("recommendation", {}).get("intent", "analysis"), chart_type=result.get("chart_type", "bar"))))
            continue
        result = generate_chart(df, plan.question, metadata, context, _plan_to_interpretation(plan))
        if result.get("chart_json") or result.get("chart_type") == "not_applicable":
            cards.append(_result_to_card(result, plan))

    return {
        "mode": mode,
        "profile": profile,
        "metadata": metadata,
        "question": question,
        "charts": cards,
        "summary": _summary_from_cards(cards, profile, mode),
        "quality_report": quality_report,
        "statistical_summary": statistical_summary,
        "follow_up_questions": _follow_up_questions(profile),
        "retrieved_context": context,
    }
