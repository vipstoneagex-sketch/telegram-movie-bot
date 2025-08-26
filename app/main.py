import os
import threading
import logging
import asyncio
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
        workdir="/tmp"  # Use /tmp on Render
    )
    
    # Register all handlers
    start.register(bot_app)
    admin.register(bot_app)
    user_search.register(bot_app)
    callbacks.register(bot_app)
    errors.register(bot_app)
    
    return bot_app

def start_flask():
    """Start Flask server in a separate thread"""
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

async def main():
    """Main async function to run the bot"""
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
        
        # Start Flask in a separate thread
        flask_thread = threading.Thread(target=start_flask, daemon=True)
        flask_thread.start()
        
        # Create and start bot in main thread
        bot_app = create_bot()
        logger.info("Starting Telegram bot...")
        await bot_app.start()
        logger.info("Bot started successfully!")
        
        # Keep the bot running
        await bot_app.idle()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise
    finally:
        if 'bot_app' in locals():
            await bot_app.stop()
            logger.info("Bot stopped")

if __name__ == "__main__":
    # Validate required environment variables
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        logger.error("Missing required environment variables: API_ID, API_HASH, BOT_TOKEN")
        exit(1)
    
    logger.info("Starting application...")
    
    # Run the main async function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        exit(1)