from pyrogram import Client
from app.logger import logger

def register(app: Client):
    @app.on_raw_update()
    async def _error_guard(_, __):
        # This is a placeholder to ensure the module is loaded; real errors are logged per-handler
        pass

    logger.info("Error handler stub registered")
