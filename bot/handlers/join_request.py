from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.helpers import revoke_link_by_id, send_log

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

    # ----- WELCOME MESSAGE (plain text + safe HTML) -----
    welcome_text = (
        f"<b>Hi {user.first_name}</b>,\n\n"
        f"🔹 This bot provides secure invite links for our group/channel.\n"
        f"🔹 Each invite link may have a usage limit or expiry time.\n"
        f"🔹 To receive your invite link, press the button below or use /start.\n\n"
        f"📌 <b>Rules:</b>\n"
        f"• Do not share invite links with others.\n"
        f"• Expired links cannot be reused.\n"
        f"• Contact an admin if you have any issues.\n\n"
        f"Enjoy your stay! 🚀\n\n"
        f"Created By @TeamJB_bot"
    )
    try:
        await context.bot.send_message(group_id, welcome_text, parse_mode="HTML")
    except Exception as e:
        print(f"Welcome error: {e}")
        # Fallback: send without formatting
        await context.bot.send_message(group_id, welcome_text.replace("<b>", "").replace("</b>", ""))
    await send_log(context.bot, f"✅ New join: {user.full_name} (@{user.username}) used link {link['invite_link']}")
