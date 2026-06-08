from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, set_bot_setting, get_bot_setting
from bot.utils.decorators import owner_required

def extract_link_id(input_str: str) -> str:
    """Extract link_id from URL or return the string if it's already an ID."""
    if "t.me/+" in input_str:
        return input_str.split("/")[-1]
    return input_str

@owner_required
async def setactivelink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Set multiple active links (overwrites current list).
    Usage: /setactivelink <link_id_or_url1> <link_id_or_url2> ...
    Example: /setactivelink https://t.me/+ABC123 +DEF456
    To clear: /setactivelink clear
    """
    args = context.args
    if not args:
        await update.message.reply_text(
            "Usage:\n"
            "/setactivelink <link_id1> <link_id2> ... – set active links\n"
            "/setactivelink clear – remove all active links\n"
            "Example: /setactivelink https://t.me/+ABC123 +DEF456"
        )
        return

    if args[0].lower() == "clear":
        await set_bot_setting("active_link_ids", [])
        await update.message.reply_text("✅ All active links cleared.")
        return

    db = get_db()
    valid_ids = []
    invalid = []
    not_found = []

    for arg in args:
        link_id = extract_link_id(arg)
        link = await db.invite_links.find_one({"link_id": link_id})
        if not link:
            not_found.append(arg)
            continue
        if link.get("is_revoked"):
            invalid.append(f"{link_id} (revoked)")
            continue
        if link["expiry_date"] < datetime.utcnow():
            invalid.append(f"{link_id} (expired)")
            continue
        valid_ids.append(link_id)

    if not_found:
        await update.message.reply_text(f"❌ Links not found: {', '.join(not_found)}")
    if invalid:
        await update.message.reply_text(f"⚠️ Invalid (revoked/expired): {', '.join(invalid)}")

    if valid_ids:
        await set_bot_setting("active_link_ids", valid_ids)
        # Also ensure Create‑Link Mode is ON
        current_mode = await get_bot_setting("create_link_mode", False)
        if not current_mode:
            await set_bot_setting("create_link_mode", True)
            await update.message.reply_text("✅ Create‑Link Mode automatically turned ON.")
        await update.message.reply_text(
            f"✅ Active links set ({len(valid_ids)}):\n" +
            "\n".join([f"• {link_id}" for link_id in valid_ids])
        )
    else:
        await update.message.reply_text("No valid links were added. Active list unchanged.")
