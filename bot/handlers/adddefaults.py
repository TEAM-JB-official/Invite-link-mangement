from telegram import Update
from telegram.ext import ContextTypes
from bot.database.mongo import get_db, set_default_link
from bot.utils.decorators import owner_required

@owner_required
async def adddefaults(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Add multiple default link templates in one command.
    Usage: /adddefaults <chat_id1> <exp1> <max1> <chat_id2> <exp2> <max2> ...
    Example: /adddefaults -100111 604800 1 -100222 86400 5
    """
    args = context.args
    if len(args) % 3 != 0:
        await update.message.reply_text(
            "Usage: /adddefaults <chat_id1> <expiry1> <max1> <chat_id2> <expiry2> <max2> ...\n"
            "Example: /adddefaults -1001111111111 604800 1 -1002222222222 86400 5"
        )
        return

    db = get_db()
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
        await set_default_link(chat_id, expiry, max_uses)
        added += 1

    await update.message.reply_text(
        f"✅ Added/updated {added} default templates.\n"
        f"Errors: {errors if errors else 'None'}"
    )
