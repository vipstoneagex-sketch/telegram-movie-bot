from flask import Flask
import threading
import logging
from app.bot import run_bot

# Initialize Flask app for Render health check
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

def start_bot():
    run_bot()

if __name__ == "__main__":
    logging.info("Starting Flask and bot threads...")
    # Start bot in a separate thread
    t = threading.Thread(target=start_bot)
    t.start()
    # Run Flask app to keep service alive
    app.run(host="0.0.0.0", port=5000)
