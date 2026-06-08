from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, get_bot_setting
from bot.config import OWNER_IDS, LOG_CHANNEL   # list of owner IDs
from bot.utils.helpers import register_user, create_invite_link, revoke_link_by_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = get_db()
    await register_user(user.id, user.username, user.first_name)

    # Owner welcome (no link generated) – check if user is in OWNER_IDS
    if user.id in OWNER_IDS:
        await update.message.reply_text(
            f"Welcome back, {user.first_name} (Owner).\n"
            "Use /setdefaultlink to configure default auto‑links.\n"
            "Use /create_link to make custom links, then /setactivelink and /activelinkmode on to share them.\n"
            "Use /dashboard for admin panel."
        )
        return

    # --- Check which mode is active ---
    create_link_mode = await get_bot_setting("create_link_mode", False)

    if create_link_mode:
        # Create-Link Mode is ON – use the shared active link
        active_link_id = await get_bot_setting("active_link_id", None)
        if not active_link_id:
            await update.message.reply_text(
                "❌ Create-Link Mode is ON but no active link is set.\n"
                "Please contact the owner to set an active link using /setactivelink."
            )
            return

        active_link = await db.invite_links.find_one({"link_id": active_link_id})
        if not active_link or active_link.get("is_revoked"):
            await update.message.reply_text(
                "❌ The active invite link has been revoked. Please contact the owner."
            )
            return

        if active_link["expiry_date"] < datetime.utcnow():
            await update.message.reply_text(
                "❌ Current invite link has expired. Please wait for admin to create a new link."
            )
            return

        # Check if user is already a member of the target chat
        try:
            chat_member = await context.bot.get_chat_member(active_link["chat_id"], user.id)
            is_member = chat_member.status in ("member", "administrator", "creator")
        except:
            is_member = False

        if is_member:
            await update.message.reply_text(
                f"Hi {user.first_name},\n\n"
                "🔹 You are already a member of our group/channel.\n"
                "🔹 Your previous invite link has been used and is now disabled.\n\n"
                "📌 Rules:\n"
                "• Do not share invite links with others.\n"
                "• Expired or revoked links cannot be reused.\n"
                "• Contact an admin if you have any issues.\n\n"
                "Enjoy your stay! 🚀\n\n"
                "Created By @TeamJB_bot"
            )
            return

        # Not a member – send the active link
        remaining = active_link["max_uses"] - active_link["current_uses"]
        text = (
            f"✅ Active invite link:\n{active_link['invite_link']}\n\n"
            f"Expires: {active_link['expiry_date']}\n"
            f"Remaining uses: {remaining}\n\n"
            "Click the link to join. You will be automatically approved."
        )
        await update.message.reply_text(text)
        return

    else:
        # Default Auto-Link Mode – original behaviour (unchanged)
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

        # Check membership
        try:
            chat_member = await context.bot.get_chat_member(chat_id, user.id)
            is_member = chat_member.status in ("member", "administrator", "creator")
        except:
            is_member = False

        if is_member:
            await update.message.reply_text(
                f"Hi {user.first_name},\n\n"
                "🔹 You are already a member of our group/channel.\n"
                "🔹 Your previous invite link has been used and is now disabled.\n\n"
                "📌 Rules:\n"
                "• Do not share invite links with others.\n"
                "• Expired or revoked links cannot be reused.\n"
                "• Contact an admin if you have any issues.\n\n"
                "Enjoy your stay! 🚀\n\n"
                "Created By @TeamJB_bot"
            )
            return

        # Create new unique link (original logic)
        old_links = await db.invite_links.find({"creator_id": user.id, "chat_id": chat_id}).to_list(None)
        for old in old_links:
            await revoke_link_by_id(old["link_id"], context.bot)

        expiry_date = datetime.utcnow() + timedelta(seconds=expiry_seconds)
        try:
            link_info = await create_invite_link(
                bot=context.bot,
                chat_id=chat_id,
                creator_id=user.id,
                expiry_date=expiry_date,
                max_uses=max_uses
            )
            await update.message.reply_text(
                f"✅ Invite link created for you:\n{link_info['invite_link']}\n\n"
                f"Expires: {expiry_date}\n"
                f"Max uses: {max_uses}\n\n"
                "Click the link to join. You will be automatically approved."
            )
            if LOG_CHANNEL:
                await context.bot.send_message(LOG_CHANNEL, f"🔗 New default link for user {user.id}: {link_info['invite_link']}")
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to create invite link: {str(e)}")
