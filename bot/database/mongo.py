from motor.motor_asyncio import AsyncIOMotorClient
from bot.config import MONGODB_URI, DATABASE_NAME

client = None
db = None

async def init_db():
    global client, db
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    await create_indexes()
    await ensure_default_settings()
    await ensure_settings()   # <-- NEW: initialize bot settings
    print("MongoDB connected and indexes created")

async def create_indexes():
    await db.users.create_index("user_id", unique=True)
    await db.invite_links.create_index("link_id", unique=True)
    await db.invite_links.create_index("expiry_date")
    await db.link_usage.create_index("link_id")
    await db.link_usage.create_index("user_id")
    await db.groups.create_index("group_id", unique=True)
    await db.admins.create_index("user_id", unique=True)

async def ensure_default_settings():
    existing = await db.default_link.find_one({"_id": "template"})
    if not existing:
        await db.default_link.insert_one({
            "_id": "template",
            "chat_id": 0,
            "expiry_seconds": 604800,   # 7 days
            "max_uses": 1
        })
        print("Default link template created (inactive). Use /setdefaultlink to activate.")

# ----- NEW FUNCTIONS FOR BOT SETTINGS (create_link_mode, active_link_id) -----
async def ensure_settings():
    """Ensure bot_settings collection has default values for the two‑system mode."""
    if await db.bot_settings.count_documents({}) == 0:
        await db.bot_settings.insert_many([
            {"_id": "create_link_mode", "value": False},
            {"_id": "active_link_id", "value": None}
        ])
        print("Bot settings initialized: create_link_mode=False, active_link_id=None")

async def get_bot_setting(key: str, default=None):
    """Get a setting from bot_settings collection."""
    doc = await db.bot_settings.find_one({"_id": key})
    return doc["value"] if doc else default

async def set_bot_setting(key: str, value):
    """Set a setting in bot_settings collection."""
    await db.bot_settings.update_one(
        {"_id": key},
        {"$set": {"value": value}},
        upsert=True
    )
# -------------------------------------------------------------

def get_db():
    return db
