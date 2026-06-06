import asyncio
import logging
from aiohttp import web
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ChatJoinRequestHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from bot.config import BOT_TOKEN, PORT, WEBHOOK_URL
from bot.database.mongo import init_db
from bot.handlers import (
    start,
    create_link,
    active_links,
    revoke_link,
    revoke_all,
    stats,
    settings,
    admins,
    backup,
    restore,
    dashboard,
    join_request,
    callback_handlers,
)
from bot.middleware.error_handler import error_handler
from bot.middleware.logging_middleware import logging_middleware
from bot.scheduler.jobs import setup_scheduler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

async def health_check(request):
    return web.Response(text="OK")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Health check server running on port {PORT}")

async def main():
    await init_db()
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Middleware
    application.update_persistent_state(logging_middleware)
    
    # Command handlers
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
    
    # Join request handler
    application.add_handler(ChatJoinRequestHandler(join_request))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(callback_handlers))
    
    # Start background scheduler
    setup_scheduler(application.bot)
    
    # Start health web server
    await start_web_server()
    
    # Start bot
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
