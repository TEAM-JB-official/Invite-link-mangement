from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import owner_required

@owner_required
async def listlinks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all invite links from all chats (paginated, owner only)."""
    db = get_db()
    links = await db.invite_links.find().to_list(None)
    if not links:
        await update.message.reply_text("No invite links found.")
        return

    # Send in chunks of 5 links per message
    chunk_size = 5
    for i in range(0, len(links), chunk_size):
        chunk = links[i:i+chunk_size]
        text = "📋 All Invite Links\n\n"
        for link in chunk:
            # Safely get chat_id; fallback to "unknown" if missing
            chat_id = link.get("chat_id")
            if chat_id:
                group = await db.groups.find_one({"group_id": chat_id})
                chat_title = group["title"] if group else str(chat_id)
            else:
                chat_title = "Unknown (old link)"
            text += f"📌 Chat: {chat_title}\n"
            text += f"🔗 {link.get('invite_link', 'No link')}\n"
            text += f"🆔 {link.get('link_id', 'No ID')}\n"
            text += f"📊 Uses: {link.get('current_uses', 0)}/{link.get('max_uses', 0)}\n"
            text += f"⏰ Expires: {link.get('expiry_date', 'Unknown')}\n"
            text += f"👤 Creator: {link.get('creator_id', 'Unknown')}\n"
            text += "───────────────────\n"
        await update.message.reply_text(text)
