from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import set_bot_setting, get_bot_setting
from bot.utils.decorators import owner_required

@owner_required
async def activelinkmode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enable or disable Create‑Link Mode: /activelinkmode on/off"""
    args = context.args
    if len(args) != 1 or args[0].lower() not in ["on", "off"]:
        await update.message.reply_text("Usage: /activelinkmode on  or  /activelinkmode off")
        return
    mode = args[0].lower() == "on"
    await set_bot_setting("create_link_mode", mode)
    status = "ON" if mode else "OFF"
    await update.message.reply_text(f"✅ Create‑Link Mode turned {status}.")
    if mode:
        active_id = await get_bot_setting("active_link_id")
        if not active_id:
            await update.message.reply_text("⚠️ No active link set. Use /setactivelink <link_id> first.")
