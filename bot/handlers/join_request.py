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
    if not link or link.get("is_revoked"):
        await request.decline()
        return
    if link["expiry_date"] < datetime.utcnow():
        await request.decline()
        await revoke_link_by_id(link_id, context.bot)
        await send_log(context.bot, f"⏰ Link {link_id} expired, join declined.")
        return
    if link["current_uses"] >= link["max_uses"]:
        await request.decline()
        return

    await request.approve()
    await db.link_usage.insert_one({
        "user_id": user.id,
        "link_id": link_id,
        "chat_id": group_id,
        "joined_at": datetime.utcnow()
    })
    await db.invite_links.update_one({"link_id": link_id}, {"$inc": {"current_uses": 1}})

    if link["max_uses"] == 1 or link["current_uses"] + 1 >= link["max_uses"]:
        await revoke_link_by_id(link_id, context.bot)

    # Send welcome message
    await send_welcome(context.bot, group_id, user, link["creator_id"])
    await send_log(context.bot, f"✅ New join: {user.full_name} (@{user.username}) used link {link['invite_link']}")
