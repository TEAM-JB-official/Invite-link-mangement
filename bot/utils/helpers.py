import random
import string
from datetime import datetime, timedelta
from telegram import Bot
from bot.database.mongo import get_db
from bot.config import LOG_CHANNEL, NORMAL_MAX_DAYS, PREMIUM_MAX_DAYS

def generate_referral_code(user_id):
    return f"REF{user_id}{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"

async def grant_premium(user_id, days=1):
    db = get_db()
    now = datetime.utcnow()
    user = await db.users.find_one({"user_id": user_id})
    if user and user.get("premium_expiry") and user["premium_expiry"] > now:
        new_expiry = user["premium_expiry"] + timedelta(days=days)
    else:
        new_expiry = now + timedelta(days=days)
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"is_premium": True, "premium_expiry": new_expiry}}
    )
    await db.premium_users.update_one(
        {"user_id": user_id},
        {"$set": {"expiry_date": new_expiry, "plan_type": "referral"}},
        upsert=True
    )

async def create_invite_link(bot: Bot, group_id: int, creator_id: int, expiry_date: datetime, max_uses: int):
    db = get_db()
    link = await bot.create_chat_invite_link(
        chat_id=group_id,
        expire_date=expiry_date,
        member_limit=max_uses,
        creates_join_request=True
    )
    link_doc = {
        "link_id": link.invite_link.split("/")[-1],
        "invite_link": link.invite_link,
        "group_id": group_id,
        "creator_id": creator_id,
        "max_uses": max_uses,
        "current_uses": 0,
        "expiry_date": expiry_date,
        "created_at": datetime.utcnow(),
        "is_revoked": False
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
            chat_id=link["group_id"],
            invite_link=link["invite_link"],
            expire_date=datetime.utcnow(),
            member_limit=0
        )
    except Exception as e:
        print(f"Error revoking link: {e}")
    await db.invite_links.update_one({"link_id": link_id}, {"$set": {"is_revoked": True}})

def format_link_info(link):
    return (
        f"🔗 {link['invite_link']}\n"
        f"📊 Uses: {link['current_uses']}/{link['max_uses']}\n"
        f"⏰ Expires: {link['expiry_date']}\n"
        f"🆔 ID: `{link['link_id']}`\n\n"
    )
