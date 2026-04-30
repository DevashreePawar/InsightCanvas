from __future__ import annotations

from typing import Any

import pandas as pd


def _round(value: Any, places: int = 3):
    if pd.isna(value):
        return None
    try:
        return round(float(value), places)
    except (TypeError, ValueError):
        return value


def _numeric_columns(df: pd.DataFrame, profile: dict) -> list[str]:
    excluded = set(profile.get("possible_id_columns", [])) | set(profile.get("sensitive_columns", {}).keys())
    logical_types = profile.get("logical_types", {})
    return [
        column
        for column in df.select_dtypes(include="number").columns
        if column not in excluded and logical_types.get(column) not in {"identifier", "sensitive_identifier", "categorical_numeric"}
    ]


def _categorical_columns(profile: dict) -> list[str]:
    excluded = set(profile.get("possible_id_columns", [])) | set(profile.get("sensitive_columns", {}).keys())
    logical_types = profile.get("logical_types", {})
    return [
        column
        for column in profile.get("column_names", [])
        if column not in excluded and logical_types.get(column) in {"categorical", "categorical_numeric", "multi_value_categorical"}
    ]


def _top_correlations(df: pd.DataFrame, numeric: list[str]) -> list[dict]:
    if len(numeric) < 2:
        return []
    corr = df[numeric].corr(numeric_only=True)
    pairs = []
    for index, column_a in enumerate(numeric):
        for column_b in numeric[index + 1 :]:
            value = corr.loc[column_a, column_b]
            if pd.isna(value):
                continue
            pairs.append(
                {
                    "columns": [column_a, column_b],
                    "correlation": _round(value),
                    "strength": "strong" if abs(value) >= 0.7 else "moderate" if abs(value) >= 0.4 else "weak",
                    "direction": "positive" if value > 0 else "negative",
                }
            )
    return sorted(pairs, key=lambda item: abs(item["correlation"] or 0), reverse=True)[:5]


def _categorical_balance(df: pd.DataFrame, categorical: list[str]) -> list[dict]:
    results = []
    for column in categorical[:8]:
        values = df[column].dropna().astype(str)
        if values.empty:
            continue
        counts = values.value_counts().head(5)
        top_label = str(counts.index[0])
        top_count = int(counts.iloc[0])
        results.append(
            {
                "column": column,
                "unique_count": int(values.nunique()),
                "top_value": top_label,
                "top_value_share": _round(top_count / len(values) * 100, 2),
                "top_values": {str(key): int(value) for key, value in counts.items()},
            }
        )
    return results


def _group_comparisons(df: pd.DataFrame, numeric: list[str], categorical: list[str]) -> list[dict]:
    comparisons = []
    for group in categorical[:4]:
        if df[group].nunique(dropna=True) > 20:
            continue
        for metric in numeric[:4]:
            grouped = df[[group, metric]].dropna()
            if grouped.empty:
                continue
            means = grouped.groupby(group)[metric].mean().sort_values(ascending=False)
            if len(means) < 2:
                continue
            comparisons.append(
                {
                    "group_column": group,
                    "metric": metric,
                    "highest_group": str(means.index[0]),
                    "highest_mean": _round(means.iloc[0]),
                    "lowest_group": str(means.index[-1]),
                    "lowest_mean": _round(means.iloc[-1]),
                    "spread": _round(means.iloc[0] - means.iloc[-1]),
                }
            )
    return sorted(comparisons, key=lambda item: abs(item.get("spread") or 0), reverse=True)[:5]


def build_statistical_summary(df: pd.DataFrame, profile: dict) -> dict:
    """Summarize EDA statistics without assuming a specific dataset domain."""
    numeric = _numeric_columns(df, profile)
    categorical = _categorical_columns(profile)

    distributions = []
    for column in numeric[:8]:
        series = pd.to_numeric(df[column], errors="coerce").dropna()
        if series.empty:
            continue
        distributions.append(
            {
                "column": column,
                "mean": _round(series.mean()),
                "median": _round(series.median()),
                "std": _round(series.std()),
                "min": _round(series.min()),
                "max": _round(series.max()),
                "skew": _round(series.skew()),
            }
        )

    correlations = _top_correlations(df, numeric)
    categorical_balance = _categorical_balance(df, categorical)
    group_comparisons = _group_comparisons(df, numeric, categorical)

    takeaways = []
    if distributions:
        most_skewed = max(distributions, key=lambda item: abs(item.get("skew") or 0))
        if abs(most_skewed.get("skew") or 0) >= 1:
            takeaways.append(f"{most_skewed['column']} is noticeably skewed, so medians may be more reliable than averages.")
    if correlations:
        top = correlations[0]
        takeaways.append(
            f"{top['columns'][0]} and {top['columns'][1]} have the strongest {top['direction']} numeric relationship found here."
        )
    if categorical_balance:
        dominant = max(categorical_balance, key=lambda item: item.get("top_value_share") or 0)
        if (dominant.get("top_value_share") or 0) >= 60:
            takeaways.append(f"{dominant['column']} is dominated by {dominant['top_value']}, which may affect grouped comparisons.")
    if group_comparisons:
        top_group = group_comparisons[0]
        takeaways.append(
            f"{top_group['metric']} varies most across {top_group['group_column']}, from {top_group['lowest_group']} to {top_group['highest_group']}."
        )
    if not takeaways:
        takeaways.append("The dataset has enough structure for EDA, but no dominant statistical pattern stood out automatically.")

    return {
        "numeric_columns_analyzed": numeric[:8],
        "categorical_columns_analyzed": categorical[:8],
        "distributions": distributions,
        "correlations": correlations,
        "categorical_balance": categorical_balance,
        "group_comparisons": group_comparisons,
        "takeaways": takeaways[:4],
    }
