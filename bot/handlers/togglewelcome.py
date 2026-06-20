from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import set_send_welcome_setting, get_send_welcome_setting
from bot.utils.decorators import owner_required

@owner_required
async def togglewelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Enable or disable welcome messages globally.
    Usage: /togglewelcome on  or  /togglewelcome off
    """
    args = context.args
    if len(args) != 1 or args[0].lower() not in ["on", "off"]:
        await update.message.reply_text(
            "Usage: /togglewelcome on  or  /togglewelcome off"
        )
        return

    enable = args[0].lower() == "on"
    await set_send_welcome_setting(enable)
    status = "enabled" if enable else "disabled"
    await update.message.reply_text(f"✅ Welcome messages {status} globally.")

    # Show current state
    current = await get_send_welcome_setting()
    await update.message.reply_text(f"Current state: {'ON' if current else 'OFF'}")
