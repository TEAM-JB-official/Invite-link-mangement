from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.helpers import revoke_link_by_id, send_log

async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    invite_url = request.invite_link.invite_link
    link_id = invite_url.split("/")[-1]
    user = request.from_user
    group_id = request.chat.id

    # DEBUG
    print(f"=== JOIN REQUEST RECEIVED ===")
    print(f"User: {user.id} ({user.first_name})")
    print(f"Group: {group_id}")
    print(f"Link URL: {invite_url}")
    print(f"Link ID: {link_id}")

    db = get_db()
    link = await db.invite_links.find_one({"link_id": link_id})
    if not link:
        print("❌ Link not found in database")
        await request.decline()
        return
    if link.get("is_revoked"):
        print("❌ Link is revoked")
        await request.decline()
        return
    if link["expiry_date"] < datetime.utcnow():
        print("❌ Link expired")
        await request.decline()
        await revoke_link_by_id(link_id, context.bot)
        await send_log(context.bot, f"⏰ Link {link_id} expired, join declined.")
        return
    if link["current_uses"] >= link["max_uses"]:
        print("❌ Usage limit reached")
        await request.decline()
        return

    await request.approve()
    print("✅ Request approved")

    await db.link_usage.insert_one({
        "user_id": user.id,
        "link_id": link_id,
        "chat_id": group_id,
        "joined_at": datetime.utcnow()
    })
    await db.invite_links.update_one({"link_id": link_id}, {"$inc": {"current_uses": 1}})

    if link["max_uses"] == 1 or link["current_uses"] + 1 >= link["max_uses"]:
        await revoke_link_by_id(link_id, context.bot)
        print("🔁 Link revoked after use")

    # Send welcome message (plain text)
    welcome_text = (
        f"Hi {user.first_name},\n\n"
        f"🔹 This bot provides secure invite links for our group/channel.\n"
        f"🔹 Each invite link may have a usage limit or expiry time.\n"
        f"🔹 To receive your invite link, press the button below or use /start.\n\n"
        f"📌 Rules:\n"
        f"• Do not share invite links with others.\n"
        f"• Expired links cannot be reused.\n"
        f"• Contact an admin if you have any issues.\n\n"
        f"Enjoy your stay! 🚀\n\n"
        f"Created By @TeamJB_bot"
    )
    try:
        await context.bot.send_message(group_id, welcome_text)
        print(f"✅ Welcome message sent to group {group_id}")
    except Exception as e:
        print(f"❌ ERROR sending welcome message: {e}")
        await send_log(context.bot, f"❌ Failed to send welcome: {e}")

    await send_log(context.bot, f"✅ New join: {user.full_name} (@{user.username}) used link {link['invite_link']}")
