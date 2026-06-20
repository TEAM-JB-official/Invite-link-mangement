from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import owner_required

@owner_required
async def removegroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a registered group/channel: /removegroup <group_id>"""
    args = context.args
    if not args:
        await update.message.reply_text(
            "Usage: /removegroup <group_id>\n"
            "Example: /removegroup -1001234567890"
        )
        return

    try:
        group_id = int(args[0])
    except ValueError:
        await update.message.reply_text("❌ Group ID must be a number.")
        return

    db = get_db()
    result = await db.groups.delete_one({"group_id": group_id})

    if result.deleted_count:
        await update.message.reply_text(f"✅ Group/channel {group_id} removed successfully.")
    else:
        await update.message.reply_text(f"❌ Group/channel {group_id} not found.")
