from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import owner_required

@owner_required
async def set_default_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 3:
        await update.message.reply_text(
            "Usage: /setdefaultlink <group_id> <expiry_seconds> <max_uses>\n"
            "Example: /setdefaultlink -1003985321670 604800 1\n"
            "Expiry seconds: 3600=1h, 86400=1d, 604800=7d"
        )
        return
    try:
        group_id = int(args[0])
        expiry_seconds = int(args[1])
        max_uses = int(args[2])
    except ValueError:
        await update.message.reply_text("Invalid numbers. Group ID must be integer (negative for groups).")
        return

    db = get_db()
    await db.default_link.update_one(
        {"_id": "template"},
        {"$set": {"group_id": group_id, "expiry_seconds": expiry_seconds, "max_uses": max_uses}},
        upsert=True
    )
    await update.message.reply_text(
        f"✅ Default invite link set:\n"
        f"Group ID: {group_id}\n"
        f"Expiry: {expiry_seconds} seconds ({expiry_seconds//3600} hours)\n"
        f"Max uses: {max_uses}\n\n"
        "New users will now receive this type of link on /start."
    )
