from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from bot.database.mongo import get_db
from bot.utils.helpers import create_invite_link, revoke_link_by_id, get_max_allowed_days
from bot.config import LOG_CHANNEL

async def callback_handlers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id
    db = get_db()
    
    # Group selection for create link
    if data.startswith("creategroup_"):
        group_id = int(data.split("_")[1])
        context.user_data["create_group_id"] = group_id
        context.user_data["create_link_step"] = "expiry"
        # Expiry options
        keyboard = [
            [InlineKeyboardButton("1 hour", callback_data="expiry_3600")],
            [InlineKeyboardButton("6 hours", callback_data="expiry_21600")],
            [InlineKeyboardButton("1 day", callback_data="expiry_86400")],
            [InlineKeyboardButton("7 days", callback_data="expiry_604800")],
            [InlineKeyboardButton("Custom", callback_data="expiry_custom")],
        ]
        await query.edit_message_text("Select expiry time:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("expiry_"):
        if data == "expiry_custom":
            context.user_data["create_link_step"] = "custom_expiry"
            await query.edit_message_text("Send expiry in seconds (e.g., 3600 for 1 hour):")
            return
        seconds = int(data.split("_")[1])
        context.user_data["create_expiry_seconds"] = seconds
        context.user_data["create_link_step"] = "max_uses"
        keyboard = [
            [InlineKeyboardButton("1 (single-use)", callback_data="maxuses_1")],
            [InlineKeyboardButton("5", callback_data="maxuses_5")],
            [InlineKeyboardButton("10", callback_data="maxuses_10")],
            [InlineKeyboardButton("50", callback_data="maxuses_50")],
            [InlineKeyboardButton("Custom", callback_data="maxuses_custom")],
        ]
        await query.edit_message_text("Select max number of joins:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("maxuses_"):
        if data == "maxuses_custom":
            context.user_data["create_link_step"] = "custom_maxuses"
            await query.edit_message_text("Send maximum number of joins (e.g., 100):")
            return
        max_uses = int(data.split("_")[1])
        context.user_data["create_max_uses"] = max_uses
        # Create the link
        group_id = context.user_data.get("create_group_id")
        expiry_seconds = context.user_data.get("create_expiry_seconds")
        if not group_id or not expiry_seconds:
            await query.edit_message_text("Error: missing data. Please start over with /create_link")
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
            await query.edit_message_text(f"✅ Invite link created:\n{link_info['invite_link']}\n\nExpires: {expiry_date}\nMax uses: {max_uses}")
            # Log to channel
            if LOG_CHANNEL:
                await context.bot.send_message(LOG_CHANNEL, f"🔗 New link created by {user_id} for group {group_id}: {link_info['invite_link']}")
        except Exception as e:
            await query.edit_message_text(f"❌ Failed to create link: {str(e)}")
        # Clear step
        context.user_data["create_link_step"] = None
    
    # Revoke link from active_links panel
    elif data.startswith("revoke_"):
        link_id = data.split("_")[1]
        await revoke_link_by_id(link_id, context.bot)
        await query.edit_message_text("Link revoked.")
    
    # Dashboard actions
    elif data == "dashboard_create":
        await create_link(update, context)  # re-use the command handler
    elif data == "dashboard_active":
        await active_links(update, context)
    elif data == "dashboard_stats":
        await stats(update, context)
    elif data == "dashboard_settings":
        await settings(update, context)
    elif data == "dashboard_backup":
        await backup(update, context)
    elif data == "dashboard_admins":
        await admins(update, context)
    elif data == "dashboard_logs":
        # Send last 20 logs from channel (if bot has access)
        if LOG_CHANNEL:
            await query.edit_message_text("Check the log channel for recent activity.")
        else:
            await query.edit_message_text("No log channel configured.")
