from motor.motor_asyncio import AsyncIOMotorClient
from bot.config import MONGODB_URI, DATABASE_NAME

client = None
db = None

async def init_db():
    global client, db
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    await create_indexes()
    await ensure_bot_settings()
    print("MongoDB connected and indexes created")

async def create_indexes():
    # Existing collections
    await db.users.create_index("user_id", unique=True)
    await db.invite_links.create_index("link_id", unique=True)
    await db.invite_links.create_index("expiry_date")
    await db.link_usage.create_index("link_id")
    await db.link_usage.create_index("user_id")
    await db.groups.create_index("group_id", unique=True)
    await db.admins.create_index("user_id", unique=True)

    # Multi‑default‑links collection
    await db.default_links.create_index("chat_id", unique=True)

    # Bot settings (mode, active links list)
    await db.bot_settings.create_index("_id", unique=True)

def get_db():
    return db

# ------------------------------------------------------------------
# Bot settings (mode, active links list)
# ------------------------------------------------------------------
async def ensure_bot_settings():
    """Ensure bot_settings collection has default values for the two‑system mode."""
    if await db.bot_settings.count_documents({}) == 0:
        await db.bot_settings.insert_many([
            {"_id": "create_link_mode", "value": False},
            {"_id": "active_link_ids", "value": []}
        ])
        print("Bot settings initialized: create_link_mode=False, active_link_ids=[]")

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

# ------------------------------------------------------------------
# Multi‑default‑link templates (System 1)
# ------------------------------------------------------------------
async def get_default_links():
    """Return all default link templates as a list."""
    cursor = db.default_links.find()
    return await cursor.to_list(None)

async def set_default_link(chat_id: int, expiry_seconds: int, max_uses: int):
    """Add or update a default link template for a specific chat."""
    await db.default_links.update_one(
        {"chat_id": chat_id},
        {"$set": {"expiry_seconds": expiry_seconds, "max_uses": max_uses}},
        upsert=True
    )

async def remove_default_link(chat_id: int):
    """Remove a default link template for a chat."""
    await db.default_links.delete_one({"chat_id": chat_id})

async def clear_all_default_links():
    """Remove all default templates."""
    await db.default_links.delete_many({})
