from datetime import datetime
import re
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, set_bot_setting
from bot.utils.decorators import owner_required

@owner_required
async def setactivelink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 1:
        await update.message.reply_text(
            "Usage: /setactivelink <link_id or invite_url>\n"
            "Examples:\n"
            "  /setactivelink +8mnISJbFMB1mMjE9\n"
            "  /setactivelink https://t.me/+8mnISJbFMB1mMjE9\n\n"
            "Run /listlinks to see all available links with their IDs."
        )
        return

    user_input = args[0].strip()
    
    # Extract link_id from URL or use directly
    if "t.me/+" in user_input:
        link_id = user_input.split("/")[-1]
    else:
        link_id = user_input

    db = get_db()
    link = await db.invite_links.find_one({"link_id": link_id})
    if not link:
        # Show available links to help the user
        all_links = await db.invite_links.find().to_list(None)
        if all_links:
            hint = "\nAvailable link IDs:\n" + "\n".join([f"  • {l['link_id']}" for l in all_links[:5]])
        else:
            hint = "\nNo links found. Create one with /create_link first."
        await update.message.reply_text(
            f"❌ Link not found: `{link_id}`. Use `/listlinks` to see all links.{hint}",
            parse_mode="Markdown"
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
        "Now enable Create‑Link Mode with `/activelinkmode on`."
    )
