from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.config import OWNER_ID, LOG_CHANNEL
from bot.utils.helpers import generate_referral_code, grant_premium, create_invite_link

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    ref_code = args[0] if args else None
    db = get_db()

    # Register or update user
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
        if user.id == OWNER_ID:
            await db.users.update_one({"user_id": user.id}, {"$set": {"is_verified": True, "is_premium": True}})
            await db.admins.update_one({"user_id": user.id}, {"$set": {"role": "owner"}}, upsert=True)
            await update.message.reply_text("✅ You are the owner. Full access granted.")
        if ref_code and user.id != OWNER_ID:
            referrer = await db.users.find_one({"referral_code": ref_code})
            if referrer and referrer["user_id"] != user.id:
                await db.users.update_one({"user_id": user.id}, {"$set": {"referred_by": referrer["user_id"]}})
                await db.referrals.insert_one({"referrer_id": referrer["user_id"], "referred_id": user.id, "reward_given": False, "created_at": datetime.utcnow()})
                await grant_premium(referrer["user_id"], days=1)
                await grant_premium(user.id, days=1)
                await update.message.reply_text("🎉 You and your referrer each received 1 day of premium!")

    # Auto‑send default invite link (only for non‑owner users)
    if user.id != OWNER_ID:
        default_template = await db.default_link.find_one({"_id": "template"})
        if default_template and default_template.get("group_id", 0) != 0:
            group_id = default_template["group_id"]
            expiry_seconds = default_template["expiry_seconds"]
            max_uses = default_template["max_uses"]

            active_link = await db.invite_links.find_one({
                "creator_id": user.id,
                "group_id": group_id,
                "is_revoked": False,
                "expiry_date": {"$gt": datetime.utcnow()}
            })
            if not active_link:
                expiry_date = datetime.utcnow() + timedelta(seconds=expiry_seconds)
                try:
                    link_info = await create_invite_link(
                        bot=context.bot,
                        group_id=group_id,
                        creator_id=user.id,
                        expiry_date=expiry_date,
                        max_uses=max_uses
                    )
                    await update.message.reply_text(
                        f"✅ Invite link created for you:\n{link_info['invite_link']}\n\n"
                        f"Expires: {expiry_date}\n"
                        f"Max uses: {max_uses}\n\n"
                        "Click the link to join. You will be automatically approved."
                    )
                    if LOG_CHANNEL:
                        await context.bot.send_message(LOG_CHANNEL, f"Auto‑link for {user.id}: {link_info['invite_link']}")
                except Exception as e:
                    await update.message.reply_text(f"❌ Failed to create invite link: {e}")
            else:
                await update.message.reply_text(
                    f"You already have an active invite link:\n{active_link['invite_link']}\n\n"
                    f"Expires: {active_link['expiry_date']}\n"
                    f"Remaining uses: {active_link['max_uses'] - active_link['current_uses']}"
                )
        else:
            await update.message.reply_text("No default invite link template set. Please contact the admin.")
    else:
        await update.message.reply_text(
            f"Welcome back, {user.first_name} (Owner).\n"
            "Use /dashboard to manage links and settings."
        )
