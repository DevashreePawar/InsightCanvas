import json
import logging
import re
from difflib import SequenceMatcher
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field

from app.config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)

AGGREGATION_KEYWORDS = {
    "count": ["count", "number of", "how many", "frequency", "volume"],
    "mean": ["average", "avg", "mean"],
    "sum": ["sum", "total"],
    "max": ["maximum", "max", "highest", "largest", "top"],
    "min": ["minimum", "min", "lowest", "smallest"],
    "median": ["median", "middle"],
}

VALID_CHART_TYPES = {"line", "bar", "scatter", "histogram", "pie", "box", "heatmap"}
VALID_AGGREGATIONS = {"none", "count", "sum", "mean", "median", "min", "max"}
COMPARATIVE_KEYWORDS = ["compare", "comparison", "comparative", "versus", "difference", "differences", "breakdown"]
RELATIONSHIP_KEYWORDS = ["relationship", "correlation", "correlate", "association", "associated", "impact", "influence"]
ANOMALY_KEYWORDS = ["anomaly", "anomalies", "outlier", "outliers", "unusual", "abnormal", "spike"]
FEATURE_ENGINEERING_KEYWORDS = ["feature", "derived", "engineer", "bucket", "binned", "bin"]


class AgentFilter(BaseModel):
    column: str
    operator: str = Field(description="One of eq, neq, gt, gte, lt, lte, contains")
    value: str


class DerivedFeature(BaseModel):
    name: str
    numerator: str
    denominator: str | None = None
    operation: str = Field(description="One of ratio, difference, sum, product, bin")


class AgentPlan(BaseModel):
    intent: str = Field(description="Short intent label, e.g. count, comparison, distribution, ranking, correlation, time_series, outlier_detection")
    x_axis: str | None = None
    y_axis: str | None = None
    aggregation: str = Field(description="One of none, count, sum, mean, median, min, max")
    chart_type: str = Field(description="One of line, bar, scatter, histogram, pie, box, heatmap")
    filters: list[AgentFilter] = Field(default_factory=list)
    derived_feature: DerivedFeature | None = None
    sort: str | None = Field(default=None, description="Optional sort direction: asc or desc")
    limit: int | None = Field(default=None, ge=1, le=50)
    anomaly_detection: bool = False
    preprocessing_steps: list[str] = Field(default_factory=list)
    reasoning_steps: list[str] = Field(default_factory=list)
    explanation: str


class SuggestedQuestions(BaseModel):
    questions: list[str] = Field(min_length=3, max_length=6)


def build_semantic_schema(profile: dict) -> dict[str, dict[str, Any]]:
    numeric, categorical, dates = _fields(profile)
    schema = {}
    for column in profile["column_names"]:
        normalized = _normalize(column)
        aliases = set(_column_aliases(column))
        roles = []
        semantic_info = profile.get("semantic_profile", {}).get(column, {})
        roles.extend(semantic_info.get("roles", []))
        aliases.update(semantic_info.get("aliases", []))
        if column in dates:
            roles.append("date")
        if column in numeric:
            roles.append("measure")
        if column in categorical:
            roles.append("dimension")
        if column in set(profile.get("possible_id_columns", [])):
            roles.append("identifier_candidate")
        if any(token in normalized for token in ["rank", "position", "place"]):
            roles.append("rank")
            aliases.update({"ranking", "rank", "position"})
        schema[column] = {
            "dtype": profile["data_types"].get(column),
            "roles": list(dict.fromkeys(roles)),
            "aliases": sorted(aliases),
            "logical_type": profile.get("logical_types", {}).get(column),
            "unique_count": profile.get("unique_counts", {}).get(column),
            "missing_pct": profile.get("missing_value_percentage", {}).get(column),
        }
    return schema


def _fields(profile: dict) -> tuple[list[str], list[str], list[str]]:
    logical_types = profile.get("logical_types", {})
    sensitive_columns = set(profile.get("sensitive_columns", {}).keys())
    numeric_all = [
        col
        for col, dtype in profile["data_types"].items()
        if ("int" in dtype or "float" in dtype) and logical_types.get(col) not in {"identifier", "sensitive_identifier"}
    ]
    identifier_columns = set(profile.get("possible_id_columns", [])) | {col for col in profile["column_names"] if _normalize(col).endswith("id")}
    excluded = identifier_columns | sensitive_columns
    numeric = [col for col in numeric_all if col not in excluded and logical_types.get(col) == "numeric"]
    numeric.extend([col for col in numeric_all if col not in numeric and col not in excluded and logical_types.get(col) != "categorical_numeric"])
    if not numeric:
        numeric = numeric_all
    dates = profile.get("date_columns", [])
    categorical = [
        col
        for col in profile["column_names"]
        if col not in numeric and col not in excluded and logical_types.get(col) in {"categorical", "categorical_numeric", "multi_value_categorical"}
    ]
    return numeric, categorical, dates


def _mentions_column(question: str, column: str) -> bool:
    normalized_question = _normalize(question)
    return any(
        re.search(rf"(^|\s){re.escape(alias)}s?($|\s)", normalized_question)
        for alias in _column_aliases(column)
    )


def _normalize(value: str) -> str:
    split_camel = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(value))
    return re.sub(r"[^a-z0-9]+", " ", split_camel.lower()).strip()


def _column_aliases(column: str) -> set[str]:
    normalized = _normalize(column)
    aliases = {normalized, normalized.replace(" ", "")}
    if normalized.endswith("s"):
        aliases.add(normalized[:-1])
    return aliases


def _resolve_column(candidate: str | None, columns: list[str]) -> str | None:
    if not candidate:
        return None
    normalized_candidate = _normalize(candidate)
    for column in columns:
        if candidate == column or normalized_candidate == _normalize(column):
            return column
    for column in columns:
        if normalized_candidate in _column_aliases(column):
            return column
    return None


def _resolve_semantic_column(term: str | None, profile: dict, required_role: str | None = None) -> str | None:
    if not term:
        return None
    normalized_term = _normalize(term)
    query_tokens = set(normalized_term.split())
    semantic_schema = profile.get("semantic_schema") or build_semantic_schema(profile)
    best_match = None
    best_score = 0
    for column, info in semantic_schema.items():
        aliases = set(info.get("aliases", [])) | {_normalize(column)}
        roles = set(info.get("roles", []))
        score = 0
        if normalized_term == _normalize(column):
            score += 5
        if normalized_term in aliases:
            score += 4
        if any(alias and (alias in normalized_term or normalized_term in alias) for alias in aliases):
            score += 2
        column_tokens = set(_normalize(column).split())
        overlap = query_tokens & column_tokens
        if overlap:
            score += min(4, len(overlap) * 2)
        best_fuzzy = max(
            [SequenceMatcher(None, token, column_token).ratio() for token in query_tokens for column_token in column_tokens] or [0]
        )
        if best_fuzzy >= 0.86:
            score += 2
        if required_role and required_role in roles:
            score += 2
        if score > best_score:
            best_match = column
            best_score = score
    return best_match if best_score >= 2 else None


def _apply_question_overrides(question: str, plan: dict[str, Any], profile: dict) -> dict[str, Any]:
    normalized = _normalize(question)
    numeric, categorical, _dates = _fields(profile)
    if any(keyword in normalized for keyword in ["bin", "bins", "bucket", "buckets", "low medium high"]):
        source = _mentioned_column(question, numeric) or _resolve_semantic_column(question, profile, "measure")
        metric = next((column for column in _mentioned_columns(question, numeric) if column != source), None)
        metric = metric or _resolve_semantic_column(question, profile, "measure")
        if source:
            engineered_name = f"{source}_bin"
            plan.update(
                {
                    "intent": "derived_feature",
                    "x_axis": engineered_name,
                    "y_axis": metric or next((column for column in numeric if column != source), None),
                    "aggregation": "mean" if metric or len(numeric) > 1 else "count",
                    "chart_type": "bar",
                    "derived_feature": {
                        "name": engineered_name,
                        "numerator": source,
                        "denominator": None,
                        "operation": "bin",
                    },
                    "sort": None,
                    "limit": None,
                }
            )
            plan["reasoning_steps"] = (plan.get("reasoning_steps") or []) + [
                f"Created low/medium/high bins from {source}",
                f"Compared {plan['y_axis'] or 'record count'} across the engineered bins",
            ]
    if plan.get("x_axis") is None and plan.get("aggregation") == "count" and categorical:
        plan["x_axis"] = categorical[0]
    return plan


def _validated_plan(plan: dict[str, Any], profile: dict, question: str = "") -> dict[str, Any]:
    columns = profile["column_names"]
    numeric, categorical, dates = _fields(profile)
    grouping_candidates = categorical + _low_cardinality_columns(profile, numeric)

    plan["x_axis"] = _resolve_column(plan.get("x_axis"), columns)
    plan["y_axis"] = _resolve_column(plan.get("y_axis"), columns)
    plan["aggregation"] = plan.get("aggregation") if plan.get("aggregation") in VALID_AGGREGATIONS else "none"
    plan["chart_type"] = plan.get("chart_type") if plan.get("chart_type") in VALID_CHART_TYPES else "bar"
    plan["sort"] = plan.get("sort") if plan.get("sort") in {"asc", "desc"} else None
    plan["limit"] = plan.get("limit") if isinstance(plan.get("limit"), int) and 1 <= plan.get("limit") <= 50 else None

    derived = plan.get("derived_feature")
    if derived:
        numerator = _resolve_column(derived.get("numerator"), columns)
        denominator = _resolve_column(derived.get("denominator"), columns)
        operation = derived.get("operation") if derived.get("operation") in {"ratio", "difference", "sum", "product", "bin"} else "ratio"
        if numerator and (operation == "bin" or operation != "ratio" or denominator):
            name = derived.get("name") or f"{numerator}_{operation}_{denominator}"
            plan["derived_feature"] = {"name": name, "numerator": numerator, "denominator": denominator, "operation": operation}
            if not plan["y_axis"]:
                plan["y_axis"] = name
        else:
            plan["derived_feature"] = None
    else:
        plan["derived_feature"] = None

    valid_filters = []
    for item in plan.get("filters", []):
        column = _resolve_column(item.get("column"), columns)
        operator = item.get("operator")
        if column and operator in {"eq", "neq", "gt", "gte", "lt", "lte", "contains"}:
            valid_filters.append({"column": column, "operator": operator, "value": str(item.get("value", ""))})
    plan["filters"] = valid_filters

    if plan["aggregation"] == "count" and not plan["x_axis"]:
        plan["x_axis"] = grouping_candidates[0] if grouping_candidates else columns[0]
    if plan["chart_type"] == "histogram" and plan["x_axis"] not in numeric:
        plan["x_axis"] = plan["y_axis"] if plan["y_axis"] in numeric else (numeric[0] if numeric else columns[0])
        plan["y_axis"] = None
    if plan["chart_type"] == "scatter":
        numeric_mentions = [column for column in [plan["x_axis"], plan["y_axis"]] if column in numeric]
        if len(numeric_mentions) < 2 and len(numeric) >= 2:
            plan["x_axis"], plan["y_axis"] = numeric[0], numeric[1]
    if plan["chart_type"] == "heatmap":
        plan["x_axis"] = plan["x_axis"] if plan["x_axis"] in numeric else None
        plan["y_axis"] = plan["y_axis"] if plan["y_axis"] in numeric else None
        plan["aggregation"] = "none"
    if (
        plan.get("intent") in {"comparison", "ranking", "grouped_aggregation"}
        and plan["chart_type"] == "bar"
        and plan["x_axis"] in grouping_candidates
        and plan["y_axis"] in numeric
        and plan["aggregation"] == "none"
    ):
        plan["aggregation"] = _default_comparison_aggregation(plan["y_axis"])
    if plan["chart_type"] == "line" and not plan["x_axis"] and dates:
        plan["x_axis"] = dates[0]
    if not plan["x_axis"] and plan["chart_type"] in {"bar", "line", "pie"} and plan["aggregation"] == "count":
        plan["x_axis"] = grouping_candidates[0] if grouping_candidates else columns[0]
    if plan.get("anomaly_detection"):
        plan["chart_type"] = "box"
        if plan["y_axis"] not in numeric:
            plan["y_axis"] = numeric[0] if numeric else None

    return _apply_question_overrides(question, plan, profile) if question else plan


def mock_suggest_questions(profile: dict) -> list[str]:
    numeric, categorical, dates = _fields(profile)
    grouping_candidates = categorical + _low_cardinality_columns(profile, numeric)
    questions = []

    if grouping_candidates:
        questions.append(f"Show the count of records by {grouping_candidates[0]}")
    if dates and numeric:
        questions.append(f"Show {numeric[0]} trends over {dates[0]}")
    if grouping_candidates and numeric:
        questions.append(f"Compare average {numeric[0]} by {grouping_candidates[0]}")
        questions.append(f"Give comparative insights for {numeric[0]} by {grouping_candidates[0]}")
    if len(numeric) >= 2:
        questions.append(f"Find the relationship between {numeric[0]} and {numeric[1]}")
        questions.append(f"What factors seem related to {numeric[0]}?")
    if numeric:
        questions.append(f"Show the distribution of {numeric[0]}")
    if len(grouping_candidates) > 1:
        questions.append(f"Compare counts by {grouping_candidates[1]}")

    fallback = [
        "What are the most important patterns in this dataset?",
        "Which category has the highest count?",
        "Show the distribution of the main numeric column",
    ]
    return list(dict.fromkeys(questions + fallback))[:4]


def suggest_questions(profile: dict) -> list[str]:
    if not OPENAI_API_KEY:
        return mock_suggest_questions(profile)

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.beta.chat.completions.parse(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You generate useful natural-language analytics questions for a CSV dataset. "
                        "Use only the provided column names. Include questions that are likely to produce "
                        "good charts: counts by category, numeric distributions, trends, comparisons, and relationships. "
                        "Return concise questions a non-technical user would click."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps({"dataset_profile": profile, "desired_count": 4}),
                },
            ],
            response_format=SuggestedQuestions,
        )
        parsed = response.choices[0].message.parsed
        if not parsed:
            raise ValueError("OpenAI returned no suggested questions")
        clean_questions = [question.strip() for question in parsed.questions if question.strip()]
        return clean_questions[:4] or mock_suggest_questions(profile)
    except Exception as exc:
        logger.warning("OpenAI question suggestion failed, using mock fallback: %s", exc)
        return mock_suggest_questions(profile)


def _mentioned_columns(question: str, columns: list[str]) -> list[str]:
    normalized_question = _normalize(question)
    return sorted(
        [column for column in columns if _mentions_column(question, column)],
        key=lambda column: min(
            (normalized_question.find(alias) for alias in _column_aliases(column) if alias in normalized_question),
            default=9999,
        ),
    )


def _mentioned_column(question: str, columns: list[str]) -> str | None:
    matches = _mentioned_columns(question, columns)
    return matches[0] if matches else None


def _detect_aggregation(question: str) -> str:
    normalized = _normalize(question)
    for aggregation, keywords in AGGREGATION_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return aggregation
    return "none"


def _is_comparative_question(question: str) -> bool:
    normalized = _normalize(question)
    return any(keyword in normalized for keyword in COMPARATIVE_KEYWORDS)


def _default_comparison_aggregation(metric: str | None) -> str:
    if not metric:
        return "count"
    return "mean"


def _detect_limit_and_sort(question: str) -> tuple[int | None, str | None]:
    normalized = _normalize(question)
    match = re.search(r"\b(?:top|bottom|first|last)\s+(\d+)\b", normalized)
    limit = int(match.group(1)) if match else None
    if any(word in normalized for word in ["bottom", "lowest", "smallest", "least"]):
        return limit or 5, "asc"
    if any(word in normalized for word in ["top", "highest", "largest", "most", "best"]):
        return limit or 5, "desc"
    return limit, None


def _detect_derived_feature(question: str, numeric: list[str], profile: dict | None = None) -> dict | None:
    normalized = _normalize(question)
    explicit_binning = any(keyword in normalized for keyword in ["bucket", "binned", "bin", "bins"])
    explicit_binning = explicit_binning or any(phrase in normalized for phrase in ["create groups", "create segments", "make groups", "make segments"])
    if explicit_binning:
        source = _mentioned_column(question, numeric)
        if not source and profile:
            source = _resolve_semantic_column(question, profile, "measure")
        source = source or (numeric[0] if numeric else None)
        if source:
            return {"name": f"{source}_group", "numerator": source, "denominator": None, "operation": "bin"}
    operation = "ratio" if any(word in normalized for word in [" per ", " ratio ", "rate", "efficiency"]) else None
    if not operation and any(word in normalized for word in ["difference", "gap", "delta"]):
        operation = "difference"
    if not operation:
        return None
    mentioned_numeric = _mentioned_columns(question, numeric)
    if len(mentioned_numeric) < 2:
        return None
    numerator, denominator = mentioned_numeric[0], mentioned_numeric[1]
    name = f"{numerator}_per_{denominator}" if operation == "ratio" else f"{numerator}_{operation}_{denominator}"
    return {"name": name, "numerator": numerator, "denominator": denominator, "operation": operation}


def _is_anomaly_question(question: str) -> bool:
    normalized = _normalize(question)
    return any(keyword in normalized for keyword in ANOMALY_KEYWORDS)


def _is_feature_engineering_question(question: str) -> bool:
    normalized = _normalize(question)
    return any(keyword in normalized for keyword in FEATURE_ENGINEERING_KEYWORDS)


def _detect_grouping(question: str, candidates: list[str]) -> str | None:
    normalized = _normalize(question)
    for phrase in [" by ", " per ", " across ", " grouped by ", " for each "]:
        if phrase.strip() in normalized:
            after_phrase = normalized.split(phrase.strip(), 1)[-1]
            match = _mentioned_column(after_phrase, candidates)
            if match:
                return match
    return None


def _low_cardinality_columns(profile: dict, columns: list[str]) -> list[str]:
    unique_counts = profile.get("unique_counts", {})
    row_count = max(profile.get("row_count", 1), 1)
    return [
        column
        for column in columns
        if unique_counts.get(column, row_count) <= min(30, max(10, row_count * 0.2))
    ]


def _merge_rag_context_into_profile(profile: dict, rag_context: list[dict] | None) -> dict:
    if not rag_context:
        return profile
    context_text = " ".join(chunk.get("content", "") for chunk in rag_context)
    metadata = dict(profile.get("dataset_metadata", {}))
    metadata["retrieved_context"] = context_text[:4000]
    return {**profile, "dataset_metadata": metadata}


def mock_interpret_question(question: str, profile: dict, rag_context: list[dict] | None = None) -> dict:
    profile = _merge_rag_context_into_profile(profile, rag_context)
    profile = {**profile, "semantic_schema": profile.get("semantic_schema") or build_semantic_schema(profile)}
    question_lower = question.lower()
    numeric, categorical, dates = _fields(profile)
    all_columns = profile["column_names"]
    grouping_candidates = categorical + _low_cardinality_columns(profile, numeric)
    mentioned_columns = _mentioned_columns(question_lower, all_columns)
    limit, sort = _detect_limit_and_sort(question_lower)
    mentioned_group = _detect_grouping(question_lower, categorical)
    if not mentioned_group and sort is not None:
        mentioned_group = _mentioned_column(question_lower, categorical)
    if not mentioned_group and sort is None:
        mentioned_group = _detect_grouping(question_lower, grouping_candidates)
    mentioned_metric = next((column for column in mentioned_columns if column in numeric and column != mentioned_group), None)
    mentioned_metric = mentioned_metric or _resolve_semantic_column(question_lower, profile, "measure")
    default_metric = next((column for column in numeric if column not in grouping_candidates), numeric[0] if numeric else None)
    derived_feature = _detect_derived_feature(question_lower, numeric, profile)
    aggregation = _detect_aggregation(question_lower)
    if "rate" in _normalize(question_lower) and mentioned_metric:
        aggregation = "mean"
    x_axis = categorical[0] if categorical else None
    y_axis = mentioned_metric or default_metric
    intent = "comparison"
    chart_type = "bar"

    if _is_anomaly_question(question_lower):
        intent = "anomaly_detection"
        chart_type = "box"
        x_axis = mentioned_group or _mentioned_column(question_lower, categorical)
        y_axis = mentioned_metric or default_metric
        aggregation = "none"
    elif derived_feature:
        intent = "derived_feature"
        chart_type = "bar"
        x_axis = derived_feature["name"] if derived_feature.get("operation") == "bin" else mentioned_group or _mentioned_column(question_lower, grouping_candidates) or (
            grouping_candidates[0] if grouping_candidates else None
        )
        if derived_feature.get("operation") == "bin":
            y_axis = next(
                (column for column in mentioned_columns if column in numeric and column != derived_feature["numerator"]),
                None,
            )
        else:
            y_axis = derived_feature["name"]
        if derived_feature.get("operation") == "bin" and not y_axis:
            y_axis = next((column for column in numeric if column != derived_feature["numerator"]), default_metric)
        aggregation = "mean" if x_axis and y_axis else "count"
    elif aggregation == "count":
        intent = "count"
        chart_type = "bar"
        count_group = mentioned_group or _mentioned_column(question_lower, grouping_candidates)
        x_axis = count_group or (grouping_candidates[0] if grouping_candidates else all_columns[0])
        y_axis = None
    elif any(word in question_lower for word in ["trend", "monthly", "over time", "date"]):
        intent = "time_series"
        chart_type = "line"
        x_axis = dates[0] if dates else x_axis
        y_axis = mentioned_metric or y_axis
        aggregation = "sum" if aggregation == "sum" else aggregation
    elif (
        any(phrase in question_lower for phrase in ["what factors", "which factors", "factors seem related", "drivers of", "related to"])
        and len(numeric) >= 3
    ):
        intent = "correlation"
        chart_type = "heatmap"
        target = mentioned_metric or _resolve_semantic_column(question_lower, profile, "measure")
        x_axis = target
        y_axis = None
        aggregation = "none"
    elif any(word in question_lower for word in RELATIONSHIP_KEYWORDS) or (
        " vs " in question_lower and len([column for column in mentioned_columns if column in numeric]) >= 2
    ) or (
        "between" in question_lower and len([column for column in mentioned_columns if column in numeric]) >= 2
    ):
        intent = "correlation"
        chart_type = "scatter"
        mentioned_numeric = [column for column in mentioned_columns if column in numeric]
        x_axis = mentioned_numeric[0] if mentioned_numeric else (numeric[0] if numeric else x_axis)
        y_axis = mentioned_numeric[1] if len(mentioned_numeric) > 1 else next((col for col in numeric if col != x_axis), y_axis)
        aggregation = "none"
    elif any(word in question_lower for word in ["distribution", "spread", "histogram"]):
        mentioned_category = _mentioned_column(question_lower, categorical)
        if mentioned_category:
            intent = "count"
            chart_type = "bar"
            x_axis = mentioned_category
            y_axis = None
            aggregation = "count"
        else:
            intent = "distribution"
            chart_type = "histogram"
            x_axis = mentioned_metric or y_axis
            y_axis = None
            aggregation = "none"
    elif _is_comparative_question(question_lower):
        intent = "comparison"
        chart_type = "bar"
        x_axis = mentioned_group or _mentioned_column(question_lower, grouping_candidates) or (
            grouping_candidates[0] if grouping_candidates else None
        )
        y_axis = mentioned_metric or default_metric
        aggregation = aggregation if aggregation != "none" else _default_comparison_aggregation(y_axis)
    elif aggregation in {"mean", "sum", "median", "min", "max"} and mentioned_group:
        intent = "comparison"
        chart_type = "bar"
        x_axis = mentioned_group
        y_axis = mentioned_metric or y_axis
    elif aggregation in {"mean", "sum", "median", "min", "max"} and mentioned_metric:
        intent = "single_metric"
        chart_type = "bar"
        x_axis = None
        y_axis = mentioned_metric
    elif "pie" in question_lower or "share" in question_lower:
        intent = "share"
        chart_type = "pie"
        aggregation = "sum"

    return {
        "intent": intent,
        "x_axis": x_axis,
        "y_axis": y_axis,
        "aggregation": aggregation,
        "chart_type": chart_type,
        "filters": [],
        "derived_feature": derived_feature,
        "sort": sort,
        "limit": limit,
        "anomaly_detection": intent == "anomaly_detection",
        "preprocessing_steps": [
            "Coerce numeric-like columns before analysis",
            "Drop missing values only for the selected chart fields",
        ],
        "reasoning_steps": [
            f"Detected intent: {intent}",
            f"Selected chart type: {chart_type}",
            f"Mapped axes: x={x_axis}, y={y_axis}",
        ],
        "explanation": "Mock interpretation used because no OpenAI API key is configured.",
    }


def interpret_question(question: str, profile: dict, rag_context: list[dict] | None = None) -> dict[str, Any]:
    profile = _merge_rag_context_into_profile(profile, rag_context)
    profile = {**profile, "semantic_schema": profile.get("semantic_schema") or build_semantic_schema(profile)}
    if not OPENAI_API_KEY:
        return mock_interpret_question(question, profile, rag_context)

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.beta.chat.completions.parse(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a data visualization planning agent. Return only a structured analysis plan. "
                        "Use only columns that exist in the provided dataset profile. Map natural language aliases "
                        "to columns using column names, logical types, semantic aliases, retrieved context, and statistical suitability. "
                        "Do not assume domain-specific columns; adapt to the uploaded schema only. "
                        "For categorical distributions, use aggregation=count and chart_type=bar. "
                        "For numeric distributions, use chart_type=histogram. "
                        "For rates over 0/1 columns, use aggregation=mean. "
                        "For count/how many questions, use aggregation=count. "
                        "For comparative insights, comparison, breakdown, or difference questions, choose a useful "
                        "categorical or low-cardinality x_axis and a meaningful numeric y_axis, then use bar chart. "
                        "For time trends, use a date column on x_axis and a numeric column on y_axis. "
                        "For relationships between two numeric columns, use chart_type=scatter."
                        "For broad questions like 'what factors are related to X' or 'which variables correlate with X', "
                        "use chart_type=heatmap when several numeric columns exist. "
                        "For derived metrics such as ratios, per-unit metrics, differences, or efficiency, "
                        "set derived_feature with numerator, denominator, operation, and use the derived feature as y_axis. "
                        "For feature engineering prompts such as bins, buckets, age groups, or segments, set "
                        "derived_feature.operation='bin' and use the new engineered feature as x_axis. "
                        "For anomaly/outlier/unusual/spike prompts, set anomaly_detection=true and use a box plot "
                        "or a scatter plot with the suspected numeric metric. "
                        "For top/bottom/highest/lowest prompts, set sort and limit."
                        "Always include reasoning_steps and preprocessing_steps."
                        "Use retrieved_context as supporting evidence for semantic column mapping, but never use "
                        "columns that are absent from dataset_profile.column_names."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "question": question,
                            "dataset_profile": profile,
                            "semantic_schema": profile["semantic_schema"],
                            "retrieved_context": rag_context or [],
                            "allowed_chart_types": sorted(VALID_CHART_TYPES),
                            "allowed_aggregations": sorted(VALID_AGGREGATIONS),
                        }
                    ),
                },
            ],
            response_format=AgentPlan,
        )
        parsed = response.choices[0].message.parsed
        if not parsed:
            raise ValueError("OpenAI returned no parsed plan")
        plan = parsed.model_dump()
        plan["explanation"] = f"OpenAI mapped the question to the dataset schema. {plan['explanation']}"
        return _validated_plan(plan, profile, question)
    except Exception as exc:
        logger.warning("OpenAI interpretation failed, using mock fallback: %s", exc)
        return mock_interpret_question(question, profile, rag_context)
