from aiogram import Bot, Dispatcher, executor
import os
from app.handlers import start, admin, user_search

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Register handlers
start.register(dp)
admin.register(dp)
user_search.register(dp)

def run_bot():
    executor.start_polling(dp, skip_updates=True)
