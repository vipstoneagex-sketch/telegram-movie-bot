import os
from dotenv import load_dotenv

# Load from .env if present (local dev). In hosted envs, real env vars take precedence.
load_dotenv()

def _int(v, default):
    try:
        return int(v) if v else default
    except (ValueError, TypeError):
        return default

def _float(v, default):
    try:
        return float(v) if v else default
    except (ValueError, TypeError):
        return default

# Required Telegram API credentials
API_ID = _int(os.getenv("API_ID"), 0)
API_HASH = os.getenv("API_HASH", "").strip()
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "").strip()
ADMIN_ID = _int(os.getenv("ADMIN_ID"), 0)

# Optional settings
PROMO_TEXT = os.getenv("PROMO_TEXT", "").strip()

# Optional: comma-separated IDs for chats where uploads are allowed
ALLOWED_CHAT_IDS = []
_raw_chats = os.getenv("ALLOWED_CHAT_IDS", "").strip()
if _raw_chats:
    for chat_id in _raw_chats.split(","):
        chat_id = chat_id.strip()
        if chat_id:
            try:
                ALLOWED_CHAT_IDS.append(int(chat_id))
            except (ValueError, TypeError):
                pass

# Confidence thresholds
HIGH_CONFIDENCE = _float(os.getenv("HIGH_CONFIDENCE"), 82.0)
LOW_CONFIDENCE = _float(os.getenv("LOW_CONFIDENCE"), 70.0)

# Database path - use /tmp for Render since filesystem is ephemeral
if os.getenv("RENDER"):
    # On Render, use /tmp which is writable
    DATABASE = "/tmp/movies.db"
else:
    # Local development or other hosting
    DATABASE = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "db", "movies.db"))

# Validate required settings
def validate_config():
    missing = []
    if not API_ID:
        missing.append("API_ID")
    if not API_HASH:
        missing.append("API_HASH") 
    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")
    if not ADMIN_ID:
        missing.append("ADMIN_ID")
    
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

if __name__ == "__main__":
    validate_config()
    print("Configuration validated successfully!")