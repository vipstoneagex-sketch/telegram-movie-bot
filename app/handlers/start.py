from pyrogram import Client, filters
from app.config import ADMIN_ID, HIGH_CONFIDENCE, LOW_CONFIDENCE

HELP_TEXT = (
    "🎬 *Movie Bot*\n\n"
    "• Send (or forward) a video/document: I’ll detect the movie title.\n"
    f"• Auto-save if confidence ≥ *{int(HIGH_CONFIDENCE)}%*; ask admin if between *{int(LOW_CONFIDENCE)}–{int(HIGH_CONFIDENCE)}%*.\n\n"
    "*Commands*\n"
    "• /get <name> — send stored file\n"
    "• /search <name> — search stored titles\n"
    "• /help — this help\n\n"
    "*Admin*\n"
    "• /addjunk <word>\n"
    "• /removejunk <word>\n"
    "• /listjunk\n"
    "• /setconfidence <high> <low>\n"
    "• /setpromo <text>\n"
)

def register(app: Client):
    @app.on_message(filters.command("start"))
    async def start_cmd(_, m):
        who = "admin" if m.from_user and m.from_user.id == ADMIN_ID else "there"
        await m.reply_text(f"Hello {who}! 👋\n\n" + HELP_TEXT, disable_web_page_preview=True)

    @app.on_message(filters.command("help"))
    async def help_cmd(_, m):
        await m.reply_text(HELP_TEXT, disable_web_page_preview=True)
