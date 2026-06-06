import os
import sys
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ChatJoinRequestHandler,
    CallbackQueryHandler,
)
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

# Build the bot application
application = Application.builder().token(BOT_TOKEN).build()
application.add_error_handler(error_handler)

# Add all handlers
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

async def health_check(request):
    return web.Response(text="OK")

async def main():
    await init_db()
    setup_scheduler(application.bot)
    
    if not WEBHOOK_URL:
        logging.error("WEBHOOK_URL is not set! Please set it in Koyeb environment variables.")
        return
    
    # Set webhook
    webhook_path = f"/{BOT_TOKEN}"
    full_webhook_url = f"{WEBHOOK_URL.rstrip('/')}{webhook_path}"
    await application.bot.set_webhook(full_webhook_url)
    logging.info(f"Webhook set to {full_webhook_url}")
    
    # Create aiohttp web server
    app = web.Application()
    # Telegram webhook endpoint
    app.router.add_post(webhook_path, application.process_update)
    # Health check endpoints
    app.router.add_get("/health", health_check)
    app.router.add_get("/", health_check)
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Webhook server running on port {PORT}")
    
    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
