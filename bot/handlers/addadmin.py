from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import owner_required

@owner_required
async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new admin: /addadmin <user_id> <role>
       Role: admin, super_admin, or owner"""
    args = context.args
    if len(args) != 2:
        await update.message.reply_text(
            "Usage: /addadmin <user_id> <role>\n"
            "Role options: admin, super_admin, owner\n"
            "Example: /addadmin 123456789 super_admin"
        )
        return
    try:
        user_id = int(args[0])
        role = args[1].lower()
        if role not in ["admin", "super_admin", "owner"]:
            await update.message.reply_text("Role must be 'admin', 'super_admin', or 'owner'.")
            return
    except ValueError:
        await update.message.reply_text("User ID must be a number.")
        return

    db = get_db()
    existing = await db.admins.find_one({"user_id": user_id})
    if existing:
        await update.message.reply_text(f"User {user_id} is already an admin with role {existing['role']}.")
    else:
        await db.admins.insert_one({
            "user_id": user_id,
            "role": role,
            "added_by": update.effective_user.id,
            "added_at": datetime.utcnow()
        })
        await update.message.reply_text(f"✅ Admin added: {user_id} as {role}.")
