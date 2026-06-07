from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.config import OWNER_ID, LOG_CHANNEL
from bot.utils.helpers import register_user, create_invite_link, revoke_link_by_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = get_db()
    await register_user(user.id, user.username, user.first_name)

    # Owner gets different message
    if user.id == OWNER_ID:
        await update.message.reply_text(
            f"Welcome back, {user.first_name} (Owner).\n"
            "Use /setdefaultlink to configure the default invite link template.\n"
            "Use /dashboard to manage everything."
        )
        return

    # Get default template
    template = await db.default_link.find_one({"_id": "template"})
    if not template or template.get("chat_id", 0) == 0:
        await update.message.reply_text(
            "❌ No default invite link template set.\n"
            "Please contact the admin to run `/setdefaultlink`."
        )
        return

    chat_id = template["chat_id"]
    expiry_seconds = template["expiry_seconds"]
    max_uses = template["max_uses"]

    # Find ANY existing link for this user and chat (including expired/revoked)
    existing_link = await db.invite_links.find_one({
        "creator_id": user.id,
        "chat_id": chat_id
    })

    # Check if the existing link is still valid
    is_valid = False
    if existing_link:
        is_valid = (
            not existing_link.get("is_revoked", False) and
            existing_link["expiry_date"] > datetime.utcnow() and
            existing_link["current_uses"] < existing_link["max_uses"]
        )

    if is_valid:
        # Link is still active – resend it
        remaining = existing_link["max_uses"] - existing_link["current_uses"]
        await update.message.reply_text(
            f"✅ **Invite link created for you:**\n{existing_link['invite_link']}\n\n"
            f"⏰ Expires: {existing_link['expiry_date']}\n"
            f"👥 Max uses: {existing_link['max_uses']}\n\n"
            f"**You already have an active invite link:**\n{existing_link['invite_link']}\n\n"
            f"Expires: {existing_link['expiry_date']}\n"
            f"Remaining uses: {remaining}\n\n"
            "Click the link to join. You will be automatically approved.",
            parse_mode="Markdown"
        )
        return

    # No valid link – create a NEW one
    # First, revoke any old link (if exists)
    if existing_link:
        await revoke_link_by_id(existing_link["link_id"], context.bot)
        await db.invite_links.update_one(
            {"_id": existing_link["_id"]},
            {"$set": {"is_revoked": True}}
        )

    # Create fresh link
    expiry_date = datetime.utcnow() + timedelta(seconds=expiry_seconds)
    try:
        link_info = await create_invite_link(
            bot=context.bot,
            chat_id=chat_id,
            creator_id=user.id,
            expiry_date=expiry_date,
            max_uses=max_uses
        )
        await update.message.reply_text(
            f"✅ **Invite link created for you:**\n{link_info['invite_link']}\n\n"
            f"⏰ Expires: {expiry_date}\n"
            f"👥 Max uses: {max_uses}\n\n"
            "Click the link to join. You will be automatically approved.",
            parse_mode="Markdown"
        )
        if LOG_CHANNEL:
            await context.bot.send_message(LOG_CHANNEL, f"🔗 New default link for user {user.id}: {link_info['invite_link']}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to create invite link: {str(e)}")
