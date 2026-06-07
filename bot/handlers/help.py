from telegram import Update
from telegram.ext import ContextTypes
from bot.config import OWNER_ID

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_owner = (user_id == OWNER_ID)

    user_text = (
        "🤖 Invite Link Management Bot\n\n"
        "User Commands\n"
        "/start – Get your personal invite link (single‑use, with expiry).\n"
        "           If you are already a member, you will see a welcome message.\n\n"
        "/create_link – Create a custom invite link (choose group, expiry, max uses).\n"
        "/active_links – List all your active invite links.\n"
        "/revoke_link <link_id> – Revoke a specific invite link (use the ID from /active_links).\n"
        "/stats – View bot statistics (total links, joins, users, etc.).\n"
        "/dashboard – Open the interactive admin panel (buttons for all actions).\n"
        "/help – Show this message.\n\n"
        "How It Works\n"
        "• Each user receives a unique invite link on /start.\n"
        "• The link is single‑use (or limited uses) and expires after the set time.\n"
        "• When you click the link, you send a join request – the bot auto‑approves instantly.\n"
        "• After joining, the link is revoked and cannot be reused.\n"
        "• If you run /start again after joining, you will see a welcome message instead of a new link.\n\n"
        "Need a different invite link?\n"
        "Use /create_link to make a custom link for any group/channel where the bot is admin.\n\n"
        "📌 Rules\n"
        "• Do not share your personal invite link with others.\n"
        "• Expired or revoked links cannot be reused.\n"
        "• Contact an admin if you have any issues.\n\n"
        "Created By @TeamJB_bot"
    )

    admin_text = (
        "\n\n👑 Admin Commands (Owner Only)\n\n"
        "/setdefaultlink <chat_id> <expiry_seconds> <max_uses> – Set the default invite link template.\n"
        "   Example: /setdefaultlink -1001234567890 604800 1 (7 days, single‑use)\n\n"
        "/addgroup <group_id> <title> – Manually add a group/channel to the database.\n\n"
        "/revoke_all – Revoke all active invite links (global).\n"
        "/backup – Export the entire database as a JSON file.\n"
        "/restore – Restore the database from a backup file (send the file after the command).\n"
        "/admins – Manage other admins (add/remove roles).\n"
        "/settings – Configure welcome messages and log channels per group.\n\n"
        "Important\n"
        "• The bot must be an admin in each group/channel with rights:\n"
        "  - Create Invite Links\n"
        "  - Approve Join Requests (for groups)\n"
        "  - Send Messages (for welcome messages)\n"
        "• For channels, auto‑approval is not possible – users join directly.\n\n"
        "📌 Default link template\n"
        "When a new user runs /start, the bot uses this template to create their personal invite link.\n"
        "You can change it anytime – new users will get the new settings.\n\n"
        "🔗 Need help?\n"
        "Contact the bot developer: @TeamJB_bot"
    )

    if is_owner:
        await update.message.reply_text(user_text + admin_text)
    else:
        await update.message.reply_text(user_text)
