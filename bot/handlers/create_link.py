from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import require_verified, log_command
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

@log_command
@require_verified
async def create_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    groups = await db.groups.find().to_list(None)
    if not groups:
        await update.message.reply_text("❌ I'm not admin in any group yet. Add me as admin first.")
        return
    context.user_data["create_link_step"] = "group"
    keyboard = [[InlineKeyboardButton(g["title"], callback_data=f"creategroup_{g['group_id']}")] for g in groups]
    await update.message.reply_text("Select a group:", reply_markup=InlineKeyboardMarkup(keyboard))
