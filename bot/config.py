import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "invite_bot")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))
PORT = int(os.getenv("PORT", 8000))
NORMAL_MAX_DAYS = int(os.getenv("NORMAL_MAX_DAYS", 7))
PREMIUM_MAX_DAYS = int(os.getenv("PREMIUM_MAX_DAYS", 30))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
