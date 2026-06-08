from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.config import OWNER_ID
from bot.utils.decorators import log_command

@log_command
async def create_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Start the interactive flow to create a custom invite link (owner only).
    """
    user_id = update.effective_user.id

    # Only owner can use this command
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ Only the bot owner can create custom invite links.")
        return

    db = get_db()
    groups = await db.groups.find().to_list(None)
    if not groups:
        await update.message.reply_text(
            "❌ I'm not admin in any group/channel yet. "
            "Add me as admin and use /addgroup or /addgroups to register the chat."
        )
        return

    context.user_data["create_link_step"] = "group"
    keyboard = []
    for g in groups:
        keyboard.append([InlineKeyboardButton(g["title"], callback_data=f"creategroup_{g['group_id']}")])

    await update.message.reply_text(
        "Select a group or channel:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
