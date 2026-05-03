import json
from datetime import datetime, timedelta
from typing import Any

from app.database import get_db

ALLOWED_METADATA_KEYS = {
    "mode",
    "file_type",
    "source",
    "chart_count",
    "status",
    "error_type",
    "format",
}


def _clean_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    cleaned = {}
    for key, value in (metadata or {}).items():
        if key not in ALLOWED_METADATA_KEYS:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            cleaned[key] = value
    return cleaned


def record_event(visitor_id: str, event_name: str, page: str | None = None, metadata: dict[str, Any] | None = None) -> dict:
    safe_metadata = _clean_metadata(metadata or {})
    with get_db() as db:
        db.execute(
            """
            INSERT INTO analytics_events (visitor_id, event_name, page, metadata)
            VALUES (?, ?, ?, ?)
            """,
            (visitor_id, event_name, page, json.dumps(safe_metadata)),
        )
    return {"status": "recorded"}


def analytics_summary(days: int = 30) -> dict:
    since = datetime.utcnow() - timedelta(days=max(1, min(days, 365)))
    since_text = since.strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as db:
        totals = db.execute(
            """
            SELECT
              COUNT(*) AS total_events,
              COUNT(DISTINCT visitor_id) AS unique_visitors,
              MIN(created_at) AS first_seen,
              MAX(created_at) AS last_seen
            FROM analytics_events
            WHERE created_at >= ?
            """,
            (since_text,),
        ).fetchone()
        by_event = db.execute(
            """
            SELECT event_name, COUNT(*) AS count
            FROM analytics_events
            WHERE created_at >= ?
            GROUP BY event_name
            ORDER BY count DESC, event_name ASC
            """,
            (since_text,),
        ).fetchall()
        by_page = db.execute(
            """
            SELECT COALESCE(page, 'unknown') AS page, COUNT(*) AS count
            FROM analytics_events
            WHERE created_at >= ?
            GROUP BY page
            ORDER BY count DESC, page ASC
            """,
            (since_text,),
        ).fetchall()
        recent = db.execute(
            """
            SELECT event_name, page, metadata, created_at
            FROM analytics_events
            WHERE created_at >= ?
            ORDER BY created_at DESC
            LIMIT 20
            """,
            (since_text,),
        ).fetchall()

    return {
        "window_days": days,
        "total_events": int(totals["total_events"] or 0),
        "unique_visitors": int(totals["unique_visitors"] or 0),
        "dashboard_views": next((int(row["count"]) for row in by_event if row["event_name"] == "dashboard_view"), 0),
        "analysis_runs": next((int(row["count"]) for row in by_event if row["event_name"] == "analysis_run"), 0),
        "uploads": next((int(row["count"]) for row in by_event if row["event_name"] == "dataset_uploaded"), 0),
        "first_seen": totals["first_seen"],
        "last_seen": totals["last_seen"],
        "events_by_name": [{"event_name": row["event_name"], "count": int(row["count"])} for row in by_event],
        "events_by_page": [{"page": row["page"], "count": int(row["count"])} for row in by_page],
        "recent_events": [
            {
                "event_name": row["event_name"],
                "page": row["page"],
                "metadata": json.loads(row["metadata"] or "{}"),
                "created_at": row["created_at"],
            }
            for row in recent
        ],
    }
