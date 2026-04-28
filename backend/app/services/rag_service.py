import json
import logging
import math
import re
from typing import Any

from openai import OpenAI

from app.config import OPENAI_API_KEY
from app.database import get_db

logger = logging.getLogger(__name__)
EMBEDDING_MODEL = "text-embedding-3-small"


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9_]+", text.lower()) if len(token) > 2}


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def _embed(text: str) -> list[float] | None:
    if not OPENAI_API_KEY:
        return None
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=text[:8000])
        return response.data[0].embedding
    except Exception as exc:
        logger.warning("Embedding failed; keyword RAG will be used: %s", exc)
        return None


def _chunk(title: str, chunk_type: str, content: Any) -> dict:
    text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
    return {"title": title, "chunk_type": chunk_type, "content": text}


def build_dataset_chunks(profile: dict) -> list[dict]:
    chunks = [
        _chunk("Dataset metadata", "metadata", profile.get("dataset_metadata", {})),
        _chunk(
            "Column overview",
            "schema",
            {
                "columns": profile.get("column_names", []),
                "data_types": profile.get("data_types", {}),
                "date_columns": profile.get("date_columns", []),
                "semantic_profile": profile.get("semantic_profile", {}),
            },
        ),
        _chunk("Missing values", "quality", profile.get("missing_value_percentage", {})),
        _chunk("Unique counts", "quality", profile.get("unique_counts", {})),
        _chunk("Sample rows", "sample", profile.get("preview", [])),
    ]
    for column in profile.get("column_names", []):
        chunks.append(
            _chunk(
                f"Column: {column}",
                "column",
                {
                    "name": column,
                    "dtype": profile.get("data_types", {}).get(column),
                    "missing_pct": profile.get("missing_value_percentage", {}).get(column),
                    "unique_count": profile.get("unique_counts", {}).get(column),
                    "numeric_summary": profile.get("numeric_summary_statistics", {}).get(column),
                    "categorical_summary": profile.get("categorical_summaries", {}).get(column),
                    "semantic": profile.get("semantic_profile", {}).get(column),
                },
            )
        )
    return chunks


def index_dataset_context(dataset_id: str, profile: dict) -> None:
    chunks = build_dataset_chunks(profile)
    embeddings_available = bool(OPENAI_API_KEY)
    with get_db() as db:
        db.execute("DELETE FROM rag_chunks WHERE dataset_id = ?", (dataset_id,))
        for item in chunks:
            text = f"{item['title']}\n{item['content']}"
            embedding = _embed(text) if embeddings_available else None
            if embeddings_available and embedding is None:
                embeddings_available = False
            db.execute(
                """
                INSERT INTO rag_chunks (dataset_id, chunk_type, title, content, embedding)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    dataset_id,
                    item["chunk_type"],
                    item["title"],
                    item["content"],
                    json.dumps(embedding) if embedding else None,
                ),
            )


def retrieve_dataset_context(dataset_id: str, question: str, limit: int = 6) -> list[dict]:
    with get_db() as db:
        rows = db.execute("SELECT chunk_type, title, content, embedding FROM rag_chunks WHERE dataset_id = ?", (dataset_id,)).fetchall()
    if not rows:
        return []

    query_embedding = _embed(question)
    query_tokens = _tokenize(question)
    scored = []
    for row in rows:
        content = row["content"]
        keyword_score = len(query_tokens & _tokenize(f"{row['title']} {content}"))
        vector_score = 0.0
        if query_embedding and row["embedding"]:
            vector_score = _cosine(query_embedding, json.loads(row["embedding"]))
        score = vector_score + keyword_score * 0.15
        scored.append((score, row))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        {
            "type": row["chunk_type"],
            "title": row["title"],
            "content": row["content"],
            "score": round(score, 4),
        }
        for score, row in scored[:limit]
    ]
