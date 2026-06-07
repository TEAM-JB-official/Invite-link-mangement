import os
import sys
import logging
import threading
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import (
    Application,
    CommandHandler,
    ChatJoinRequestHandler,
    CallbackQueryHandler,
    MessageHandler, filters
)
from bot.config import BOT_TOKEN, PORT
from bot.database.mongo import init_db
from bot.handlers import (
    start, create_link, active_links, revoke_link, revoke_all,
    stats, settings, admins, backup, restore, dashboard, join_request, callback_handlers
)
from bot.handlers.set_default_link import set_default_link
from bot.handlers.message_handlers import handle_custom_input
from bot.handlers.addgroup import addgroup
from bot.middleware.error_handler import error_handler
from bot.scheduler.jobs import setup_scheduler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/health'):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, format, *args):
        pass

def run_health_server():
    server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
    logging.info(f"Health check server running on port {PORT} (background thread)")
    server.serve_forever()

# Start health check in background thread
health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()

# Build bot application
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
application.add_handler(CommandHandler("addgroup", addgroup))
application.add_handler(CommandHandler("setdefaultlink", set_default_link))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_input))
application.add_handler(ChatJoinRequestHandler(join_request))
application.add_handler(CallbackQueryHandler(callback_handlers))

async def post_init(app: Application):
    await init_db()
    # Delete webhook and wait 5 seconds for Telegram to close old connections
    await app.bot.delete_webhook(drop_pending_updates=True)
    logging.info("Deleted webhook, waiting 5 seconds for Telegram to release old polling connections...")
    await asyncio.sleep(5)
    setup_scheduler(app.bot)
    logging.info("Bot initialised")

application.post_init = post_init

if __name__ == "__main__":
    # Start polling with drop_pending_updates=True and a shorter read timeout
    application.run_polling(drop_pending_updates=True, read_timeout=30)
