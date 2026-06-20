import os
import sys
import logging
import threading
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram.ext import (
    Application,
    CommandHandler,
    ChatJoinRequestHandler,      # KEPT for logging, but NO auto-approval
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ChatMemberHandler
)
from bot.config import BOT_TOKEN, PORT
from bot.database.mongo import init_db
from bot.handlers import (
    start, create_link, active_links, revoke_link, revoke_all,
    stats, backup, restore, dashboard, join_request, callback_handlers
)
from bot.handlers.help import help_command
from bot.handlers.set_default_link import set_default_link
from bot.handlers.message_handlers import handle_custom_input
from bot.handlers.addgroup import addgroup
from bot.handlers.settings import settings, settings_callback, handle_settings_text
from bot.handlers.admins import admins, admins_callback, handle_admin_text
from bot.handlers.setlogchannel import setlogchannel
from bot.handlers.addadmin import addadmin
from bot.handlers.setwelcome import setwelcome
from bot.middleware.error_handler import error_handler
from bot.scheduler.jobs import setup_scheduler
from bot.handlers.activelinkmode import activelinkmode
from bot.handlers.setactivelink import setactivelink
from bot.handlers.defaultlinkstatus import defaultlinkstatus
from bot.handlers.listlinks import listlinks
from bot.handlers.togglewelcome import togglewelcome
from bot.handlers.channel_join import handle_new_chat_member

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/health'):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_HEAD(self):
        if self.path in ('/', '/health'):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
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

# Command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
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
application.add_handler(CommandHandler("setlogchannel", setlogchannel))
application.add_handler(CommandHandler("addadmin", addadmin))
application.add_handler(CommandHandler("setwelcome", setwelcome))
application.add_handler(CommandHandler("setdefaultlink", set_default_link))
application.add_handler(CommandHandler("activelinkmode", activelinkmode))
application.add_handler(CommandHandler("setactivelink", setactivelink))
application.add_handler(CommandHandler("defaultlinkstatus", defaultlinkstatus))
application.add_handler(CommandHandler("listlinks", listlinks))
application.add_handler(CommandHandler("togglewelcome", togglewelcome))

# Message handlers for custom text input
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_input))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_settings_text))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_text))

# Join request handler - LOGS but does NOT auto-approve
application.add_handler(ChatJoinRequestHandler(join_request))

# Callback handler for inline keyboards
application.add_handler(CallbackQueryHandler(callback_handlers))

# Detect new members and send private links
application.add_handler(ChatMemberHandler(handle_new_chat_member, ChatMemberHandler.CHAT_MEMBER))

async def post_init(app: Application):
    await init_db()
    await app.bot.delete_webhook(drop_pending_updates=True)
    logging.info("Deleted webhook, waiting 5 seconds for Telegram to release old polling connections...")
    await asyncio.sleep(5)
    setup_scheduler(app.bot)
    logging.info("Bot initialised")

application.post_init = post_init

if __name__ == "__main__":
    application.run_polling(
        drop_pending_updates=True,
        read_timeout=30
)
