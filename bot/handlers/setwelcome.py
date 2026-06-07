from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import admin_required

@admin_required
async def setwelcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set welcome message for a group: /setwelcome -1001234567890 Welcome {user}!"""
    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "Usage: /setwelcome <group_id> <message>\n"
            "Use {user} for user's first name, {link_creator} for creator ID.\n"
            "Example: /setwelcome -1001234567890 Welcome {user}! You joined via {link_creator}."
        )
        return
    try:
        group_id = int(args[0])
        message = " ".join(args[1:])
    except ValueError:
        await update.message.reply_text("Group ID must be a number.")
        return

    db = get_db()
    group = await db.groups.find_one({"group_id": group_id})
    if not group:
        await update.message.reply_text(f"Group {group_id} not found. Use /addgroup first.")
        return

    await db.groups.update_one({"group_id": group_id}, {"$set": {"welcome_message": message}})
    await update.message.reply_text(f"✅ Welcome message set for group {group['title']}:\n{message}")
