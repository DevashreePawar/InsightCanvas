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
              auth_provider TEXT DEFAULT 'local',
              google_sub TEXT UNIQUE,
              created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        existing_columns = {row["name"] for row in db.execute("PRAGMA table_info(users)").fetchall()}
        if "auth_provider" not in existing_columns:
            db.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'local'")
        if "google_sub" not in existing_columns:
            db.execute("ALTER TABLE users ADD COLUMN google_sub TEXT")
        db.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_google_sub ON users(google_sub)")
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
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS analytics_events (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              visitor_id TEXT NOT NULL,
              event_name TEXT NOT NULL,
              page TEXT,
              metadata TEXT,
              created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.execute("CREATE INDEX IF NOT EXISTS idx_analytics_events_name ON analytics_events(event_name)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_analytics_events_created ON analytics_events(created_at)")
