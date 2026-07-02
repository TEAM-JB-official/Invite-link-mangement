import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import owner_required

logger = logging.getLogger(__name__)

@owner_required
async def removegroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Remove a registered group/channel from the database.
    Usage: /removegroup <group_id>
    Example: /removegroup -1001234567890
    """
    try:
        user = update.effective_user
        chat = update.effective_chat
        logger.info(f"removegroup called by {user.id} in chat {chat.id if chat else 'private'}")

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
        if db is None:
            logger.error("Database connection is None")
            await update.message.reply_text("❌ Database not available. Please try again later.")
            return

        # Check if group exists before deleting
        existing = await db.groups.find_one({"group_id": group_id})
        if not existing:
            await update.message.reply_text(f"❌ Group/channel {group_id} not found.")
            return

        # Delete the group
        result = await db.groups.delete_one({"group_id": group_id})
        if result.deleted_count:
            await update.message.reply_text(f"✅ Group/channel {group_id} removed successfully.")
            logger.info(f"Group {group_id} removed by {user.id}")
        else:
            await update.message.reply_text(f"❌ Failed to remove group {group_id}.")
            logger.warning(f"Delete failed for group {group_id}")

    except Exception as e:
        logger.error(f"Unhandled exception in removegroup: {e}", exc_info=True)
        await update.message.reply_text("❌ An internal error occurred. Please check logs and try again.")
