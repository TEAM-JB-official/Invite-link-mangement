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
            group = await db.groups.find_one({"group_id": link["chat_id"]})
            chat_title = group["title"] if group else str(link["chat_id"])
            text += f"📌 Chat: {chat_title}\n"
            text += f"🔗 {link['invite_link']}\n"
            text += f"🆔 {link['link_id']}\n"
            text += f"📊 Uses: {link['current_uses']}/{link['max_uses']}\n"
            text += f"⏰ Expires: {link['expiry_date']}\n"
            text += f"👤 Creator: {link['creator_id']}\n"
            text += "───────────────────\n"
        await update.message.reply_text(text)
