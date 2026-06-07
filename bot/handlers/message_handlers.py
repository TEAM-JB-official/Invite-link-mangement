from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.helpers import create_invite_link
from bot.config import LOG_CHANNEL

async def handle_custom_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    step = context.user_data.get("create_link_step")

    if step == "custom_expiry":
        try:
            seconds = int(text)
            if seconds <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Please send a valid positive number (seconds).")
            return
        context.user_data["create_expiry_seconds"] = seconds
        context.user_data["create_link_step"] = "max_uses"
        keyboard = [
            [InlineKeyboardButton("1 (single-use)", callback_data="maxuses_1")],
            [InlineKeyboardButton("5", callback_data="maxuses_5")],
            [InlineKeyboardButton("10", callback_data="maxuses_10")],
            [InlineKeyboardButton("50", callback_data="maxuses_50")],
            [InlineKeyboardButton("Custom", callback_data="maxuses_custom")],
        ]
        await update.message.reply_text("Select max number of joins:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if step == "custom_maxuses":
        try:
            max_uses = int(text)
            if max_uses <= 0:
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Please send a valid positive integer (e.g., 100).")
            return
        context.user_data["create_max_uses"] = max_uses
        group_id = context.user_data.get("create_group_id")
        expiry_seconds = context.user_data.get("create_expiry_seconds")
        if not group_id or not expiry_seconds:
            await update.message.reply_text("Error: missing data. Please start over with /create_link")
            context.user_data["create_link_step"] = None
            return
        expiry_date = datetime.utcnow() + timedelta(seconds=expiry_seconds)
        try:
            link_info = await create_invite_link(
                bot=context.bot,
                group_id=group_id,
                creator_id=user_id,
                expiry_date=expiry_date,
                max_uses=max_uses
            )
            await update.message.reply_text(f"✅ Invite link created:\n{link_info['invite_link']}\n\nExpires: {expiry_date}\nMax uses: {max_uses}")
            if LOG_CHANNEL:
                await context.bot.send_message(LOG_CHANNEL, f"🔗 New link created by {user_id}: {link_info['invite_link']}")
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to create link: {str(e)}")
        context.user_data["create_link_step"] = None
        return
