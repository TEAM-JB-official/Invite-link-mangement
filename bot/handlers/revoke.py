from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db
from bot.utils.decorators import admin_required, log_command
from bot.utils.helpers import revoke_link_by_id

@log_command
async def revoke_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /revoke_link <link_id>")
        return
    link_id = context.args[0]
    db = get_db()
    link = await db.invite_links.find_one({"link_id": link_id})
    if not link:
        await update.message.reply_text("Link not found.")
        return
    await revoke_link_by_id(link_id, update.get_bot())
    await update.message.reply_text("Link revoked.")

@log_command
@admin_required
async def revoke_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = get_db()
    links = await db.invite_links.find({"is_revoked": False}).to_list(None)
    for link in links:
        await revoke_link_by_id(link["link_id"], update.get_bot())
    await update.message.reply_text("All active links have been revoked.")
