from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, get_bot_setting, get_default_links
from bot.config import OWNER_IDS, LOG_CHANNEL
from bot.utils.helpers import register_user, create_invite_link, revoke_link_by_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Always shows invite link(s) to users – even if they are already members.
    """
    user = update.effective_user
    db = get_db()
    await register_user(user.id, user.username, user.first_name)

    # Owner – show owner panel
    if user.id in OWNER_IDS:
        await update.message.reply_text(
            f"👑 Welcome back, {user.first_name} (Owner).\n\n"
            "📌 Quick Commands:\n"
            "/dashboard - Admin panel\n"
            "/create_link - Create custom link\n"
            "/setdefaultlink - Configure auto-links\n"
            "/setactivelink - Set active links\n"
            "/activelinkmode - Toggle link mode\n"
            "/help - Full command list"
        )
        return

    # Check mode
    create_mode = await get_bot_setting("create_link_mode", False)

    if create_mode:
        # SYSTEM 2: fixed active links
        active_ids = await get_bot_setting("active_link_ids", [])
        if not active_ids:
            await update.message.reply_text(
                "❌ Create-Link Mode is ON but no active links are set.\n"
                "Please contact the owner to set active links using /setactivelink."
            )
            return

        valid_links = []
        for link_id in active_ids:
            link = await db.invite_links.find_one({"link_id": link_id})
            if not link or link.get("is_revoked") or link["expiry_date"] < datetime.utcnow():
                continue
            valid_links.append(link)

        if not valid_links:
            await update.message.reply_text(
                "❌ No active invite links available. All have expired or been revoked.\n"
                "Please wait for the admin to create new links."
            )
            return

        # Build message with links
        lines = ["🔗 Here are your invite links:\n"]
        for link in valid_links:
            group = await db.groups.find_one({"group_id": link["chat_id"]})
            chat_title = group["title"] if group else f"Chat {link['chat_id']}"
            lines.append(f"📢 {chat_title}")
            lines.append(f"✅ {link['invite_link']}")
            lines.append(f"⏰ Expires: {link['expiry_date']}")
            lines.append(f"👥 Remaining uses: {link['max_uses'] - link['current_uses']}")
            lines.append("───────────────────")
        await update.message.reply_text("\n".join(lines))
        return

    else:
        # SYSTEM 1: auto‑generated links per default template
        templates = await get_default_links()
        if not templates:
            await update.message.reply_text(
                "❌ No default invite link templates set.\n"
                "Please contact the admin to run /setdefaultlink for at least one chat."
            )
            return

        valid_links = []
        for tmpl in templates:
            chat_id = tmpl["chat_id"]
            expiry_seconds = tmpl["expiry_seconds"]
            max_uses = tmpl["max_uses"]

            # Check existing link (even if user is already a member)
            existing = await db.invite_links.find_one({
                "creator_id": user.id,
                "chat_id": chat_id,
                "is_revoked": False,
                "expiry_date": {"$gt": datetime.utcnow()}
            })
            if existing and existing["current_uses"] < existing["max_uses"]:
                valid_links.append(existing)
                continue

            # Revoke old links and create new
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
                valid_links.append(link_info)
                if LOG_CHANNEL:
                    await context.bot.send_message(LOG_CHANNEL, f"🔗 New link for user {user.id} in chat {chat_id}: {link_info['invite_link']}")
            except Exception as e:
                print(f"Error creating link for {chat_id}: {e}")

        if not valid_links:
            await update.message.reply_text(
                "❌ Could not create invite links. Please contact the admin.\n"
                f"Error: No valid links generated."
            )
            return

        # Build message with links
        lines = ["🔗 Here are your invite links:\n"]
        for link in valid_links:
            group = await db.groups.find_one({"group_id": link["chat_id"]})
            chat_title = group["title"] if group else f"Chat {link['chat_id']}"
            lines.append(f"📢 {chat_title}")
            lines.append(f"✅ {link['invite_link']}")
            lines.append(f"⏰ Expires: {link['expiry_date']}")
            lines.append(f"👥 Max uses: {link['max_uses']}")
            lines.append("───────────────────")
        await update.message.reply_text("\n".join(lines))
