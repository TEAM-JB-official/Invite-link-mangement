from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.helpers import create_invite_link, revoke_link_by_id, format_link_info
from bot.config import LOG_CHANNEL, OWNER_ID

async def callback_handlers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = update.effective_user.id
    db = get_db()

    # Helper to send/edit message from callback
    async def send_or_edit(text, reply_markup=None, parse_mode=None):
        if query.message:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            await context.bot.send_message(chat_id=user_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)

    # Dashboard: Create Link
    if data == "dashboard_create":
        # Get groups where bot is admin
        groups = await db.groups.find().to_list(None)
        if not groups:
            await send_or_edit("❌ I'm not admin in any group yet. Add me as admin first.")
            return
        context.user_data["create_link_step"] = "group"
        keyboard = [[InlineKeyboardButton(g["title"], callback_data=f"creategroup_{g['group_id']}")] for g in groups]
        await send_or_edit("Select a group:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Dashboard: Active Links
    if data == "dashboard_active":
        links = await db.invite_links.find({
            "creator_id": user_id,
            "is_revoked": False,
            "expiry_date": {"$gt": datetime.utcnow()}
        }).to_list(None)
        if not links:
            await send_or_edit("No active invite links.")
            return
        text = "🔗 *Your active invite links*\n\n"
        keyboard = []
        for link in links:
            text += format_link_info(link)
            keyboard.append([InlineKeyboardButton(f"Revoke {link['invite_link'][:30]}", callback_data=f"revoke_{link['link_id']}")])
        await send_or_edit(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # Dashboard: Statistics
    if data == "dashboard_stats":
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
        await send_or_edit(text, parse_mode="Markdown")
        return

    # Dashboard: Settings (just a placeholder, full implementation in separate handler)
    if data == "dashboard_settings":
        # You can implement settings menu here or call the settings command properly
        # For now, inform user to use /settings
        await send_or_edit("Use /settings to configure bot settings.")
        return

    # Dashboard: Logs
    if data == "dashboard_logs":
        if LOG_CHANNEL:
            await send_or_edit("Check the log channel for recent activity.")
        else:
            await send_or_edit("No log channel configured.")
        return

    # Dashboard: Backup
    if data == "dashboard_backup":
        # Check if user is owner
        if user_id != OWNER_ID:
            await send_or_edit("❌ Only the owner can perform backups.")
            return
        # Import backup function
        from bot.handlers.backup import backup
        # We need to call backup with a message context, but we can simulate a command
        # For simplicity, just run backup logic here
        # Since backup sends a file, it's easier to call the command handler with a synthetic update?
        # Instead, we'll call the existing backup function, but it expects a message.
        # For now, advise user to use /backup command.
        await send_or_edit("Please use /backup command to generate a backup.")
        return

    # Dashboard: Admins
    if data == "dashboard_admins":
        if user_id != OWNER_ID:
            # Check if user is super_admin or owner
            admin = await db.admins.find_one({"user_id": user_id})
            if not admin or admin.get("role") not in ["owner", "super_admin"]:
                await send_or_edit("❌ You don't have permission to manage admins.")
                return
        admins_list = await db.admins.find().to_list(None)
        text = "👥 *Admin List*\n\n"
        for a in admins_list:
            user = await db.users.find_one({"user_id": a["user_id"]})
            name = user["first_name"] if user else str(a["user_id"])
            text += f"- {name} ({a['role']})\n"
        keyboard = [[InlineKeyboardButton("Add Admin", callback_data="add_admin")]]
        await send_or_edit(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # Add admin flow (simplified)
    if data == "add_admin":
        context.user_data["add_admin_step"] = "waiting_for_user_id"
        await send_or_edit("Send the Telegram user ID of the new admin.\nRole options: admin, super_admin")
        return

    # Group selection for create link
    if data.startswith("creategroup_"):
        group_id = int(data.split("_")[1])
        context.user_data["create_group_id"] = group_id
        context.user_data["create_link_step"] = "expiry"
        keyboard = [
            [InlineKeyboardButton("1 hour", callback_data="expiry_3600")],
            [InlineKeyboardButton("6 hours", callback_data="expiry_21600")],
            [InlineKeyboardButton("1 day", callback_data="expiry_86400")],
            [InlineKeyboardButton("7 days", callback_data="expiry_604800")],
            [InlineKeyboardButton("Custom", callback_data="expiry_custom")],
        ]
        await send_or_edit("Select expiry time:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("expiry_"):
        if data == "expiry_custom":
            context.user_data["create_link_step"] = "custom_expiry"
            await send_or_edit("Send expiry in seconds (e.g., 3600 for 1 hour):")
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
        await send_or_edit("Select max number of joins:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("maxuses_"):
        if data == "maxuses_custom":
            context.user_data["create_link_step"] = "custom_maxuses"
            await send_or_edit("Send maximum number of joins (e.g., 100):")
            return
        max_uses = int(data.split("_")[1])
        context.user_data["create_max_uses"] = max_uses
        group_id = context.user_data.get("create_group_id")
        expiry_seconds = context.user_data.get("create_expiry_seconds")
        if not group_id or not expiry_seconds:
            await send_or_edit("Error: missing data. Please start over with /create_link")
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
            await send_or_edit(f"✅ Invite link created:\n{link_info['invite_link']}\n\nExpires: {expiry_date}\nMax uses: {max_uses}")
            if LOG_CHANNEL:
                await context.bot.send_message(LOG_CHANNEL, f"🔗 New link created by {user_id} for group {group_id}: {link_info['invite_link']}")
        except Exception as e:
            await send_or_edit(f"❌ Failed to create link: {str(e)}")
        context.user_data["create_link_step"] = None
        return

    # Revoke link from active_links panel
    if data.startswith("revoke_"):
        link_id = data.split("_")[1]
        await revoke_link_by_id(link_id, context.bot)
        await send_or_edit("Link revoked.")
        return

    # If nothing matched
    await send_or_edit("Unknown command. Use /help.")
