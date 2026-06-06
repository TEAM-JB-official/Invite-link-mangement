import os
import sys
import logging
import asyncio
from aiohttp import web
from telegram.ext import (
    Application,
    CommandHandler,
    ChatJoinRequestHandler,
    CallbackQueryHandler,
)
from bot.config import BOT_TOKEN, PORT
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

application = Application.builder().token(BOT_TOKEN).build()
application.add_error_handler(error_handler)

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

async def run_web_server():
    """Simple aiohttp server for health checks"""
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    logging.info(f"Health check server running on port {PORT}")
    # Keep the server alive forever
    await asyncio.Event().wait()

async def main():
    await init_db()
    setup_scheduler(application.bot)
    
    # Start bot polling and health check server concurrently
    polling_task = asyncio.create_task(application.run_polling())
    web_task = asyncio.create_task(run_web_server())
    
    # Wait for either to finish (they run forever)
    await asyncio.gather(polling_task, web_task)

if __name__ == "__main__":
    asyncio.run(main())
