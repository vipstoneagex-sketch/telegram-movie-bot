import os
import threading
import logging
import asyncio
import time
from flask import Flask, jsonify
from pyrogram import Client
from app.config import API_ID, API_HASH, BOT_TOKEN, ADMIN_ID
from app.db.queries import init_db
from app.handlers import start, admin, user_search, callbacks, errors
from app.logger import logger

# Global bot instance
bot_app = None
bot_status = {"running": False, "error": None, "start_time": None}

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    uptime = time.time() - bot_status.get("start_time", time.time()) if bot_status.get("start_time") else 0
    return jsonify({
        "status": "healthy",
        "bot_running": bot_status["running"],
        "uptime_seconds": int(uptime),
        "admin_id": ADMIN_ID,
        "error": bot_status["error"]
    }), 200

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/wake')
def wake():
    """Endpoint to wake up the service and ensure bot is running"""
    if not bot_status["running"] and bot_app:
        return jsonify({"message": "Bot restarting..."}), 200
    return jsonify({"message": "Bot is running"}), 200

def create_bot():
    """Create and configure the Pyrogram bot"""
    global bot_app
    try:
        bot_app = Client(
            "movie_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workdir="/tmp",
            sleep_threshold=0  # Disable sleep to keep connection alive
        )
        
        # Register all handlers
        start.register(bot_app)
        admin.register(bot_app)
        user_search.register(bot_app)
        callbacks.register(bot_app)
        errors.register(bot_app)
        
        return bot_app
    except Exception as e:
        logger.error(f"Failed to create bot: {e}")
        bot_status["error"] = str(e)
        return None

async def run_bot():
    """Run the bot with error handling and auto-restart"""
    global bot_app, bot_status
    
    while True:
        try:
            logger.info("Starting Telegram bot...")
            bot_status["start_time"] = time.time()
            
            if not bot_app:
                bot_app = create_bot()
            
            if bot_app:
                await bot_app.start()
                bot_status["running"] = True
                bot_status["error"] = None
                logger.info("Bot started successfully!")
                
                # Keep the bot running
                await bot_app.idle()
            else:
                logger.error("Failed to create bot instance")
                bot_status["error"] = "Failed to create bot instance"
                
        except Exception as e:
            logger.error(f"Bot error: {e}")
            bot_status["running"] = False
            bot_status["error"] = str(e)
            
            if bot_app:
                try:
                    await bot_app.stop()
                except:
                    pass
                bot_app = None
            
            # Wait before retry
            logger.info("Retrying in 30 seconds...")
            await asyncio.sleep(30)

def start_bot_thread():
    """Start bot in a new event loop"""
    try:
        # Initialize database first
        init_db()
        logger.info("Database initialized successfully")
        
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run bot
        loop.run_until_complete(run_bot())
    except Exception as e:
        logger.error(f"Bot thread error: {e}")
        bot_status["error"] = str(e)

if __name__ == "__main__":
    # Validate required environment variables
    if not all([API_ID, API_HASH, BOT_TOKEN]):
        logger.error("Missing required environment variables")
        exit(1)
    
    logger.info("Starting application...")
    
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot_thread, daemon=True)
    bot_thread.start()
    
    # Give bot time to start
    time.sleep(2)
    
    # Start Flask server (this MUST happen on main thread for Render)
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask server on port {port}")
    
    try:
        app.run(
            host="0.0.0.0", 
            port=port, 
            debug=False, 
            use_reloader=False,
            threaded=True
        )
    except Exception as e:
        logger.error(f"Flask server error: {e}")
        exit(1)