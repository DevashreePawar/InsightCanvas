from __future__ import annotations

from typing import Any

import pandas as pd


def _pct(value: float) -> float:
    return round(float(value), 2)


def _numeric_outliers(series: pd.Series) -> dict[str, Any] | None:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if len(clean) < 8:
        return None

    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return None

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    count = int(((clean < lower) | (clean > upper)).sum())
    if count == 0:
        return None

    return {
        "count": count,
        "percentage": _pct(count / len(clean) * 100),
        "lower_bound": round(float(lower), 3),
        "upper_bound": round(float(upper), 3),
    }


def build_data_quality_report(df: pd.DataFrame, profile: dict) -> dict:
    """Create a compact, dataset-agnostic quality report for the analyst view."""
    row_count = max(len(df), 1)
    duplicate_rows = int(df.duplicated().sum())
    missing = profile.get("missing_value_percentage", {})
    unique_counts = profile.get("unique_counts", {})
    logical_types = profile.get("logical_types", {})

    high_missing = [
        {"column": column, "missing_percentage": value}
        for column, value in sorted(missing.items(), key=lambda item: item[1] or 0, reverse=True)
        if isinstance(value, (int, float)) and value >= 20
    ][:8]

    constant_columns = [
        column
        for column, unique_count in unique_counts.items()
        if int(unique_count or 0) <= 1 and column not in profile.get("sensitive_columns", {})
    ][:8]

    high_cardinality = [
        {
            "column": column,
            "unique_count": int(unique_counts.get(column, 0) or 0),
            "unique_percentage": _pct((unique_counts.get(column, 0) or 0) / row_count * 100),
        }
        for column, logical_type in logical_types.items()
        if logical_type == "text"
    ][:8]

    outliers = []
    for column in df.select_dtypes(include="number").columns:
        if column in set(profile.get("possible_id_columns", [])):
            continue
        stats = _numeric_outliers(df[column])
        if stats:
            outliers.append({"column": column, **stats})

    score = 100
    score -= min(30, int(sum(value for value in missing.values() if isinstance(value, (int, float))) / max(len(missing), 1) * 0.6))
    score -= min(20, int(duplicate_rows / row_count * 100))
    score -= min(15, len(profile.get("possible_id_columns", [])) * 2)
    score -= min(15, len(high_missing) * 3)
    score = max(0, min(100, score))

    recommendations = []
    if high_missing:
        recommendations.append("Review columns with high missing values before using them in comparisons or models.")
    if duplicate_rows:
        recommendations.append("Check duplicate rows so repeated records do not distort counts and averages.")
    if profile.get("possible_id_columns"):
        recommendations.append("Use identifier columns for lookup only; avoid treating them as trends or distributions.")
    if outliers:
        recommendations.append("Inspect numeric outliers because they can strongly affect averages and rankings.")
    if profile.get("sensitive_columns"):
        recommendations.append("Sensitive columns were detected; keep them out of prompts, charts, and exports.")
    if not recommendations:
        recommendations.append("The dataset looks clean enough for exploratory analysis.")

    return {
        "score": score,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "duplicate_rows": duplicate_rows,
        "duplicate_percentage": _pct(duplicate_rows / row_count * 100),
        "high_missing_columns": high_missing,
        "constant_columns": constant_columns,
        "likely_identifier_columns": profile.get("possible_id_columns", []),
        "sensitive_columns": profile.get("sensitive_columns", {}),
        "high_cardinality_text_columns": high_cardinality,
        "numeric_outliers": outliers[:8],
        "recommendations": recommendations[:5],
    }
