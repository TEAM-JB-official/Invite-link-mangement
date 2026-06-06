from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.helpers import generate_referral_code, grant_premium, register_user
from bot.utils.decorators import log_command

@log_command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    ref_code = args[0] if args else None
    
    db = get_db()
    existing = await db.users.find_one({"user_id": user.id})
    
    if not existing:
        code = generate_referral_code(user.id)
        await db.users.insert_one({
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "is_verified": False,
            "is_premium": False,
            "premium_expiry": None,
            "referral_code": code,
            "referred_by": None,
            "created_at": datetime.utcnow()
        })
        
        if ref_code:
            referrer = await db.users.find_one({"referral_code": ref_code})
            if referrer and referrer["user_id"] != user.id:
                await db.users.update_one(
                    {"user_id": user.id},
                    {"$set": {"referred_by": referrer["user_id"]}}
                )
                await db.referrals.insert_one({
                    "referrer_id": referrer["user_id"],
                    "referred_id": user.id,
                    "reward_given": False,
                    "created_at": datetime.utcnow()
                })
                await grant_premium(referrer["user_id"], days=1)
                await grant_premium(user.id, days=1)
                await update.message.reply_text("🎉 You and your referrer both received 1 day of premium!")
    
    await update.message.reply_text(
        f"Welcome {user.first_name}!\n\n"
        "I can manage invite links for groups where I'm admin.\n"
        "Use /create_link to start.\n"
        "Use /dashboard for full control panel.\n"
        "Use /help for more commands."
    )
