from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.helpers import create_invite_link

async def create_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = get_db()
    groups = await db.groups.find().to_list(None)
    if not groups:
        await update.message.reply_text("❌ I'm not admin in any group/channel yet. Add me as admin first.")
        return
    context.user_data["create_link_step"] = "group"
    keyboard = [[InlineKeyboardButton(g["title"], callback_data=f"creategroup_{g['group_id']}")] for g in groups]
    await update.message.reply_text("Select a chat:", reply_markup=InlineKeyboardMarkup(keyboard))
