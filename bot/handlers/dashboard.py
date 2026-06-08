from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.config import OWNER_IDS   # list of owner IDs
from bot.utils.decorators import log_command

@log_command
async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = get_db()

    # Check if user is owner or admin
    if user_id not in OWNER_IDS:
        admin = await db.admins.find_one({"user_id": user_id})
        if not admin:
            await update.message.reply_text("❌ Admin privilege required to access the dashboard.")
            return

    keyboard = [
        [InlineKeyboardButton("➕ Create Link", callback_data="dashboard_create")],
        [InlineKeyboardButton("📋 Active Links", callback_data="dashboard_active")],
        [InlineKeyboardButton("📊 Statistics", callback_data="dashboard_stats")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="dashboard_settings")],
        [InlineKeyboardButton("📜 Logs", callback_data="dashboard_logs")],
        [InlineKeyboardButton("💾 Backup", callback_data="dashboard_backup")],
        [InlineKeyboardButton("👥 Admins", callback_data="dashboard_admins")],
    ]
    await update.message.reply_text("🖥️ *Admin Dashboard*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
