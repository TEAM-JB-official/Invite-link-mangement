from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import owner_required

@owner_required
async def listlinks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all invite links with their IDs (owner only)."""
    db = get_db()
    links = await db.invite_links.find().to_list(None)
    if not links:
        await update.message.reply_text("No invite links found.")
        return
    text = "📋 *All Invite Links*\n\n"
    for link in links:
        text += f"🔗 {link['invite_link']}\n"
        text += f"🆔 `{link['link_id']}`\n"
        text += f"📊 Uses: {link['current_uses']}/{link['max_uses']}\n"
        text += f"⏰ Expires: {link['expiry_date']}\n"
        text += f"👤 Creator: {link['creator_id']}\n"
        text += "───────────────────\n"
    await update.message.reply_text(text, parse_mode="Markdown")
