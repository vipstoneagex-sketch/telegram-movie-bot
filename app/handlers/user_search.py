from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.config import ADMIN_ID, ALLOWED_CHAT_IDS
from app.db.queries import (
    add_movie, search_one_like, search_many_like, get_setting, save_pending_action,
)
from app.services.search import analyze_media_message
from app.services.imdb import tmdb_search_best
from app.logger import logger

def is_allowed_chat(chat_id: int) -> bool:
    return (not ALLOWED_CHAT_IDS) or (chat_id in ALLOWED_CHAT_IDS)

def register(app: Client):
    @app.on_message((filters.video | filters.document))
    async def on_media(_, m):
        # Allow anyone to upload in allowed chats; only ADMIN gets prompts/confirm.
        if not is_allowed_chat(m.chat.id):
            return

        filename = m.document.file_name if m.document else m.video.file_name
        caption = m.caption or ""
        file_id = (m.video.file_id if m.video else m.document.file_id)

        analysis = analyze_media_message(filename, caption)
        # Query TMDB with our best guess
        tmdb_best = tmdb_search_best(analysis["query"])
        if not tmdb_best:
            return await m.reply_text("❌ Could not identify this movie on TMDB.")

        title = tmdb_best["title"]
        year = tmdb_best.get("year", "")
        score = tmdb_best["score"]

        # Load current thresholds (settings override env)
        try:
            high = float(get_setting("high_conf") or 82)
            low = float(get_setting("low_conf") or 70)
        except Exception:
            high, low = 82, 70

        if score >= high:
            add_movie(title=title, year=year, file_id=file_id)
            await m.reply_text(f"✅ Saved: *{title}* ({year}) — {int(score)}%", disable_web_page_preview=True)
        elif score >= low:
            # Ask admin to confirm; if in group, @mention admin can't DM automatically,
            # so we reply in place with inline buttons (only admin should act).
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm & Save", callback_data=f"confirm|{title}|{year}|{file_id}")],
                [InlineKeyboardButton("✏️ Rename", callback_data=f"rename|{file_id}")],
                [InlineKeyboardButton("❌ Ignore", callback_data=f"ignore|{file_id}")]
            ])
            await m.reply_text(
                f"🤔 *Low confidence* ({int(score)}%). Detected: *{title}* ({year}).\n"
                f"Admin, please choose an action:",
                reply_markup=kb, disable_web_page_preview=True
            )
            # For rename flow, remember which file we’re renaming
            save_pending_action(user_id=ADMIN_ID, chat_id=m.chat.id, action="await_rename", context={"file_id": file_id})
        else:
            await m.reply_text(f"⚠️ Confidence too low ({int(score)}%). Admin can rename via the button.")

    @app.on_message(filters.command("get"))
    async def get_cmd(_, m):
        if len(m.command) < 2:
            return await m.reply_text("Usage: /get <movie name>")
        q = m.text.split(" ", 1)[1]
        row = search_one_like(q)
        if not row:
            return await m.reply_text("❌ Not found.")
        file_id, title, year = row
        promo = get_setting("promo_text") or ""
        caption = f"🎬 *{title}* ({year})"
        if promo:
            caption += f"\n\n{promo}"
        # Try sending as video first; fallback to document
        try:
            await m.reply_video(file_id, caption=caption)
        except Exception:
            await m.reply_document(file_id, caption=caption)

    @app.on_message(filters.command("search"))
    async def search_cmd(_, m):
        if len(m.command) < 2:
            return await m.reply_text("Usage: /search <name part>")
        q = m.text.split(" ", 1)[1]
        rows = search_many_like(q, limit=10)
        if not rows:
            return await m.reply_text("❌ No matches.")
        lines = [f"• *{t}* ({y})" for (_, t, y) in rows]
        await m.reply_text("Results:\n" + "\n".join(lines), disable_web_page_preview=True)

    logger.info("User handlers registered")
