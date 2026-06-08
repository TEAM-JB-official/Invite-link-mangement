from datetime import datetime
import re
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, set_bot_setting
from bot.utils.decorators import owner_required

@owner_required
async def setactivelink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set the active link for Create‑Link Mode: /setactivelink <link_id or URL>"""
    args = context.args
    if len(args) != 1:
        await update.message.reply_text(
            "Usage: /setactivelink <link_id or invite_url>\n"
            "Examples:\n"
            "  /setactivelink +8mnISJbFMB1mMjE9\n"
            "  /setactivelink https://t.me/+8mnISJbFMB1mMjE9\n\n"
            "Use /active_links to see your links."
        )
        return

    user_input = args[0].strip()
    
    # If input is a full URL, extract the link_id
    if user_input.startswith("https://t.me/+"):
        link_id = user_input.split("/")[-1]
    elif user_input.startswith("t.me/+"):
        link_id = user_input.split("/")[-1]
    else:
        link_id = user_input  # assume it's already a link_id

    db = get_db()
    link = await db.invite_links.find_one({"link_id": link_id})
    if not link:
        await update.message.reply_text(
            f"❌ Link not found: {link_id}\n"
            "Make sure you copied the correct link ID from /active_links."
        )
        return
    if link.get("is_revoked"):
        await update.message.reply_text("❌ This link is revoked and cannot be used.")
        return
    if link["expiry_date"] < datetime.utcnow():
        await update.message.reply_text("❌ This link has expired. Create a new one.")
        return

    await set_bot_setting("active_link_id", link_id)
    await update.message.reply_text(
        f"✅ Active link set to:\n{link['invite_link']}\n\n"
        "Now enable Create‑Link Mode with /activelinkmode on."
    )
