from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, set_default_link, get_default_links, remove_default_link
from bot.utils.decorators import owner_required

@owner_required
async def set_default_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manage default link templates for multiple chats.
    Commands:
      /setdefaultlink <chat_id> <expiry_seconds> <max_uses>   – add/update template
      /setdefaultlink list                                   – show all templates
      /setdefaultlink remove <chat_id>                       – remove a template
    """
    args = context.args
    if not args:
        await update.message.reply_text(
            "Usage:\n"
            "/setdefaultlink <chat_id> <expiry_seconds> <max_uses> – add/update\n"
            "/setdefaultlink list – show all\n"
            "/setdefaultlink remove <chat_id> – remove"
        )
        return

    if args[0].lower() == "list":
        templates = await get_default_links()
        if not templates:
            await update.message.reply_text("No default templates configured.")
            return
        text = "📋 *Default Link Templates*\n\n"
        for t in templates:
            text += f"• Chat ID: `{t['chat_id']}`\n"
            text += f"  Expiry: {t['expiry_seconds']} sec ({t['expiry_seconds']//3600} hours)\n"
            text += f"  Max uses: {t['max_uses']}\n\n"
        await update.message.reply_text(text, parse_mode="Markdown")
        return

    if args[0].lower() == "remove":
        if len(args) != 2:
            await update.message.reply_text("Usage: /setdefaultlink remove <chat_id>")
            return
        try:
            chat_id = int(args[1])
        except ValueError:
            await update.message.reply_text("Invalid chat ID.")
            return
        await remove_default_link(chat_id)
        await update.message.reply_text(f"✅ Default template for chat {chat_id} removed.")
        return

    # add/update: expect 3 arguments
    if len(args) != 3:
        await update.message.reply_text(
            "Usage: /setdefaultlink <chat_id> <expiry_seconds> <max_uses>\n"
            "Example: /setdefaultlink -1001234567890 604800 1"
        )
        return

    try:
        chat_id = int(args[0])
        expiry_seconds = int(args[1])
        max_uses = int(args[2])
    except ValueError:
        await update.message.reply_text("Invalid numbers. Chat ID must be integer.")
        return

    await set_default_link(chat_id, expiry_seconds, max_uses)
    await update.message.reply_text(
        f"✅ Default invite link template set for chat {chat_id}:\n"
        f"Expiry: {expiry_seconds} seconds ({expiry_seconds//3600} hours)\n"
        f"Max uses: {max_uses}\n\n"
        "Now each user will receive a unique link for this chat on /start (when Create‑Link Mode OFF)."
    )
