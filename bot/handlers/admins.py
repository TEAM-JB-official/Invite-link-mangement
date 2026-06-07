from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import owner_required
from bot.config import OWNER_ID

@owner_required
async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin list and management buttons."""
    db = get_db()
    admin_list = await db.admins.find().to_list(None)

    if not admin_list:
        await db.admins.update_one(
            {"user_id": OWNER_ID},
            {"$set": {"role": "owner", "added_by": OWNER_ID, "added_at": datetime.utcnow()}},
            upsert=True
        )
        admin_list = await db.admins.find().to_list(None)

    text = "👥 Admin List\n\n"
    for a in admin_list:
        try:
            user_info = await context.bot.get_chat(a["user_id"])
            name = user_info.first_name or str(a["user_id"])
        except:
            name = str(a["user_id"])
        text += f"• {name} ({a['role']})\n"

    keyboard = [
        [InlineKeyboardButton("➕ Add Admin", callback_data="add_admin")],
        [InlineKeyboardButton("🔙 Back to Dashboard", callback_data="dashboard_admins_back")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def admins_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin management callbacks."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "add_admin":
        context.user_data["add_admin_step"] = "waiting_for_user_id"
        await query.edit_message_text(
            "Send the Telegram user ID of the new admin.\n"
            "Example: 123456789\n\n"
            "Role options: admin or super_admin"
        )
        return

    elif data == "dashboard_admins_back":
        from bot.handlers.dashboard import dashboard
        await dashboard(update, context)
        return

async def handle_admin_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text input for adding an admin."""
    if context.user_data.get("add_admin_step") != "waiting_for_user_id":
        return

    user_id_input = update.message.text.strip()
    parts = user_id_input.split()
    if len(parts) != 2:
        await update.message.reply_text("❌ Please send in format: <user_id> <role>\nExample: 123456789 admin")
        return

    try:
        new_admin_id = int(parts[0])
        role = parts[1].lower()
        if role not in ["admin", "super_admin"]:
            await update.message.reply_text("❌ Role must be admin or super_admin.")
            return
    except ValueError:
        await update.message.reply_text("❌ User ID must be a number.")
        return

    db = get_db()
    existing = await db.admins.find_one({"user_id": new_admin_id})
    if existing:
        await update.message.reply_text(f"User {new_admin_id} is already an admin with role {existing['role']}.")
    else:
        await db.admins.insert_one({
            "user_id": new_admin_id,
            "role": role,
            "added_by": update.effective_user.id,
            "added_at": datetime.utcnow()
        })
        await update.message.reply_text(f"✅ Admin added: {new_admin_id} as {role}.")

    context.user_data.pop("add_admin_step", None)
    await admins(update, context)
