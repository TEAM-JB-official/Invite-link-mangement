import os
import sys
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
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

# Start health server in a background daemon thread
health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()

# Build bot application
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

# Run initialisation inside the bot's event loop using post_init
async def post_init(app: Application):
    await init_db()
    setup_scheduler(app.bot)
    logging.info("Bot initialised (MongoDB and scheduler ready)")

application.post_init = post_init

# Start polling (this will block and manage its own event loop)
if __name__ == "__main__":
    application.run_polling()
