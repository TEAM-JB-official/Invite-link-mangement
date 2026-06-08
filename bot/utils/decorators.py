from datetime import datetime
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.config import OWNER_IDS   # <-- Import the list of owner IDs

def require_verified(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        db = get_db()
        user = await db.users.find_one({"user_id": update.effective_user.id})
        if not user or not user.get("is_verified"):
            await update.message.reply_text("❌ You are not verified. Contact an admin.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def admin_required(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        # Owners are automatically admins
        if user_id in OWNER_IDS:
            return await func(update, context, *args, **kwargs)
        db = get_db()
        admin = await db.admins.find_one({"user_id": user_id})
        if not admin:
            await update.message.reply_text("❌ Admin privilege required.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def owner_required(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        # Check if user ID is in the OWNER_IDS list
        if user_id in OWNER_IDS:
            return await func(update, context, *args, **kwargs)
        # Also check if user is in admins collection with role "owner"
        db = get_db()
        admin = await db.admins.find_one({"user_id": user_id})
        if not admin or admin.get("role") != "owner":
            await update.message.reply_text("❌ Owner privilege required.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# Alias for owner_only (same as owner_required)
owner_only = owner_required

def owner_or_superadmin_required(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id in OWNER_IDS:
            return await func(update, context, *args, **kwargs)
        db = get_db()
        admin = await db.admins.find_one({"user_id": user_id})
        if not admin or admin.get("role") not in ["owner", "super_admin"]:
            await update.message.reply_text("❌ Owner or Super Admin privilege required.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

def log_command(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        cmd = update.message.text.split()[0] if update.message else "callback"
        print(f"[LOG] User {user.id} ({user.username}) executed: {cmd}")
        return await func(update, context, *args, **kwargs)
    return wrapper
