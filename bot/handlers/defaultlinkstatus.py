from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, get_bot_setting
from bot.utils.decorators import owner_required
from datetime import datetime

@owner_required
async def defaultlinkstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    # Default Auto-Link System status: always ON unless Create-Link Mode is ON? Actually default system is always ready.
    # We'll show the template.
    template = await db.default_link.find_one({"_id": "template"})
    default_status = "Active" if template and template.get("chat_id",0) != 0 else "Not configured"
    create_mode = await get_bot_setting("create_link_mode", False)
    active_link_id = await get_bot_setting("active_link_id", None)
    active_link_info = "None"
    if active_link_id:
        link = await db.invite_links.find_one({"link_id": active_link_id})
        if link:
            active_link_info = f"{link['invite_link']} (expires: {link['expiry_date']})"
    text = (
        f"📊 *Link System Status*\n\n"
        f"🔹 Default Auto-Link System: {default_status}\n"
        f"🔹 Create-Link Mode: {'ON' if create_mode else 'OFF'}\n"
        f"🔹 Current Active Link ID: {active_link_id or 'None'}\n"
        f"🔹 Active Link: {active_link_info}\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
