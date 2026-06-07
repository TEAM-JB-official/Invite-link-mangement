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
        logging.info(f"Cleaned up expired link {link['link_id']}")

def setup_scheduler(bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(cleanup_expired_links, 'interval', minutes=1, args=[bot])
    scheduler.start()
    return scheduler
