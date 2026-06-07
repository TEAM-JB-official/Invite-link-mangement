from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import admin_required

@admin_required
async def setlogchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set log channel for a group: /setlogchannel <group_id> <channel_id>"""
    args = context.args
    if len(args) != 2:
        await update.message.reply_text(
            "Usage: /setlogchannel <group_id> <channel_id>\n"
            "Example: /setlogchannel -1001234567890 -1009876543210\n\n"
            "The bot must be an admin in both the group and the log channel."
        )
        return
    try:
        group_id = int(args[0])
        log_channel = int(args[1])
    except ValueError:
        await update.message.reply_text("Both IDs must be numbers.")
        return

    db = get_db()
    group = await db.groups.find_one({"group_id": group_id})
    if not group:
        await update.message.reply_text(f"Group {group_id} not found. Use /addgroup first.")
        return

    await db.groups.update_one({"group_id": group_id}, {"$set": {"log_channel": log_channel}})
    await update.message.reply_text(
        f"✅ Log channel set for group {group['title']}:\n"
        f"Channel ID: {log_channel}\n\n"
        "All join logs and link creation logs will be sent there."
    )
