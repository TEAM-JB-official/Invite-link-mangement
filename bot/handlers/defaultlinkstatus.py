from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, get_bot_setting
from bot.utils.decorators import owner_required

@owner_required
async def defaultlinkstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    template = await db.default_link.find_one({"_id": "template"})
    default_status = "Active" if template and template.get("chat_id", 0) != 0 else "Not configured"

    create_mode = await get_bot_setting("create_link_mode", False)
    active_link_ids = await get_bot_setting("active_link_ids", [])

    text = f"📊 *Link System Status*\n\n"
    text += f"🔹 Default Auto-Link System: {default_status}\n"
    text += f"🔹 Create-Link Mode: {'ON' if create_mode else 'OFF'}\n"
    text += f"🔹 Total Active Links: {len(active_link_ids)}\n"

    if active_link_ids:
        text += "\n*Active Links:*\n"
        for link_id in active_link_ids:
            link = await db.invite_links.find_one({"link_id": link_id})
            if link:
                group = await db.groups.find_one({"group_id": link["chat_id"]})
                chat = group["title"] if group else str(link["chat_id"])
                status = "✅ valid" if not link.get("is_revoked") and link["expiry_date"] > datetime.utcnow() else "❌ expired/revoked"
                text += f"• {chat}: `{link_id}` ({status})\n"
            else:
                text += f"• `{link_id}` (❌ not found)\n"
    else:
        text += "\nNo active links set.\n"

    await update.message.reply_text(text, parse_mode="Markdown")
