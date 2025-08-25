from pyrogram import Client, filters

def register(app: Client):
    @app.on_message(filters.command("start"))
    async def start_cmd(client, message):
        await message.reply_text("Hello! Send me a movie name to search.")