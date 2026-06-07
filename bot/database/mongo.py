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

def get_db():
    return db
