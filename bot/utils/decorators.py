import logging
from datetime import datetime
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.config import OWNER_IDS

logger = logging.getLogger(__name__)

def require_verified(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        db = get_db()
        if db is None:
            await update.message.reply_text("❌ Database not available. Please try again later.")
            return
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
        if db is None:
            await update.message.reply_text("❌ Database not available. Please try again later.")
            return
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
        try:
            db = get_db()
            if db is None:
                await update.message.reply_text("❌ Database not available. Please try again later.")
                return
            admin = await db.admins.find_one({"user_id": user_id})
            if not admin or admin.get("role") != "owner":
                await update.message.reply_text("❌ Owner privilege required.")
                return
        except Exception as e:
            logger.error(f"Error in owner_required: {e}", exc_info=True)
            await update.message.reply_text("❌ An internal error occurred. Please try again later.")
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
        if db is None:
            await update.message.reply_text("❌ Database not available. Please try again later.")
            return
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
        logger.info(f"User {user.id} ({user.username}) executed: {cmd}")
        return await func(update, context, *args, **kwargs)
    return wrapper
