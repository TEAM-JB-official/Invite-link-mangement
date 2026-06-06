from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import admin_required, log_command

@log_command
@admin_required
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Set Welcome Message", callback_data="set_welcome")],
        [InlineKeyboardButton("Set Log Channel", callback_data="set_log_channel")],
        [InlineKeyboardButton("View Current Settings", callback_data="view_settings")],
    ]
    await update.message.reply_text("⚙️ *Settings Menu*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
