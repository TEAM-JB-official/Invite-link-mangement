from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.helpers import revoke_link_by_id, send_log, send_welcome

async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    link_id = request.invite_link.id
    user = request.from_user
    group_id = request.chat.id
    
    db = get_db()
    link = await db.invite_links.find_one({"link_id": link_id})
    
    if not link or link.get("is_revoked", False):
        await request.decline()
        return
    
    # Check expiry
    if link["expiry_date"] < datetime.utcnow():
        await request.decline()
        await revoke_link_by_id(link_id, context.bot)
        await send_log(f"⏰ Link {link_id} expired, join request declined.")
        return
    
    # Check usage limit
    if link["current_uses"] >= link["max_uses"]:
        await request.decline()
        return
    
    # Approve user
    await request.approve()
    
    # Record usage
    await db.link_usage.insert_one({
        "user_id": user.id,
        "link_id": link_id,
        "group_id": group_id,
        "joined_at": datetime.utcnow()
    })
    await db.invite_links.update_one({"link_id": link_id}, {"$inc": {"current_uses": 1}})
    
    # Revoke if single-use or limit reached
    if link["max_uses"] == 1 or link["current_uses"] + 1 >= link["max_uses"]:
        await revoke_link_by_id(link_id, context.bot)
    
    # Send welcome message
    group = await db.groups.find_one({"group_id": group_id})
    if group and group.get("welcome_message"):
        msg = group["welcome_message"].format(user=user.first_name, link_creator=str(link["creator_id"]))
        await context.bot.send_message(group_id, msg)
    
    # Log join
    await send_log(f"✅ New join: {user.full_name} (@{user.username}) used link {link['invite_link']}")
