import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8205160181:AAGK2wBXe_uaR_jqN6iuLhAY63Q5f0gEP4Q")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://rs92573993688:pVf4EeDuRi2o92ex@cluster0.9u29q.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = os.getenv("DATABASE_NAME", "invite_bot")
OWNER_ID = int(os.getenv("OWNER_ID", "8043316865"))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1003974194245"))
PORT = int(os.getenv("PORT", 8000))
NORMAL_MAX_DAYS = int(os.getenv("NORMAL_MAX_DAYS", 7))
PREMIUM_MAX_DAYS = int(os.getenv("PREMIUM_MAX_DAYS", 30))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
