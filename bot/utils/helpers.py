import random
import string
from datetime import datetime, timedelta
from telegram import Bot
from bot.database.mongo import get_db
from bot.config import LOG_CHANNEL

def generate_referral_code(user_id):
    return f"REF{user_id}{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"

async def register_user(user_id, username, first_name):
    db = get_db()
    existing = await db.users.find_one({"user_id": user_id})
    if not existing:
        code = generate_referral_code(user_id)
        await db.users.insert_one({
            "user_id": user_id,
            "username": username,
            "first_name": first_name,
            "is_verified": False,
            "is_premium": False,
            "premium_expiry": None,
            "referral_code": code,
            "referred_by": None,
            "created_at": datetime.utcnow()
        })
        return True
    return False

async def create_invite_link(bot: Bot, chat_id: int, creator_id: int, expiry_date: datetime, max_uses: int):
    """
    Creates invite link:
    - Groups: uses creates_join_request=True (requires admin approval)
    - Channels: uses member_limit (direct join)
    """
    db = get_db()
    chat = await bot.get_chat(chat_id)
    is_group = chat.type in ["group", "supergroup"]
    
    if is_group:
        # Groups: requires admin approval
        link = await bot.create_chat_invite_link(
            chat_id=chat_id,
            expire_date=expiry_date,
            creates_join_request=True
        )
    else:
        # Channels: direct join
        link = await bot.create_chat_invite_link(
            chat_id=chat_id,
            expire_date=expiry_date,
            member_limit=max_uses
        )
    
    link_doc = {
        "link_id": link.invite_link.split("/")[-1],
        "invite_link": link.invite_link,
        "chat_id": chat_id,
        "creator_id": creator_id,
        "max_uses": max_uses,
        "current_uses": 0,
        "expiry_date": expiry_date,
        "created_at": datetime.utcnow(),
        "is_revoked": False,
        "is_group": is_group
    }
    await db.invite_links.insert_one(link_doc)
    return link_doc

async def revoke_link_by_id(link_id: str, bot: Bot):
    db = get_db()
    link = await db.invite_links.find_one({"link_id": link_id})
    if not link or link.get("is_revoked"):
        return
    try:
        await bot.edit_chat_invite_link(
            chat_id=link["chat_id"],
            invite_link=link["invite_link"],
            expire_date=datetime.utcnow(),
            member_limit=0
        )
    except Exception as e:
        print(f"Error revoking link {link_id}: {e}")
    await db.invite_links.update_one({"link_id": link_id}, {"$set": {"is_revoked": True}})

def format_link_info(link):
    return (
        f"🔗 {link['invite_link']}\n"
        f"📊 Uses: {link['current_uses']}/{link['max_uses']}\n"
        f"⏰ Expires: {link['expiry_date']}\n"
        f"🆔 ID: `{link['link_id']}`\n\n"
    )

async def send_log(bot: Bot, message: str):
    if LOG_CHANNEL:
        try:
            await bot.send_message(LOG_CHANNEL, message)
        except Exception as e:
            print(f"Failed to send log: {e}")

async def send_welcome(bot: Bot, chat_id: int, user, creator_id: int):
    # NOT USED – no welcome messages
    pass
