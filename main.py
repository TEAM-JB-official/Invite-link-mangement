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
    TypeHandler,
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

# Initialize bot application
application = Application.builder().token(BOT_TOKEN).build()
application.add_error_handler(error_handler)

# Add handlers
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
    # Start the background scheduler (cleans expired links, etc.)
    setup_scheduler(application.bot)
    
    # Set up webhook (or use polling if WEBHOOK_URL not set)
    if WEBHOOK_URL:
        # Koyeb will provide the public URL automatically.
        # Use the PORT environment variable (Koyeb sets it to 8000).
        await application.bot.set_webhook(WEBHOOK_URL)
        logging.info(f"Webhook set to {WEBHOOK_URL}")
        
        # Run the aiohttp server that will handle both webhook and health checks
        app = web.Application()
        # Telegram webhook endpoint
        app.router.add_post(f"/{BOT_TOKEN}", application.process_update)
        # Health check endpoint
        app.router.add_get("/health", health_check)
        app.router.add_get("/", health_check)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        logging.info(f"Webhook server running on port {PORT}")
        
        # Keep the server running forever
        await asyncio.Event().wait()
    else:
        # Fallback to polling (for local testing)
        logging.info("No WEBHOOK_URL set, using polling...")
        await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
