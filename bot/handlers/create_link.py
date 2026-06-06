from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from bot.database.mongo import get_db
from bot.utils.decorators import require_verified, log_command
from bot.utils.helpers import can_create_link, get_max_allowed_days
from bot.config import NORMAL_MAX_DAYS, PREMIUM_MAX_DAYS, LOG_CHANNEL
import logging

logger = logging.getLogger(__name__)

@log_command
@require_verified
async def create_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = get_db()
    
    # Get groups where bot is admin
    groups = []
    async for group in db.groups.find():
        groups.append(group)
    
    if not groups:
        await update.message.reply_text("❌ I'm not admin in any group yet. Add me as admin first.")
        return
    
    # Store selection step in user_data
    context.user_data["create_link_step"] = "group"
    keyboard = []
    for g in groups:
        keyboard.append([InlineKeyboardButton(g["title"], callback_data=f"creategroup_{g['group_id']}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a group:", reply_markup=reply_markup)
