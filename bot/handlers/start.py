from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.config import OWNER_ID, LOG_CHANNEL
from bot.utils.helpers import register_user, create_invite_link, revoke_link_by_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = get_db()
    await register_user(user.id, user.username, user.first_name)

    # Owner gets different message
    if user.id == OWNER_ID:
        await update.message.reply_text(
            f"Welcome back, {user.first_name} (Owner).\n"
            "Use /setdefaultlink to configure the default invite link template.\n"
            "Use /dashboard to manage everything."
        )
        return

    # Get default template
    template = await db.default_link.find_one({"_id": "template"})
    if not template or template.get("chat_id", 0) == 0:
        await update.message.reply_text(
            "❌ No default invite link template set.\n"
            "Please contact the admin to run `/setdefaultlink`."
        )
        return

    chat_id = template["chat_id"]
    expiry_seconds = template["expiry_seconds"]
    max_uses = template["max_uses"]

    # --- NEW: Check if user is already a member of the target chat ---
    try:
        chat_member = await context.bot.get_chat_member(chat_id, user.id)
        is_member = chat_member.status in ("member", "administrator", "creator")
    except Exception as e:
        # If the bot can't get member info (e.g., not admin, chat not found), assume not member
        print(f"Error checking membership for user {user.id}: {e}")
        is_member = False

    if is_member:
        # User is already a member – show welcome message and do NOT create a new link
        welcome_text = (
            f"Hi {user.first_name},\n\n"
            f"🔹 This bot provides secure invite links for our group/channel.\n"
            f"🔹 You are already a member of our group/channel.\n"
            f"🔹 Your previous invite link has been used and is now disabled.\n\n"
            f"📌 Rules:\n"
            f"• Do not share invite links with others.\n"
            f"• Expired or revoked links cannot be reused.\n"
            f"• Contact an admin if you have any issues.\n\n"
            f"Enjoy your stay! 🚀\n\n"
            f"Created By @TeamJB_bot"
        )
        await update.message.reply_text(welcome_text)
        return

    # --- User is NOT a member → proceed with invite link creation ---
    # Check for any existing active link (not revoked, not expired)
    existing_link = await db.invite_links.find_one({
        "creator_id": user.id,
        "chat_id": chat_id,
        "is_revoked": False,
        "expiry_date": {"$gt": datetime.utcnow()}
    })

    if existing_link and existing_link["current_uses"] < existing_link["max_uses"]:
        # Resend the active link
        remaining = existing_link["max_uses"] - existing_link["current_uses"]
        text = (
            f"✅ Invite link created for you:\n{existing_link['invite_link']}\n\n"
            f"Expires: {existing_link['expiry_date']}\n"
            f"Max uses: {existing_link['max_uses']}\n\n"
            f"You already have an active invite link:\n{existing_link['invite_link']}\n\n"
            f"Expires: {existing_link['expiry_date']}\n"
            f"Remaining uses: {remaining}\n\n"
            "Click the link to join. You will be automatically approved."
        )
        await update.message.reply_text(text)
        return

    # Revoke any old links (if they exist and are not valid)
    old_links = await db.invite_links.find({"creator_id": user.id, "chat_id": chat_id}).to_list(None)
    for old in old_links:
        await revoke_link_by_id(old["link_id"], context.bot)

    # Create a fresh link
    expiry_date = datetime.utcnow() + timedelta(seconds=expiry_seconds)
    try:
        link_info = await create_invite_link(
            bot=context.bot,
            chat_id=chat_id,
            creator_id=user.id,
            expiry_date=expiry_date,
            max_uses=max_uses
        )
        text = (
            f"✅ Invite link created for you:\n{link_info['invite_link']}\n\n"
            f"Expires: {expiry_date}\n"
            f"Max uses: {max_uses}\n\n"
            "Click the link to join. You will be automatically approved."
        )
        await update.message.reply_text(text)
        if LOG_CHANNEL:
            await context.bot.send_message(LOG_CHANNEL, f"🔗 New default link for user {user.id}: {link_info['invite_link']}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to create invite link: {str(e)}")
