from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, set_default_link as db_set_default_link, get_default_links, remove_default_link
from bot.utils.decorators import owner_required

@owner_required
async def set_default_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manage default link templates.
    Commands:
      /setdefaultlink <chat_id1> <exp1> <max1> <chat_id2> <exp2> <max2> ...  – add/update multiple
      /setdefaultlink list – show all templates
      /setdefaultlink remove <chat_id> – remove a template
    """
    args = context.args
    if not args:
        await update.message.reply_text(
            "Usage:\n"
            "/setdefaultlink <chat_id> <expiry> <max_uses> – add/update one\n"
            "/setdefaultlink <chat_id1> <exp1> <max1> <chat_id2> <exp2> <max2> ... – add/update multiple\n"
            "/setdefaultlink list – show all templates\n"
            "/setdefaultlink remove <chat_id> – remove a template"
        )
        return

    # Handle "list" command
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

    # Handle "remove" command
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

    # Handle one or more triples (each triple: chat_id expiry max_uses)
    if len(args) % 3 != 0:
        await update.message.reply_text(
            "Usage: /setdefaultlink <chat_id1> <expiry1> <max1> <chat_id2> <expiry2> <max2> ...\n"
            "Example: /setdefaultlink -100111 604800 1 -100222 86400 5"
        )
        return

    added = 0
    errors = []
    for i in range(0, len(args), 3):
        try:
            chat_id = int(args[i])
            expiry = int(args[i+1])
            max_uses = int(args[i+2])
        except ValueError:
            errors.append(f"Invalid numbers at position {i+1}-{i+3}")
            continue
        await db_set_default_link(chat_id, expiry, max_uses)
        added += 1

    await update.message.reply_text(
        f"✅ Added/updated {added} default templates.\n"
        f"Errors: {errors if errors else 'None'}"
    )
