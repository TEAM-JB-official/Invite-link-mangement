from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, get_bot_setting, get_default_links
from bot.utils.decorators import owner_required

@owner_required
async def defaultlinkstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    templates = await get_default_links()
    default_info = f"{len(templates)} template(s)"
    if templates:
        details = []
        for t in templates:
            details.append(f"  • Chat `{t['chat_id']}`: {t['expiry_seconds']}s, {t['max_uses']} uses")
        default_info += "\n" + "\n".join(details)
    else:
        default_info = "Not configured"

    create_mode = await get_bot_setting("create_link_mode", False)
    active_ids = await get_bot_setting("active_link_ids", [])
    active_info = f"{len(active_ids)} link(s)"
    if active_ids:
        details = []
        for lid in active_ids:
            link = await db.invite_links.find_one({"link_id": lid})
            if link:
                group = await db.groups.find_one({"group_id": link["chat_id"]})
                chat = group["title"] if group else str(link["chat_id"])
                status = "✅" if not link.get("is_revoked") and link["expiry_date"] > datetime.utcnow() else "❌"
                details.append(f"  • {chat}: `{lid}` {status}")
            else:
                details.append(f"  • `{lid}` ❌ not found")
        active_info += "\n" + "\n".join(details)

    text = (
        f"📊 *Link System Status*\n\n"
        f"🔹 Default Auto-Link System: {default_info}\n"
        f"🔹 Create-Link Mode: {'ON' if create_mode else 'OFF'}\n"
        f"🔹 Active Links (fixed): {active_info}\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
