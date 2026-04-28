import sqlite3
from contextlib import contextmanager

from app.config import DATABASE_PATH


@contextmanager
def get_db():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db():
    with get_db() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              email TEXT UNIQUE NOT NULL,
              password_hash TEXT NOT NULL,
              created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
              id TEXT PRIMARY KEY,
              user_id INTEGER NOT NULL,
              share_id TEXT UNIQUE NOT NULL,
              title TEXT NOT NULL,
              dataset_metadata TEXT NOT NULL,
              question TEXT NOT NULL,
              chart_type TEXT NOT NULL,
              chart_config TEXT NOT NULL,
              insight TEXT NOT NULL,
              created_at TEXT DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS rag_chunks (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              dataset_id TEXT NOT NULL,
              chunk_type TEXT NOT NULL,
              title TEXT NOT NULL,
              content TEXT NOT NULL,
              embedding TEXT,
              created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.execute("CREATE INDEX IF NOT EXISTS idx_rag_chunks_dataset ON rag_chunks(dataset_id)")
