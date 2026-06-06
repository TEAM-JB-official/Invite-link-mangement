import sys
import os
import logging
import asyncio
import threading
from aiohttp import web
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ChatJoinRequestHandler,
    CallbackQueryHandler,
)

sys.path.insert(0, os.getcwd())

from bot.config import BOT_TOKEN, PORT, WEBHOOK_URL
from bot.database.mongo import init_db
from bot.handlers import (
    start, create_link, active_links, revoke_link, revoke_all,
    stats, settings, admins, backup, restore, dashboard, join_request, callback_handlers
)
from bot.middleware.error_handler import error_handler
from bot.scheduler.jobs import setup_scheduler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

async def health_check(request):
    return web.Response(text="OK")

def run_web_server():
    """Run aiohttp web server in a separate thread"""
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    # Use the PORT environment variable (default 8000)
    web.run_app(app, host="0.0.0.0", port=int(PORT), print=None)

async def main():
    # Initialize MongoDB
    await init_db()
    
    # Build the bot application
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_error_handler(error_handler)
    
    # Add all command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("create_link", create_link))
    application.add_handler(CommandHandler("active_links", active_links))
    application.add_handler(CommandHandler("revoke_link", revoke_link))
    application.add_handler(CommandHandler("revoke_all", revoke_all))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CommandHandler("admins", admins))
    application.add_handler(CommandHandler("backup", backup))
    application.add_handler(CommandHandler("restore", restore))
    application.add_handler(CommandHandler("dashboard", dashboard))
    application.add_handler(ChatJoinRequestHandler(join_request))
    application.add_handler(CallbackQueryHandler(callback_handlers))
    
    # Start background scheduler (cleans expired links, updates premium status)
    setup_scheduler(application.bot)
    
    # Start the health check web server in a separate daemon thread
    thread = threading.Thread(target=run_web_server, daemon=True)
    thread.start()
    logging.info(f"Health check server running on port {PORT} (in background thread)")
    
    # Start the bot (polling) – this will block the main thread
    if WEBHOOK_URL:
        await application.bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Webhook set to {WEBHOOK_URL}")
        await application.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=WEBHOOK_URL + "/" + BOT_TOKEN,
        )
    else:
        logging.info("Starting polling...")
        await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
