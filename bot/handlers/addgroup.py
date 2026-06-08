from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.config import OWNER_IDS  # import the list of owner IDs

async def addgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    # Check if user is in the list of owners
    if user_id not in OWNER_IDS:
        await update.message.reply_text("❌ Only the owner can add groups.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addgroup <group_id> <group_title>\nExample: /addgroup -1001234567890 My Group")
        return
    try:
        group_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Group ID must be a number.")
        return
    title = " ".join(context.args[1:])
    db = get_db()
    existing = await db.groups.find_one({"group_id": group_id})
    if existing:
        await update.message.reply_text(f"✅ Group already exists: {title}")
        return
    await db.groups.insert_one({
        "group_id": group_id,
        "title": title,
        "welcome_message": "Welcome {user}! You joined via {link_creator}.",
        "log_channel": None,
        "settings": {}
    })
    await update.message.reply_text(f"✅ Group added: {title} ({group_id})\nNow you can create invite links.")
