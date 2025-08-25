from pyrogram import Client, filters
from app.config import ADMIN_ID
from app.db.queries import add_junk_word, remove_junk_word, list_junk, set_setting, get_setting
from app.logger import logger

def admin_only(_, m):
    return bool(m.from_user and m.from_user.id == ADMIN_ID)

def register(app: Client):
    @app.on_message(filters.command("addjunk") & filters.create(admin_only))
    async def add_junk_cmd(_, m):
        if len(m.command) < 2:
            return await m.reply_text("Usage: /addjunk <word>")
        word = m.command[1].strip()
        add_junk_word(word)
        await m.reply_text(f"✅ Added junk word: `{word}`", quote=True)

    @app.on_message(filters.command("removejunk") & filters.create(admin_only))
    async def remove_junk_cmd(_, m):
        if len(m.command) < 2:
            return await m.reply_text("Usage: /removejunk <word>")
        word = m.command[1].strip()
        remove_junk_word(word)
        await m.reply_text(f"🗑️ Removed junk word: `{word}`", quote=True)

    @app.on_message(filters.command("listjunk") & filters.create(admin_only))
    async def list_junk_cmd(_, m):
        words = list_junk()
        if not words:
            return await m.reply_text("No junk words configured.")
        await m.reply_text("🧹 *Junk words:*\n" + ", ".join(f"`{w}`" for w in words))

    @app.on_message(filters.command("setconfidence") & filters.create(admin_only))
    async def set_confidence_cmd(_, m):
        if len(m.command) < 3:
            return await m.reply_text("Usage: /setconfidence <high> <low>")
        try:
            high = float(m.command[1])
            low = float(m.command[2])
        except Exception:
            return await m.reply_text("Both values must be numbers, e.g. /setconfidence 82 70")
        set_setting("high_conf", str(high))
        set_setting("low_conf", str(low))
        await m.reply_text(f"✅ Set thresholds: high={high} low={low}")

    @app.on_message(filters.command("setpromo") & filters.create(admin_only))
    async def set_promo_cmd(_, m):
        if len(m.command) < 2:
            return await m.reply_text("Usage: /setpromo <text>")
        text = m.text.split(" ", 1)[1]
        set_setting("promo_text", text)
        await m.reply_text("✅ Promo text updated.")

    logger.info("Admin handlers registered")
