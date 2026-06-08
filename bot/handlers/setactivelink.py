from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, set_bot_setting
from bot.utils.decorators import owner_required

@owner_required
async def setactivelink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set the active link for Create‑Link Mode: /setactivelink <link_id>"""
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Usage: /setactivelink <link_id>\nUse /active_links to see link IDs.")
        return
    link_id = args[0]
    db = get_db()
    link = await db.invite_links.find_one({"link_id": link_id})
    if not link:
        await update.message.reply_text("❌ Link not found. Check the ID.")
        return
    if link.get("is_revoked"):
        await update.message.reply_text("❌ This link is revoked and cannot be used.")
        return
    if link["expiry_date"] < datetime.utcnow():
        await update.message.reply_text("❌ This link has expired. Create a new one.")
        return
    await set_bot_setting("active_link_id", link_id)
    await update.message.reply_text(f"✅ Active link set to: {link['invite_link']}\nNow enable Create‑Link Mode with /activelinkmode on.")
