from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, get_bot_setting, get_default_links
from bot.config import OWNER_IDS, LOG_CHANNEL
from bot.utils.helpers import register_user, create_invite_link, revoke_link_by_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Silent start – does NOT reply to users.
    Only registers the user and optionally creates links if needed.
    """
    user = update.effective_user
    db = get_db()
    
    # Register user if not exists
    await register_user(user.id, user.username, user.first_name)

    # Owner – send a brief message (only for owners)
    if user.id in OWNER_IDS:
        await update.message.reply_text(
            f"Welcome back, {user.first_name} (Owner).\n"
            "Use /dashboard for admin panel."
        )
        return

    # For regular users: DO NOTHING (silent)
    # Links will be sent when they join via ChatMemberHandler
    return
