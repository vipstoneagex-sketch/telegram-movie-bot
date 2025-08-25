import os
from dotenv import load_dotenv

# Load from .env if present (local dev). In hosted envs, real env vars take precedence.
load_dotenv()

def _int(v, default):
    try:
        return int(v)
    except Exception:
        return default

def _float(v, default):
    try:
        return float(v)
    except Exception:
        return default

API_ID = _int(os.getenv("API_ID"), 0)
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
ADMIN_ID = _int(os.getenv("ADMIN_ID"), 0)
PROMO_TEXT = os.getenv("PROMO_TEXT", "")

# Optional: comma-separated IDs for chats where uploads are allowed
ALLOWED_CHAT_IDS = []
_raw_chats = os.getenv("ALLOWED_CHAT_IDS", "")
if _raw_chats.strip():
    for p in _raw_chats.split(","):
        p = p.strip()
        if p:
            try:
                ALLOWED_CHAT_IDS.append(int(p))
            except Exception:
                pass

HIGH_CONFIDENCE = _float(os.getenv("HIGH_CONFIDENCE"), 82.0)
LOW_CONFIDENCE = _float(os.getenv("LOW_CONFIDENCE"), 70.0)

# DB path (can be overridden by env DB_PATH, useful for volumes on hosting)
DATABASE = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "db", "movies.db"))
