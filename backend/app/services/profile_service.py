import math
import re
from typing import Any

import pandas as pd

MULTI_VALUE_SEPARATORS = [",", ";", "|"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\d)")
SENSITIVE_NAME_TOKENS = {"name", "first name", "last name", "full name", "customer name", "patient name"}
SENSITIVE_EMAIL_TOKENS = {"email", "e mail", "mail"}
SENSITIVE_PHONE_TOKENS = {"phone", "mobile", "cell", "telephone", "contact number"}


def _normalize(value: str) -> str:
    split_camel = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(value))
    return re.sub(r"[^a-z0-9]+", " ", split_camel.lower()).strip()


def _tokenize(value: str) -> set[str]:
    return {token for token in _normalize(value).split() if token}


def detect_multi_value_columns(df: pd.DataFrame) -> list[str]:
    multi_value_columns = []
    for column in df.select_dtypes(include="object").columns:
        values = df[column].dropna().astype(str).head(250)
        if values.empty:
            continue
        separator_hits = values.apply(lambda value: any(separator in value for separator in MULTI_VALUE_SEPARATORS))
        if separator_hits.mean() < 0.15:
            continue
        split_lengths = []
        for value in values[separator_hits].head(100):
            parts = re.split(r"[,;|]", value)
            split_lengths.append(len([part.strip() for part in parts if part.strip()]))
        if split_lengths and sum(split_lengths) / len(split_lengths) >= 1.5:
            multi_value_columns.append(column)
    return multi_value_columns


def detect_sensitive_columns(df: pd.DataFrame, unique_counts: dict) -> dict[str, str]:
    sensitive = {}
    row_count = max(len(df), 1)
    for column in df.columns:
        normalized = _normalize(column)
        values = df[column].dropna().astype(str).str.strip()
        sample = values.head(250)
        if sample.empty:
            continue

        email_rate = sample.apply(lambda value: bool(EMAIL_RE.match(value))).mean()
        phone_rate = sample.apply(lambda value: bool(PHONE_RE.search(value))).mean()
        unique_ratio = unique_counts.get(column, 0) / row_count

        if email_rate >= 0.5 or any(token in normalized for token in SENSITIVE_EMAIL_TOKENS):
            sensitive[column] = "email"
        elif phone_rate >= 0.5 or any(token in normalized for token in SENSITIVE_PHONE_TOKENS):
            sensitive[column] = "phone"
        elif normalized in SENSITIVE_NAME_TOKENS or (
            "name" in normalized and unique_ratio >= 0.4 and not any(term in normalized for term in ["category", "type"])
        ):
            sensitive[column] = "name"
    return sensitive


def redact_sensitive_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    return "[REDACTED]"


def redacted_preview(df: pd.DataFrame, sensitive_columns: dict[str, str]) -> list[dict]:
    preview = df.head(10).copy()
    for column in sensitive_columns:
        if column in preview.columns:
            preview[column] = preview[column].apply(redact_sensitive_value)
    return preview.to_dict(orient="records")


def infer_logical_types(
    df: pd.DataFrame,
    date_columns: list[str],
    id_columns: list[str],
    multi_value_columns: list[str],
    sensitive_columns: dict[str, str],
) -> dict[str, str]:
    logical_types = {}
    row_count = max(len(df), 1)
    for column in df.columns:
        unique_count = int(df[column].nunique(dropna=True))
        unique_ratio = unique_count / row_count
        if column in sensitive_columns:
            logical_types[column] = "sensitive_identifier"
        elif column in id_columns:
            logical_types[column] = "identifier"
        elif column in date_columns:
            logical_types[column] = "datetime"
        elif column in multi_value_columns:
            logical_types[column] = "multi_value_categorical"
        elif pd.api.types.is_numeric_dtype(df[column]):
            logical_types[column] = "categorical_numeric" if unique_count <= min(20, max(10, row_count * 0.05)) else "numeric"
        elif unique_ratio > 0.6 and unique_count > 30:
            logical_types[column] = "text"
        else:
            logical_types[column] = "categorical"
    return logical_types


def infer_semantic_profile(profile: dict) -> dict:
    semantic = {}
    identifier_columns = set(profile.get("possible_id_columns", []))
    sensitive_columns = set(profile.get("sensitive_columns", {}).keys())
    multi_value_columns = set(profile.get("multi_value_columns", []))
    logical_types = profile.get("logical_types", {})
    for column in profile["column_names"]:
        normalized = _normalize(column)
        roles = []
        aliases = {normalized, column, normalized.replace(" ", "")}
        tokens = _tokenize(column)
        if len(tokens) > 1:
            aliases.update(tokens)
        logical_type = logical_types.get(column)
        if logical_type == "numeric":
            roles.append("measure")
        if logical_type in {"categorical", "categorical_numeric", "multi_value_categorical"}:
            roles.append("dimension")
        if logical_type == "datetime":
            roles.append("date")
        if column in identifier_columns:
            roles.append("identifier")
        if column in sensitive_columns:
            roles.extend(["sensitive", "identifier"])
        if column in multi_value_columns:
            roles.append("multi_value")
        if logical_type == "text":
            roles.append("text")
        semantic[column] = {
            "roles": list(dict.fromkeys(roles)),
            "aliases": sorted(alias for alias in aliases if alias),
            "logical_type": logical_type,
        }
    return semantic


def detect_identifier_columns(df: pd.DataFrame, unique_counts: dict) -> list[str]:
    row_count = max(len(df), 1)
    identifiers = []
    for column in df.columns:
        normalized = _normalize(column).strip()
        unique_count = unique_counts.get(column, 0)
        unique_ratio = unique_count / row_count
        name_suggests_id = normalized == "id" or normalized.endswith(" id") or normalized.endswith("id") or "identifier" in normalized
        almost_all_unique = unique_ratio >= 0.98 and row_count >= 20
        monotonic_numeric = pd.api.types.is_numeric_dtype(df[column]) and df[column].dropna().is_monotonic_increasing
        if name_suggests_id or (almost_all_unique and monotonic_numeric):
            identifiers.append(column)
    return identifiers


def build_data_quality_warnings(profile: dict) -> list[str]:
    warnings = []
    sensitive_columns = profile.get("sensitive_columns", {})
    if sensitive_columns:
        warnings.append(
            "Sensitive columns detected and redacted from AI context: "
            f"{', '.join(list(sensitive_columns.keys())[:5])}."
        )
    id_columns = profile.get("possible_id_columns", [])
    if id_columns:
        warnings.append(
            f"Possible identifier columns detected: {', '.join(id_columns[:5])}. These are useful for lookup but usually not for distribution charts."
        )
    high_missing = [
        column
        for column, pct in profile.get("missing_value_percentage", {}).items()
        if isinstance(pct, (int, float)) and pct >= 30
    ]
    if high_missing:
        warnings.append(f"Columns with high missing values may need caution: {', '.join(high_missing[:5])}.")
    multi_value = profile.get("multi_value_columns", [])
    if multi_value:
        warnings.append(f"Multi-value categorical columns detected: {', '.join(multi_value[:5])}. The agent can split these for grouped analysis.")
    return warnings[:4]


def clean_json(value: Any):
    if isinstance(value, dict):
        return {str(key): clean_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clean_json(item) for item in value]
    if not isinstance(value, (list, dict)) and pd.isna(value):
        return None
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def detect_date_columns(df: pd.DataFrame) -> list[str]:
    date_columns = []
    for column in df.columns:
        sample = df[column].dropna().astype(str).head(25)
        if sample.empty:
            continue
        parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
        if parsed.notna().mean() >= 0.8:
            date_columns.append(column)
    return date_columns


def profile_dataset(df: pd.DataFrame, metadata: dict | None = None) -> dict:
    numeric_df = df.select_dtypes(include="number")
    categorical_df = df.select_dtypes(exclude="number")
    missing_percent = (df.isna().mean() * 100).round(2).to_dict()
    unique_counts = df.nunique(dropna=True).to_dict()
    date_columns = detect_date_columns(df)
    possible_id_columns = detect_identifier_columns(df, unique_counts)
    sensitive_columns = detect_sensitive_columns(df, unique_counts)
    multi_value_columns = detect_multi_value_columns(df)
    logical_types = infer_logical_types(df, date_columns, possible_id_columns, multi_value_columns, sensitive_columns)

    numeric_summary = numeric_df.describe().round(2).to_dict() if not numeric_df.empty else {}
    categorical_summary = {}
    for column in categorical_df.columns:
        values = categorical_df[column].dropna().astype(str)
        if column in sensitive_columns:
            categorical_summary[column] = {
                "top_values": {"[REDACTED]": int(min(len(values), 5))} if len(values) else {},
                "unique": int(values.nunique()),
                "redacted": True,
            }
            continue
        categorical_summary[column] = {
            "top_values": values.value_counts().head(5).to_dict(),
            "unique": int(values.nunique()),
        }

    payload = {
            "row_count": int(len(df)),
            "column_count": int(len(df.columns)),
            "column_names": list(df.columns),
            "data_types": {column: str(dtype) for column, dtype in df.dtypes.items()},
            "missing_value_percentage": missing_percent,
            "unique_counts": unique_counts,
            "possible_id_columns": possible_id_columns,
            "sensitive_columns": sensitive_columns,
            "multi_value_columns": multi_value_columns,
            "logical_types": logical_types,
            "numeric_summary_statistics": numeric_summary,
            "categorical_summaries": categorical_summary,
            "date_columns": date_columns,
            "dataset_metadata": metadata or {},
            "preview": redacted_preview(df, sensitive_columns),
        }
    payload["semantic_profile"] = infer_semantic_profile(payload)
    payload["data_quality_warnings"] = build_data_quality_warnings(payload)
    return clean_json(payload)
