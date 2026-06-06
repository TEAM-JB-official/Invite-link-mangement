from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import owner_or_superadmin_required, log_command

@log_command
@owner_or_superadmin_required
async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    admin_list = await db.admins.find().to_list(None)
    text = "👥 *Admin List*\n\n"
    for admin in admin_list:
        user = await db.users.find_one({"user_id": admin["user_id"]})
        name = user["first_name"] if user else str(admin["user_id"])
        text += f"- {name} ({admin['role']})\n"
    
    keyboard = [[InlineKeyboardButton("Add Admin", callback_data="add_admin")]]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
