from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import admin_required

@admin_required
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main settings menu – shows list of groups and options."""
    db = get_db()
    groups = await db.groups.find().to_list(None)
    if not groups:
        await update.message.reply_text("No groups/channels found in database. Use /addgroup to add one.")
        return
    keyboard = []
    for g in groups:
        keyboard.append([InlineKeyboardButton(f"📌 {g['title']}", callback_data=f"settings_group_{g['group_id']}")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="dashboard_settings_back")])
    await update.message.reply_text(
        "⚙️ Settings\n\nSelect a group/channel to configure its welcome message or log channel.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from settings menu."""
    query = update.callback_query
    await query.answer()
    data = query.data
    db = get_db()

    if data.startswith("settings_group_"):
        group_id = int(data.split("_")[2])
        group = await db.groups.find_one({"group_id": group_id})
        if not group:
            await query.edit_message_text("Group not found.")
            return
        current_welcome = group.get("welcome_message", "Not set")
        current_log = group.get("log_channel", "Not set")
        text = (
            f"⚙️ Settings for {group['title']}\n\n"
            f"📝 Welcome Message:\n{current_welcome}\n\n"
            f"📢 Log Channel: {current_log}\n\n"
            "What would you like to change?"
        )
        keyboard = [
            [InlineKeyboardButton("✏️ Set Welcome Message", callback_data=f"set_welcome_{group_id}")],
            [InlineKeyboardButton("📢 Set Log Channel", callback_data=f"set_logchannel_{group_id}")],
            [InlineKeyboardButton("🔙 Back to Groups", callback_data="settings_back_to_groups")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    elif data.startswith("set_welcome_"):
        group_id = int(data.split("_")[2])
        context.user_data["pending_welcome_group"] = group_id
        await query.edit_message_text(
            "Send the new welcome message.\n\n"
            "Use {user} for the user's first name and {link_creator} for the creator ID.\n"
            "Example: Welcome {user}! You joined via link created by {link_creator}."
        )
        return

    elif data.startswith("set_logchannel_"):
        group_id = int(data.split("_")[2])
        context.user_data["pending_logchannel_group"] = group_id
        await query.edit_message_text(
            "Send the log channel ID.\n\n"
            "The bot must be an admin in that channel to send logs.\n"
            "Example: -1001234567890"
        )
        return

    elif data == "settings_back_to_groups":
        groups = await db.groups.find().to_list(None)
        keyboard = []
        for g in groups:
            keyboard.append([InlineKeyboardButton(f"📌 {g['title']}", callback_data=f"settings_group_{g['group_id']}")])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="dashboard_settings_back")])
        await query.edit_message_text(
            "⚙️ Settings\n\nSelect a group/channel:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    elif data == "dashboard_settings_back":
        from bot.handlers.dashboard import dashboard
        await dashboard(update, context)
        return

async def handle_settings_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input for setting welcome message or log channel."""
    text = update.message.text.strip()
    db = get_db()

    if "pending_welcome_group" in context.user_data:
        group_id = context.user_data.pop("pending_welcome_group")
        await db.groups.update_one(
            {"group_id": group_id},
            {"$set": {"welcome_message": text}}
        )
        await update.message.reply_text(f"✅ Welcome message updated for group {group_id}.")
        # Re‑open settings for that group
        group = await db.groups.find_one({"group_id": group_id})
        if group:
            current_welcome = text
            current_log = group.get("log_channel", "Not set")
            reply = (
                f"⚙️ Settings for {group['title']}\n\n"
                f"📝 Welcome Message:\n{current_welcome}\n\n"
                f"📢 Log Channel: {current_log}\n\n"
                "What would you like to change?"
            )
            keyboard = [
                [InlineKeyboardButton("✏️ Set Welcome Message", callback_data=f"set_welcome_{group_id}")],
                [InlineKeyboardButton("📢 Set Log Channel", callback_data=f"set_logchannel_{group_id}")],
                [InlineKeyboardButton("🔙 Back to Groups", callback_data="settings_back_to_groups")]
            ]
            await update.message.reply_text(reply, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    elif "pending_logchannel_group" in context.user_data:
        group_id = context.user_data.pop("pending_logchannel_group")
        try:
            log_channel = int(text)
        except ValueError:
            await update.message.reply_text("❌ Please send a valid numeric channel ID.")
            return
        await db.groups.update_one(
            {"group_id": group_id},
            {"$set": {"log_channel": log_channel}}
        )
        await update.message.reply_text(f"✅ Log channel set to {log_channel} for group {group_id}.")
        group = await db.groups.find_one({"group_id": group_id})
        if group:
            current_welcome = group.get("welcome_message", "Not set")
            reply = (
                f"⚙️ Settings for {group['title']}\n\n"
                f"📝 Welcome Message:\n{current_welcome}\n\n"
                f"📢 Log Channel: {log_channel}\n\n"
                "What would you like to change?"
            )
            keyboard = [
                [InlineKeyboardButton("✏️ Set Welcome Message", callback_data=f"set_welcome_{group_id}")],
                [InlineKeyboardButton("📢 Set Log Channel", callback_data=f"set_logchannel_{group_id}")],
                [InlineKeyboardButton("🔙 Back to Groups", callback_data="settings_back_to_groups")]
            ]
            await update.message.reply_text(reply, reply_markup=InlineKeyboardMarkup(keyboard))
        return
