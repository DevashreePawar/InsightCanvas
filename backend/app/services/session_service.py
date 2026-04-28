import json
import uuid

from fastapi import HTTPException

from app.database import get_db


def save_session(user_id: int, payload: dict) -> dict:
    session_id = str(uuid.uuid4())
    share_id = str(uuid.uuid4())[:12]
    chart_config = payload["chart_config"]
    with get_db() as db:
        db.execute(
            """
            INSERT INTO sessions (id, user_id, share_id, title, dataset_metadata, question, chart_type, chart_config, insight)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                user_id,
                share_id,
                payload["title"],
                json.dumps(payload["dataset_metadata"]),
                payload["question"],
                payload["chart_type"],
                chart_config if isinstance(chart_config, str) else json.dumps(chart_config),
                payload["insight"],
            ),
        )
    return get_session(user_id, session_id)


def _row_to_session(row) -> dict:
    chart_config = json.loads(row["chart_config"])
    return {
        "id": row["id"],
        "share_id": row["share_id"],
        "title": row["title"],
        "dataset_metadata": json.loads(row["dataset_metadata"]),
        "question": row["question"],
        "chart_type": row["chart_type"],
        "chart_config": chart_config,
        "insight": row["insight"],
        "created_at": row["created_at"],
    }


def list_sessions(user_id: int) -> list[dict]:
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM sessions WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    return [_row_to_session(row) for row in rows]


def get_session(user_id: int, session_id: str) -> dict:
    with get_db() as db:
        row = db.execute(
            "SELECT * FROM sessions WHERE user_id = ? AND id = ?",
            (user_id, session_id),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Session not found.")
    return _row_to_session(row)


def get_shared_session(share_id: str) -> dict:
    with get_db() as db:
        row = db.execute("SELECT * FROM sessions WHERE share_id = ?", (share_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Shared session not found.")
    return _row_to_session(row)


def delete_session(user_id: int, session_id: str):
    with get_db() as db:
        result = db.execute(
            "DELETE FROM sessions WHERE user_id = ? AND id = ?",
            (user_id, session_id),
        )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"ok": True}
