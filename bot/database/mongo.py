from motor.motor_asyncio import AsyncIOMotorClient
from bot.config import MONGODB_URI, DATABASE_NAME

client = None
db = None


async def init_db():
    global client, db

    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]

    await create_indexes()

    # Create default invite link template
    existing = await db.default_link.find_one({"_id": "template"})

    if not existing:
        await db.default_link.insert_one({
            "_id": "template",
            "group_id": -1003985321670,  # Replace with your group ID
            "expiry_seconds": 86400,     # 1 day
            "max_uses": 1                # Single-use link
        })

    print("MongoDB connected and indexes created")


async def create_indexes():
    await db.users.create_index("user_id", unique=True)
    await db.users.create_index("referral_code", unique=True, sparse=True)

    await db.invite_links.create_index("link_id", unique=True)
    await db.invite_links.create_index("expiry_date")

    await db.link_usage.create_index("link_id")
    await db.link_usage.create_index("user_id")

    await db.groups.create_index("group_id", unique=True)
    await db.admins.create_index("user_id", unique=True)

    await db.settings.create_index("key", unique=True)


def get_db():
    return db
