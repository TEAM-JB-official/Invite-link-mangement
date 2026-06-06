from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import log_command
from bot.utils.helpers import format_link_info

@log_command
async def active_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = get_db()
    links = await db.invite_links.find({
        "creator_id": user_id,
        "is_revoked": False,
        "expiry_date": {"$gt": datetime.utcnow()}
    }).to_list(None)
    
    if not links:
        await update.message.reply_text("No active invite links.")
        return
    
    text = "🔗 *Your active invite links*\n\n"
    keyboard = []
    for link in links:
        text += format_link_info(link)
        keyboard.append([InlineKeyboardButton(f"Revoke {link['invite_link'][:30]}", callback_data=f"revoke_{link['link_id']}")])
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
