from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import log_command

@log_command
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    total_links = await db.invite_links.count_documents({})
    active_links = await db.invite_links.count_documents({"is_revoked": False, "expiry_date": {"$gt": datetime.utcnow()}})
    total_joins = await db.link_usage.count_documents({})
    total_users = await db.users.count_documents({})
    premium_users = await db.users.count_documents({"is_premium": True, "premium_expiry": {"$gt": datetime.utcnow()}})
    
    text = (
        f"📊 *Bot Statistics*\n\n"
        f"🔗 Total links created: {total_links}\n"
        f"✅ Active links: {active_links}\n"
        f"👥 Total joins: {total_joins}\n"
        f"👤 Registered users: {total_users}\n"
        f"⭐ Premium users: {premium_users}\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
