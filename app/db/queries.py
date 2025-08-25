import json
import os
import sqlite3
from typing import Iterable, Optional, Tuple, List
from app.config import DATABASE
from app.logger import logger

def _connect() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

_CONN = None

def get_conn() -> sqlite3.Connection:
    global _CONN
    if _CONN is None:
        _CONN = _connect()
    return _CONN

def init_db():
    conn = get_conn()
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    logger.info("Database initialized at %s", DATABASE)

# Movies
def add_movie(title: str, year: str, file_id: str):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO movies(title, year, file_id) VALUES(?,?,?)",
        (title.strip(), (year or "").strip(), file_id.strip())
    )
    conn.commit()

def search_one_like(name_part: str) -> Optional[Tuple[str, str, str]]:
    conn = get_conn()
    cur = conn.execute(
        "SELECT file_id, title, year FROM movies WHERE title LIKE ? ORDER BY created_at DESC LIMIT 1",
        (f"%{name_part}%",)
    )
    row = cur.fetchone()
    return (row["file_id"], row["title"], row["year"]) if row else None

def search_many_like(name_part: str, limit: int = 10) -> List[Tuple[int, str, str]]:
    conn = get_conn()
    cur = conn.execute(
        "SELECT id, title, year FROM movies WHERE title LIKE ? ORDER BY title LIMIT ?",
        (f"%{name_part}%", limit)
    )
    return [(r["id"], r["title"], r["year"]) for r in cur.fetchall()]

# Settings
def set_setting(key: str, value: str):
    conn = get_conn()
    conn.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
    conn.commit()

def get_setting(key: str) -> Optional[str]:
    conn = get_conn()
    cur = conn.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = cur.fetchone()
    return row["value"] if row else None

# Junk words
def add_junk_word(word: str):
    if not word:
        return
    conn = get_conn()
    conn.execute("INSERT OR IGNORE INTO junk_words(word) VALUES(?)", (word.strip(),))
    conn.commit()

def remove_junk_word(word: str):
    conn = get_conn()
    conn.execute("DELETE FROM junk_words WHERE word=?", (word.strip(),))
    conn.commit()

def list_junk() -> List[str]:
    conn = get_conn()
    cur = conn.execute("SELECT word FROM junk_words ORDER BY word")
    return [r["word"] for r in cur.fetchall()]

# Pending actions (for rename flow)
def save_pending_action(user_id: int, chat_id: int, action: str, context: dict):
    conn = get_conn()
    conn.execute(
        "INSERT INTO pending_actions(user_id, chat_id, action, context) VALUES(?,?,?,?) "
        "ON CONFLICT(user_id, chat_id) DO UPDATE SET action=excluded.action, context=excluded.context",
        (user_id, chat_id, action, json.dumps(context))
    )
    conn.commit()

def get_pending_action(user_id: int, chat_id: int) -> Optional[dict]:
    conn = get_conn()
    cur = conn.execute(
        "SELECT user_id, chat_id, action, context FROM pending_actions WHERE user_id=? AND chat_id=?",
        (user_id, chat_id)
    )
    row = cur.fetchone()
    if not row:
        return None
    data = {"user_id": row["user_id"], "chat_id": row["chat_id"], "action": row["action"], "context": {}}
    try:
        data["context"] = json.loads(row["context"] or "{}")
    except Exception:
        data["context"] = {}
    return data

def clear_pending_action(user_id: int, chat_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM pending_actions WHERE user_id=? AND chat_id=?", (user_id, chat_id))
    conn.commit()
