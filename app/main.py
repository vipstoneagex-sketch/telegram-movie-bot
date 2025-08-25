from pyrogram import Client
from app.config import API_ID, API_HASH, BOT_TOKEN
from app.handlers import start, admin, user_search, callbacks, errors

app = Client("movie_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Register handlers
start.register(app)
admin.register(app)
user_search.register(app)
callbacks.register(app)
errors.register(app)

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()