from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.helpers import revoke_link_by_id, send_log

async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles join requests but does NOT auto-approve.
    Only logs the request and updates database.
    Admin must approve manually via Telegram.
    """
    request = update.chat_join_request
    invite_url = request.invite_link.invite_link
    link_id = invite_url.split("/")[-1]
    user = request.from_user
    group_id = request.chat.id

    print(f"=== JOIN REQUEST RECEIVED (waiting for admin approval) ===")
    print(f"User: {user.id} ({user.first_name})")
    print(f"Group: {group_id}")
    print(f"Link ID: {link_id}")

    db = get_db()
    link = await db.invite_links.find_one({"link_id": link_id})
    
    if not link:
        print("❌ Link not found in database")
        await send_log(context.bot, f"❌ Join request from {user.first_name} - link not found")
        return
    
    if link.get("is_revoked"):
        print("❌ Link is revoked")
        await send_log(context.bot, f"❌ Join request from {user.first_name} - link revoked")
        return
    
    if link["expiry_date"] < datetime.utcnow():
        print("❌ Link expired")
        await revoke_link_by_id(link_id, context.bot)
        await send_log(context.bot, f"⏰ Link {link_id} expired, join request ignored.")
        return
    
    if link["current_uses"] >= link["max_uses"]:
        print("❌ Usage limit reached")
        await send_log(context.bot, f"❌ Join request from {user.first_name} - usage limit reached")
        return

    # DO NOT auto-approve - admin must approve manually
    print("⏳ Join request logged - waiting for admin approval")
    
    # Log the request for tracking
    await send_log(
        context.bot, 
        f"📋 Join request from {user.full_name} (@{user.username})\n"
        f"Link: {link['invite_link']}\n"
        f"Group: {group_id}\n"
        f"Waiting for admin approval."
    )
