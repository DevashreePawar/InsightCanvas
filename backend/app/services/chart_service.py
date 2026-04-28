import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio

from app.services.ai_service import interpret_question
from app.services.profile_service import profile_dataset
from app.services.quality_service import identifier_prompt_warning, selected_identifier_warning, sensitive_prompt_warning


def _preprocess_dataframe(df):
    cleaned = df.copy()
    null_like = {"", "unknown", "unk", "n/a", "na", "null", "none", "missing", "-"}
    for column in cleaned.columns:
        if cleaned[column].dtype == "object":
            cleaned[column] = cleaned[column].apply(
                lambda value: np.nan if isinstance(value, str) and value.strip().lower() in null_like else value
            )
            numeric_candidate = pd.to_numeric(cleaned[column], errors="coerce")
            if numeric_candidate.notna().mean() >= 0.85:
                cleaned[column] = numeric_candidate
    return cleaned


def _coerce_filter_value(series, value: str):
    try:
        if series.dtype.kind in {"i", "u"}:
            return int(float(value))
        if series.dtype.kind == "f":
            return float(value)
    except ValueError:
        return value
    return str(value)


def _apply_filters(df, filters: list[dict]):
    filtered = df.copy()
    for item in filters or []:
        column = item.get("column")
        operator = item.get("operator")
        if column not in filtered.columns:
            continue
        value = _coerce_filter_value(filtered[column], item.get("value", ""))
        if operator == "eq":
            filtered = filtered[filtered[column].astype(str).str.lower() == str(value).lower()]
        elif operator == "neq":
            filtered = filtered[filtered[column].astype(str).str.lower() != str(value).lower()]
        elif operator == "contains":
            filtered = filtered[filtered[column].astype(str).str.contains(str(value), case=False, na=False)]
        elif operator == "gt":
            filtered = filtered[filtered[column] > value]
        elif operator == "gte":
            filtered = filtered[filtered[column] >= value]
        elif operator == "lt":
            filtered = filtered[filtered[column] < value]
        elif operator == "lte":
            filtered = filtered[filtered[column] <= value]
    return filtered


def _apply_derived_feature(df, derived_feature: dict | None):
    if not derived_feature:
        return df
    numerator = derived_feature.get("numerator")
    denominator = derived_feature.get("denominator")
    operation = derived_feature.get("operation")
    name = derived_feature.get("name")
    if not name or numerator not in df.columns:
        return df

    enriched = df.copy()
    if operation == "bin":
        source = enriched[numerator].dropna()
        if source.empty:
            return enriched
        try:
            if source.nunique() >= 3:
                enriched[name] = pd.qcut(enriched[numerator], q=3, labels=["low", "medium", "high"], duplicates="drop").astype(str)
            else:
                enriched[name] = pd.cut(enriched[numerator], bins=min(2, source.nunique()), duplicates="drop").astype(str)
        except ValueError:
            enriched[name] = pd.cut(enriched[numerator], bins=min(3, max(2, source.nunique())), duplicates="drop").astype(str)
    elif operation == "ratio" and denominator in enriched.columns:
        denominator_series = enriched[denominator].replace(0, float("nan"))
        enriched[name] = enriched[numerator] / denominator_series
    elif operation == "difference" and denominator in enriched.columns:
        enriched[name] = enriched[numerator] - enriched[denominator]
    elif operation == "sum" and denominator in enriched.columns:
        enriched[name] = enriched[numerator] + enriched[denominator]
    elif operation == "product" and denominator in enriched.columns:
        enriched[name] = enriched[numerator] * enriched[denominator]
    return enriched


def _apply_sort_and_limit(df, y_axis: str | None, recommendation: dict):
    sort = recommendation.get("sort")
    limit = recommendation.get("limit")
    if sort and y_axis in df.columns:
        df = df.sort_values(y_axis, ascending=sort == "asc")
    if limit:
        df = df.head(limit)
    return df


def _explode_multi_value_column(df, column: str | None, profile: dict):
    if not column or column not in set(profile.get("multi_value_columns", [])) or column not in df.columns:
        return df
    exploded = df.copy()
    exploded[column] = exploded[column].fillna("").astype(str).str.split(r"\s*[,;|]\s*", regex=True)
    exploded = exploded.explode(column)
    exploded[column] = exploded[column].astype(str).str.strip()
    return exploded[exploded[column] != ""]


def _safe_axes(chart_type: str, x_axis: str | None, y_axis: str | None, df):
    columns = set(df.columns)
    safe_x = x_axis if x_axis in columns else None
    safe_y = y_axis if y_axis in columns else None
    if chart_type in {"bar", "line", "box", "scatter"} and safe_y is None:
        numeric_columns = [column for column in df.columns if getattr(df[column], "dtype", None).kind in {"i", "u", "f"}]
        safe_y = numeric_columns[0] if numeric_columns else None
    if chart_type in {"bar", "line", "box", "pie", "histogram"} and safe_x is None:
        safe_x = df.columns[0] if len(df.columns) else None
    if chart_type == "scatter" and safe_x is None:
        numeric_columns = [column for column in df.columns if getattr(df[column], "dtype", None).kind in {"i", "u", "f"}]
        safe_x = numeric_columns[0] if numeric_columns else None
    return safe_x, safe_y


def _drop_missing_chart_fields(df, *fields):
    valid_fields = [field for field in fields if field in df.columns]
    if not valid_fields:
        return df
    return df.dropna(subset=valid_fields)


def _anomaly_summary(df, y_axis: str | None):
    if not y_axis or y_axis not in df.columns:
        return None
    series = df[y_axis].dropna()
    if series.empty or series.dtype.kind not in {"i", "u", "f"}:
        return None
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    count = int(((series < lower) | (series > upper)).sum())
    return {"column": y_axis, "count": count, "lower": round(float(lower), 2), "upper": round(float(upper), 2)}


def recommend_chart(question: str, profile: dict, interpretation: dict | None = None, rag_context: list[dict] | None = None) -> dict:
    result = interpretation or interpret_question(question, profile, rag_context)
    id_columns = set(profile.get("possible_id_columns", []))
    sensitive_columns = set(profile.get("sensitive_columns", {}).keys())
    excluded_columns = id_columns | sensitive_columns
    numeric = [col for col, dtype in profile["data_types"].items() if ("int" in dtype or "float" in dtype) and col not in excluded_columns]
    numeric_all = [col for col, dtype in profile["data_types"].items() if "int" in dtype or "float" in dtype]
    if not numeric:
        numeric = numeric_all
    categorical = [col for col in profile["column_names"] if col not in numeric_all and col not in excluded_columns]
    dates = profile.get("date_columns", [])

    if result.get("intent") == "time_series" and dates and numeric:
        result.update({"chart_type": "line", "x_axis": result.get("x_axis") or dates[0], "y_axis": result.get("y_axis") or numeric[0]})
    elif result.get("intent") == "correlation" and len(numeric) >= 3 and result.get("chart_type") == "heatmap":
        result.update({"chart_type": "heatmap", "x_axis": result.get("x_axis") if result.get("x_axis") in numeric else None, "y_axis": None})
    elif result.get("intent") == "correlation" and len(numeric) >= 2:
        result.update({"chart_type": result.get("chart_type") if result.get("chart_type") == "heatmap" else "scatter", "x_axis": result.get("x_axis") or numeric[0], "y_axis": result.get("y_axis") or numeric[1]})
    elif result.get("intent") == "distribution" and numeric:
        result.update({"chart_type": "histogram", "x_axis": result.get("x_axis") or numeric[0], "y_axis": None})
    elif result.get("aggregation") == "count" and result.get("x_axis"):
        result.update({"chart_type": result.get("chart_type") or "bar", "y_axis": None})
    elif result.get("intent") == "single_metric" and result.get("y_axis"):
        result.update({"chart_type": "bar", "x_axis": None})
    elif categorical and numeric:
        result.update({"chart_type": result.get("chart_type") or "bar", "x_axis": result.get("x_axis") or categorical[0], "y_axis": result.get("y_axis") or numeric[0]})
    elif categorical:
        result.update({"chart_type": "bar", "x_axis": categorical[0], "y_axis": None})
    elif numeric:
        result.update({"chart_type": "histogram", "x_axis": numeric[0], "y_axis": None})

    return result


def _prepare_dataframe(df, recommendation, profile: dict):
    x_axis = recommendation.get("x_axis")
    y_axis = recommendation.get("y_axis")
    aggregation = recommendation.get("aggregation", "none")
    chart_type = recommendation.get("chart_type")
    df = _explode_multi_value_column(df, x_axis, profile)

    if aggregation == "count" and x_axis:
        grouped = df.groupby(x_axis, dropna=False).size().reset_index(name="count")
        return _apply_sort_and_limit(grouped, "count", recommendation), "count"

    if chart_type in {"bar", "line", "pie"} and x_axis and y_axis and aggregation in {"sum", "mean", "median", "min", "max"}:
        grouped = df.groupby(x_axis, dropna=False)[y_axis].agg(aggregation).reset_index()
        return _apply_sort_and_limit(grouped, y_axis, recommendation), y_axis

    if chart_type == "bar" and not x_axis and y_axis and aggregation in {"sum", "mean", "median", "min", "max"}:
        value = getattr(df[y_axis], aggregation)()
        label = f"{aggregation} {y_axis}".replace("_", " ").title()
        return df.__class__({"metric": [label], "value": [round(float(value), 2)]}), "value"

    return df, y_axis


def _numeric_columns_for_heatmap(df, profile: dict) -> list[str]:
    id_columns = set(profile.get("possible_id_columns", []))
    sensitive_columns = set(profile.get("sensitive_columns", {}).keys())
    excluded_columns = id_columns | sensitive_columns
    return [
        column
        for column in df.select_dtypes(include="number").columns
        if column not in excluded_columns and df[column].nunique(dropna=True) > 1
    ]


def _build_heatmap(df, profile: dict, recommendation: dict, question: str):
    numeric_columns = _numeric_columns_for_heatmap(df, profile)
    if len(numeric_columns) < 2:
        return None, "A correlation heatmap needs at least two non-identifier numeric columns."
    corr = df[numeric_columns].corr(numeric_only=True).round(3)
    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title=f"Correlation heatmap for: {question}",
    )
    fig.update_layout(autosize=True, margin=dict(l=24, r=24, t=64, b=24), paper_bgcolor="white", plot_bgcolor="white")
    fig.layout.template = None
    return fig, None


def _build_heatmap_insight(df, profile: dict, target: str | None) -> str:
    numeric = _numeric_columns_for_heatmap(df, profile)
    if len(numeric) < 2:
        return "The heatmap needs at least two meaningful numeric fields to compare relationships."
    corr = df[numeric].corr(numeric_only=True)
    if target in corr.columns:
        ranked = corr[target].drop(labels=[target], errors="ignore").abs().sort_values(ascending=False)
        if not ranked.empty:
            top = ranked.index[0]
            signed = corr.loc[top, target]
            direction = "positive" if signed > 0 else "negative"
            return f"The heatmap compares numeric relationships across the dataset. {top} has the strongest relationship with {target}, showing a {direction} correlation of {round(float(signed), 2)}."
    pairs = corr.where(~np.eye(len(corr), dtype=bool)).abs().stack().sort_values(ascending=False)
    if not pairs.empty:
        first_pair = pairs.index[0]
        return f"The heatmap highlights relationships between meaningful numeric fields. The strongest visible pairing is {first_pair[0]} and {first_pair[1]} with correlation {round(float(pairs.iloc[0]), 2)}."
    return "The heatmap compares numeric columns to show which variables move together most strongly."


def generate_chart(df, question: str, metadata: dict | None = None, rag_context: list[dict] | None = None) -> dict:
    df = _preprocess_dataframe(df)
    profile = profile_dataset(df, metadata)
    interpretation = interpret_question(question, profile, rag_context)
    recommendation = recommend_chart(question, profile, interpretation, rag_context)
    data_quality_warnings = list(profile.get("data_quality_warnings", []))
    identifier_warning = (
        sensitive_prompt_warning(question, profile, recommendation)
        or identifier_prompt_warning(question, profile, recommendation)
        or selected_identifier_warning(profile, recommendation)
    )
    if identifier_warning:
        return {
            "profile": profile,
            "interpretation": interpretation,
            "recommendation": recommendation,
            "chart_type": "not_applicable",
            "chart_json": None,
            "insight": identifier_warning["warning"],
            "reasoning": [
                "The agent detected that the requested column behaves like a row identifier.",
                "Identifier distributions usually mirror row numbering rather than business behavior.",
                "The chart was intentionally skipped to avoid a misleading visualization.",
            ],
            "data_quality_warnings": data_quality_warnings + [identifier_warning["warning"]],
            "suggested_alternatives": identifier_warning["suggested_alternatives"],
            "anomaly_summary": None,
            "retrieved_context": rag_context or [],
        }
    analysis_df = _apply_filters(df, recommendation.get("filters", []))
    if analysis_df.empty:
        analysis_df = df
        recommendation["filters"] = []
    analysis_df = _apply_derived_feature(analysis_df, recommendation.get("derived_feature"))
    chart_type = recommendation.get("chart_type", "bar")
    x_axis = recommendation.get("x_axis")
    y_axis = recommendation.get("y_axis")

    if chart_type == "heatmap":
        fig, heatmap_error = _build_heatmap(analysis_df, profile, recommendation, question)
        if heatmap_error:
            data_quality_warnings.append(heatmap_error)
            recommendation["chart_type"] = "scatter"
            chart_type = "scatter"
        else:
            insight = _build_heatmap_insight(analysis_df, profile, x_axis)
            return {
                "profile": profile,
                "interpretation": interpretation,
                "recommendation": recommendation,
                "chart_type": "heatmap",
                "chart_json": pio.to_json(fig),
                "insight": insight,
                "reasoning": recommendation.get("reasoning_steps", []),
                "data_quality_warnings": data_quality_warnings,
                "suggested_alternatives": [],
                "anomaly_summary": None,
                "retrieved_context": rag_context or [],
            }

    chart_df, plotted_y = _prepare_dataframe(analysis_df, recommendation, profile)
    plotted_x = x_axis or ("metric" if "metric" in chart_df.columns else x_axis)
    plotted_x, plotted_y = _safe_axes(chart_type, plotted_x, plotted_y, chart_df)
    chart_df = _drop_missing_chart_fields(chart_df, plotted_x, plotted_y)
    if chart_df.empty:
        warning = "No usable rows remained after cleaning missing or invalid values for the selected fields."
        return {
            "profile": profile,
            "interpretation": interpretation,
            "recommendation": recommendation,
            "chart_type": "not_applicable",
            "chart_json": None,
            "insight": warning,
            "reasoning": recommendation.get("reasoning_steps", []),
            "data_quality_warnings": data_quality_warnings + [warning],
            "suggested_alternatives": [],
            "anomaly_summary": None,
            "retrieved_context": rag_context or [],
        }

    title = f"{chart_type.title()} for: {question}"
    if chart_type == "line":
        fig = px.line(chart_df, x=plotted_x, y=plotted_y, markers=True, title=title)
    elif chart_type == "scatter":
        fig = px.scatter(chart_df, x=plotted_x, y=plotted_y, trendline=None, title=title)
    elif chart_type == "histogram":
        fig = px.histogram(chart_df, x=plotted_x, title=title)
    elif chart_type == "pie":
        fig = px.pie(chart_df, names=plotted_x, values=plotted_y, title=title)
    elif chart_type == "box":
        fig = px.box(chart_df, x=plotted_x, y=plotted_y, title=title)
    else:
        fig = px.bar(chart_df, x=plotted_x, y=plotted_y, title=title)

    fig.update_layout(autosize=True, margin=dict(l=24, r=24, t=64, b=24), paper_bgcolor="white", plot_bgcolor="white")
    fig.layout.template = None
    anomaly = _anomaly_summary(chart_df, plotted_y) if recommendation.get("anomaly_detection") else None
    insight = build_insight(chart_type, plotted_x, plotted_y, question, chart_df, recommendation, anomaly)
    return {
        "profile": profile,
        "interpretation": interpretation,
        "recommendation": recommendation,
        "chart_type": chart_type,
        "chart_json": pio.to_json(fig),
        "insight": insight,
        "reasoning": recommendation.get("reasoning_steps", []),
        "data_quality_warnings": data_quality_warnings,
        "suggested_alternatives": [],
        "anomaly_summary": anomaly,
        "retrieved_context": rag_context or [],
    }


def build_insight(chart_type: str, x_axis: str | None, y_axis: str | None, question: str, chart_df=None, recommendation=None, anomaly=None) -> str:
    aggregation = (recommendation or {}).get("aggregation")
    if anomaly:
        return (
            f"Detected {anomaly['count']} potential outliers in {anomaly['column']} using the IQR rule. "
            f"Typical values fall between {anomaly['lower']} and {anomaly['upper']}."
        )
    if y_axis == "count" and chart_df is not None and x_axis in chart_df.columns:
        sorted_df = chart_df.sort_values("count", ascending=False)
        leader = sorted_df.iloc[0]
        return f"{leader[x_axis]} has the highest count at {int(leader['count'])} records."
    if aggregation in {"mean", "sum", "median", "min", "max"} and y_axis == "value" and chart_df is not None:
        value = chart_df["value"].iloc[0]
        return f"The requested {aggregation} is {value} for: {question}"
    if aggregation in {"mean", "sum", "median", "min", "max"} and chart_df is not None and x_axis and y_axis:
        ascending = (recommendation or {}).get("sort") == "asc"
        sorted_df = chart_df.sort_values(y_axis, ascending=ascending)
        leader = sorted_df.iloc[0]
        direction = "lowest" if ascending else "highest"
        return f"The {aggregation} of {y_axis} is {direction} for {x_axis} = {leader[x_axis]} at {round(float(leader[y_axis]), 2)}."
    if chart_type == "line":
        return f"The trend view helps reveal whether {y_axis} is rising, falling, or seasonal across {x_axis}."
    if chart_type == "scatter":
        if chart_df is not None and x_axis in chart_df.columns and y_axis in chart_df.columns:
            corr = chart_df[[x_axis, y_axis]].corr(numeric_only=True).iloc[0, 1]
            if pd.notna(corr):
                direction = "positive" if corr > 0 else "negative"
                strength = "strong" if abs(corr) >= 0.7 else "moderate" if abs(corr) >= 0.35 else "weak"
                return f"{x_axis} and {y_axis} show a {strength} {direction} relationship with correlation {round(float(corr), 2)}. The scatter plot helps verify whether that pattern is consistent or driven by outliers."
        return f"The scatter plot makes it easier to inspect whether {x_axis} and {y_axis} move together."
    if chart_type == "heatmap" and chart_df is not None:
        numeric = [column for column in chart_df.select_dtypes(include="number").columns if chart_df[column].nunique(dropna=True) > 1]
        if len(numeric) >= 2:
            corr = chart_df[numeric].corr(numeric_only=True)
            target = x_axis if x_axis in corr.columns else None
            if target:
                ranked = corr[target].drop(labels=[target], errors="ignore").abs().sort_values(ascending=False)
                if not ranked.empty:
                    top = ranked.index[0]
                    signed = corr.loc[top, target]
                    direction = "positive" if signed > 0 else "negative"
                    return f"The heatmap compares numeric relationships across the dataset. {top} has the strongest relationship with {target}, showing a {direction} correlation of {round(float(signed), 2)}."
            pairs = corr.where(~np.eye(len(corr), dtype=bool)).abs().stack().sort_values(ascending=False)
            if not pairs.empty:
                first_pair = pairs.index[0]
                return f"The heatmap highlights relationships between numeric fields. The strongest visible pairing is {first_pair[0]} and {first_pair[1]} with correlation {round(float(pairs.iloc[0]), 2)}."
        return "The heatmap compares numeric columns to show which variables move together most strongly."
    if chart_type == "histogram":
        if chart_df is not None and x_axis in chart_df.columns:
            series = chart_df[x_axis].dropna()
            if not series.empty:
                return f"{x_axis} ranges from {round(float(series.min()), 2)} to {round(float(series.max()), 2)}, with an average of {round(float(series.mean()), 2)}."
        return f"The histogram shows the shape and spread of {x_axis}, which is useful for spotting skew and outliers."
    if chart_type == "pie":
        return f"The pie chart highlights proportional contribution by {x_axis} for the question: {question}"
    return f"The bar chart compares {y_axis} across {x_axis}, making the strongest and weakest categories easier to spot."
