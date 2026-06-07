from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.config import OWNER_ID, LOG_CHANNEL
from bot.utils.helpers import register_user, create_invite_link

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

    # Check for existing active link
    active_link = await db.invite_links.find_one({
        "creator_id": user.id,
        "chat_id": chat_id,
        "is_revoked": False,
        "expiry_date": {"$gt": datetime.utcnow()}
    })

    if active_link:
        remaining = active_link["max_uses"] - active_link["current_uses"]
        if remaining <= 0:
            # Link has reached usage limit, but not expired – revoke and create new
            await revoke_link_by_id(active_link["link_id"], context.bot)
            active_link = None
        else:
            # Show existing link
            await update.message.reply_text(
                f"✅ **Invite link created for you:**\n{active_link['invite_link']}\n\n"
                f"⏰ Expires: {active_link['expiry_date']}\n"
                f"👥 Max uses: {active_link['max_uses']}\n\n"
                f"**You already have an active invite link:**\n{active_link['invite_link']}\n\n"
                f"Expires: {active_link['expiry_date']}\n"
                f"Remaining uses: {remaining}\n\n"
                "Click the link to join. You will be automatically approved.",
                parse_mode="Markdown"
            )
            return

    if not active_link:
        # Create new link
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
