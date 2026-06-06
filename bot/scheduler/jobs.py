import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.database.mongo import get_db
from bot.utils.helpers import revoke_link_by_id

async def cleanup_expired_links(bot):
    db = get_db()
    expired = await db.invite_links.find({
        "expiry_date": {"$lt": datetime.utcnow()},
        "is_revoked": False
    }).to_list(None)
    for link in expired:
        await revoke_link_by_id(link["link_id"], bot)
    if expired:
        logging.info(f"Cleaned up {len(expired)} expired links")

async def update_premium_status():
    db = get_db()
    now = datetime.utcnow()
    await db.users.update_many(
        {"premium_expiry": {"$lt": now}, "is_premium": True},
        {"$set": {"is_premium": False}}
    )
    await db.premium_users.delete_many({"expiry_date": {"$lt": now}})

def setup_scheduler(bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cleanup_expired_links, 'interval', minutes=1, args=[bot])
    scheduler.add_job(update_premium_status, 'interval', hours=1)
    scheduler.start()
    return scheduler
