from pyrogram import Client, filters
from app.config import ADMIN_ID
from app.db.queries import add_movie, get_pending_action, clear_pending_action, get_setting
from app.logger import logger

def register(app: Client):
    @app.on_callback_query(filters.create(lambda _, cq: cq.from_user and cq.from_user.id == ADMIN_ID))
    async def on_cb(_, cq):
        data = cq.data or ""
        try:
            action, *rest = data.split("|")
        except Exception:
            return await cq.answer("Bad data", show_alert=True)

        if action == "confirm":
            try:
                title, year, file_id = rest
            except Exception:
                return await cq.answer("Missing data", show_alert=True)
            add_movie(title=title, year=year, file_id=file_id)
            await cq.message.edit_text(f"✅ Saved: *{title}* ({year})")
            await cq.answer("Saved")
            clear_pending_action(ADMIN_ID, cq.message.chat.id)

        elif action == "rename":
            # Set state to await next text message from admin as the new title
            await cq.message.edit_text("✏️ Send the correct *movie title* now (optionally include year in parentheses).")
            await cq.answer("Waiting for title…")

        elif action == "ignore":
            await cq.message.edit_text("❌ Ignored.")
            await cq.answer("Ignored")
            clear_pending_action(ADMIN_ID, cq.message.chat.id)

    # Catch the manual rename text after pressing Rename
    @app.on_message(filters.text & filters.create(lambda _, m: m.from_user and m.from_user.id == ADMIN_ID))
    async def on_admin_text(_, m):
        state = get_pending_action(ADMIN_ID, m.chat.id)
        if not state or state.get("action") != "await_rename":
            return  # Not in rename flow

        file_id = state["context"].get("file_id")
        if not file_id:
            return

        # Parse title + optional year like "Spider-Man (2017)"
        text = m.text.strip()
        title = text
        year = ""
        # crude parse for year in parentheses
        import re
        mobj = re.search(r"\((\d{4})\)", text)
        if mobj:
            year = mobj.group(1)
            title = re.sub(r"\(\d{4}\)", "", text).strip()

        add_movie(title=title, year=year, file_id=file_id)
        clear_pending_action(ADMIN_ID, m.chat.id)

        promo = get_setting("promo_text") or ""
        cap = f"✅ Saved: *{title}* ({year})"
        if promo:
            cap += f"\n\n{promo}"

        await m.reply_text(cap)
