import json
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import owner_only, log_command

@log_command
@owner_only
async def backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    collections = ["users", "groups", "invite_links", "link_usage", "admins", "premium_users", "referrals", "settings"]
    backup_data = {}
    for coll in collections:
        cursor = db[coll].find({})
        backup_data[coll] = await cursor.to_list(None)
    # Convert ObjectId to string for JSON
    backup_json = json.dumps(backup_data, default=str, indent=2)
    filename = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        f.write(backup_json)
    await update.message.reply_document(document=open(filename, "rb"), filename=filename)
    # Optionally store record
    await db.backups.insert_one({"filename": filename, "created_by": update.effective_user.id, "created_at": datetime.utcnow()})

@log_command
@owner_only
async def restore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("Please send a backup JSON file.")
        return
    file = await update.message.document.get_file()
    await file.download_to_drive("restore_temp.json")
    with open("restore_temp.json", "r") as f:
        data = json.load(f)
    db = get_db()
    for coll_name, docs in data.items():
        await db[coll_name].delete_many({})
        if docs:
            await db[coll_name].insert_many(docs)
    await update.message.reply_text("Restore completed.")
