import os
import threading
import logging
from flask import Flask
from pyrogram import Client
from app.config import API_ID, API_HASH, BOT_TOKEN
from app.db.queries import init_db
from app.handlers import start, admin, user_search, callbacks, errors
from app.logger import logger

# Initialize Flask app for Render health check
app = Flask(__name__)

@app.route('/')
def home():
    return "Movie Bot is running!", 200

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

def create_bot():
    """Create and configure the Pyrogram bot"""
    bot_app = Client(
        "movie_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        workdir="."
    )
    
    # Register all handlers
    start.register(bot_app)
    admin.register(bot_app)
    user_search.register(bot_app)
    callbacks.register(bot_app)
    errors.register(bot_app)
    
    return bot_app

def start_bot():
    """Initialize database and start the bot"""
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
        
        # Create and start bot
        bot_app = create_bot()
        logger.info("Starting Telegram bot...")
        bot_app.run()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    # Validate required environment variables
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        logger.error("Missing required environment variables: API_ID, API_HASH, BOT_TOKEN")
        exit(1)
    
    logger.info("Starting application...")
    
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Start Flask app to keep Render service alive
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)