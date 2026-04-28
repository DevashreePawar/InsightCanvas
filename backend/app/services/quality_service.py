import re


def normalize_text(value: str | None) -> str:
    split_camel = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", value or "")
    return re.sub(r"[^a-z0-9]+", " ", split_camel.lower()).strip()


def is_identifier_column(column: str | None, profile: dict) -> bool:
    if not column:
        return False
    return column in set(profile.get("possible_id_columns", []))


def is_sensitive_column(column: str | None, profile: dict) -> bool:
    if not column:
        return False
    return column in set(profile.get("sensitive_columns", {}).keys())


def mentioned_columns(question: str, columns: list[str]) -> list[str]:
    normalized_question = f" {normalize_text(question)} "
    matches = []
    for column in columns:
        normalized_column = normalize_text(column)
        aliases = {normalized_column}
        compact = normalized_column.replace(" ", "")
        if compact.endswith("id"):
            aliases.add(compact[:-2])
            aliases.add(f"{compact[:-2]} id")
        for alias in aliases:
            if alias and f" {alias} " in normalized_question:
                matches.append(column)
                break
    return matches


def alternative_questions(profile: dict) -> list[str]:
    id_columns = set(profile.get("possible_id_columns", []))
    sensitive_columns = set(profile.get("sensitive_columns", {}).keys())
    excluded_columns = id_columns | sensitive_columns
    data_types = profile.get("data_types", {})
    numeric = [
        column
        for column, dtype in data_types.items()
        if ("int" in dtype or "float" in dtype) and column not in excluded_columns
    ]
    categorical = [
        column
        for column in profile.get("column_names", [])
        if column not in numeric and column not in excluded_columns
    ]
    low_cardinality_numeric = [
        column
        for column in numeric
        if profile.get("unique_counts", {}).get(column, 999999) <= 20
    ]
    groupable = categorical + low_cardinality_numeric

    suggestions = []
    if groupable:
        suggestions.append(f"Show the count of records by {groupable[0]}")
    if numeric:
        suggestions.append(f"Show the distribution of {numeric[0]}")
    if groupable and numeric:
        suggestions.append(f"Compare average {numeric[0]} by {groupable[0]}")
    if len(numeric) >= 2:
        suggestions.append(f"What factors seem related to {numeric[0]}?")
    return list(dict.fromkeys(suggestions))[:3]


def identifier_prompt_warning(question: str, profile: dict, recommendation: dict) -> dict | None:
    id_columns = profile.get("possible_id_columns", [])
    if not id_columns:
        return None

    normalized_question = normalize_text(question)
    requested_distribution = any(word in normalized_question for word in ["distribution", "spread", "histogram", "count", "frequency"])
    mentioned_ids = mentioned_columns(question, id_columns)
    selected_id = recommendation.get("x_axis") if is_identifier_column(recommendation.get("x_axis"), profile) else None
    target = (mentioned_ids or ([selected_id] if selected_id else []))

    if not target or not requested_distribution:
        return None

    column = target[0]
    suggestions = alternative_questions(profile)
    return {
        "should_block_chart": True,
        "warning": (
            f"{column} looks like an identifier, so its distribution is not analytically meaningful. "
            "Identifier values usually exist to uniquely label rows rather than reveal trends."
        ),
        "suggested_alternatives": suggestions,
    }


def selected_identifier_warning(profile: dict, recommendation: dict) -> dict | None:
    selected = [
        column
        for column in [recommendation.get("x_axis"), recommendation.get("y_axis")]
        if is_identifier_column(column, profile)
    ]
    if not selected:
        return None
    column = selected[0]
    return {
        "should_block_chart": True,
        "warning": (
            f"{column} appears to be an identifier, so the agent will not use it as an analytical axis. "
            "A better analysis should use a meaningful category, date, or numeric measure."
        ),
        "suggested_alternatives": alternative_questions(profile),
    }


def sensitive_prompt_warning(question: str, profile: dict, recommendation: dict) -> dict | None:
    sensitive_columns = profile.get("sensitive_columns", {})
    if not sensitive_columns:
        return None
    mentioned_sensitive = mentioned_columns(question, list(sensitive_columns.keys()))
    selected_sensitive = [
        column
        for column in [recommendation.get("x_axis"), recommendation.get("y_axis")]
        if is_sensitive_column(column, profile)
    ]
    target = mentioned_sensitive or selected_sensitive
    if not target:
        return None

    column = target[0]
    pii_type = sensitive_columns.get(column, "sensitive data")
    return {
        "should_block_chart": True,
        "warning": (
            f"{column} appears to contain {pii_type} values. The agent redacts this column from AI context "
            "and will not use it as an analytical axis to protect privacy."
        ),
        "suggested_alternatives": alternative_questions(profile),
    }
