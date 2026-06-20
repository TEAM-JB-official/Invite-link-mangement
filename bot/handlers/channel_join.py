from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, get_bot_setting, get_default_links
from bot.config import OWNER_IDS
from bot.utils.helpers import register_user, create_invite_link, revoke_link_by_id

async def handle_new_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Called when a user joins a channel or group where the bot is admin.
    Sends a private message with the user's invite link(s) – same logic as /start.
    """
    chat_member_update = update.chat_member
    # Only act if the new status is "member" and the old status was not member (new join)
    if chat_member_update.new_chat_member.status != "member":
        return
    if chat_member_update.old_chat_member.status in ("member", "administrator", "creator"):
        return   # Not a new join

    user = chat_member_update.new_chat_member.user
    chat_id = chat_member_update.chat.id
    db = get_db()

    # Register user if not exists
    await register_user(user.id, user.username, user.first_name)

    # === Copy logic from start.py ===
    # Owner – no links
    if user.id in OWNER_IDS:
        await context.bot.send_message(
            chat_id=user.id,
            text="Welcome, Owner. Use /dashboard for admin panel."
        )
        return

    create_mode = await get_bot_setting("create_link_mode", False)

    if create_mode:
        # SYSTEM 2: fixed active links
        active_ids = await get_bot_setting("active_link_ids", [])
        if not active_ids:
            await context.bot.send_message(
                chat_id=user.id,
                text="❌ Create-Link Mode is ON but no active links are set.\nContact the owner."
            )
            return

        valid_links = []
        for link_id in active_ids:
            link = await db.invite_links.find_one({"link_id": link_id})
            if not link or link.get("is_revoked") or link["expiry_date"] < datetime.utcnow():
                continue
            valid_links.append(link)

        if not valid_links:
            await context.bot.send_message(
                chat_id=user.id,
                text="❌ No active invite links available. All have expired or been revoked."
            )
            return

        lines = []
        for link in valid_links:
            group = await db.groups.find_one({"group_id": link["chat_id"]})
            chat_title = group["title"] if group else f"Chat {link['chat_id']}"
            lines.append(f"📢 {chat_title}")
            lines.append(f"✅ Invite link:\n{link['invite_link']}")
            lines.append(f"⏰ Expires: {link['expiry_date']}")
            lines.append(f"👥 Remaining uses: {link['max_uses'] - link['current_uses']}")
            lines.append("───────────────────")
        await context.bot.send_message(chat_id=user.id, text="\n".join(lines))
        return

    else:
        # SYSTEM 1: auto‑generated links per default template
        templates = await get_default_links()
        if not templates:
            await context.bot.send_message(
                chat_id=user.id,
                text="❌ No default invite link templates set.\nPlease contact the admin."
            )
            return

        valid_links = []
        for tmpl in templates:
            chat_id_tmpl = tmpl["chat_id"]
            expiry_seconds = tmpl["expiry_seconds"]
            max_uses = tmpl["max_uses"]

            # Skip if user already member of that chat
            try:
                chat_member = await context.bot.get_chat_member(chat_id_tmpl, user.id)
                if chat_member.status in ("member", "administrator", "creator"):
                    continue
            except:
                pass

            # Check existing link
            existing = await db.invite_links.find_one({
                "creator_id": user.id,
                "chat_id": chat_id_tmpl,
                "is_revoked": False,
                "expiry_date": {"$gt": datetime.utcnow()}
            })
            if existing and existing["current_uses"] < existing["max_uses"]:
                valid_links.append(existing)
                continue

            # Revoke old links and create new
            old_links = await db.invite_links.find({"creator_id": user.id, "chat_id": chat_id_tmpl}).to_list(None)
            for old in old_links:
                await revoke_link_by_id(old["link_id"], context.bot)

            expiry_date = datetime.utcnow() + timedelta(seconds=expiry_seconds)
            try:
                link_info = await create_invite_link(
                    bot=context.bot,
                    chat_id=chat_id_tmpl,
                    creator_id=user.id,
                    expiry_date=expiry_date,
                    max_uses=max_uses
                )
                valid_links.append(link_info)
            except Exception as e:
                print(f"Error creating link for {chat_id_tmpl}: {e}")

        if not valid_links:
            await context.bot.send_message(
                chat_id=user.id,
                text=f"Hi {user.first_name},\n\nYou are already a member of all our groups/channels.\nYour previous links have been used."
            )
            return

        lines = []
        for link in valid_links:
            group = await db.groups.find_one({"group_id": link["chat_id"]})
            chat_title = group["title"] if group else f"Chat {link['chat_id']}"
            lines.append(f"📢 {chat_title}")
            lines.append(f"✅ Invite link created for you:\n{link['invite_link']}")
            lines.append(f"⏰ Expires: {link['expiry_date']}")
            lines.append(f"👥 Max uses: {link['max_uses']}")
            lines.append("───────────────────")
        await context.bot.send_message(chat_id=user.id, text="\n".join(lines))
