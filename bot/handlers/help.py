from telegram import Update
from telegram.ext import ContextTypes
from bot.config import OWNER_IDS

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_owner = (user_id in OWNER_IDS)

    user_text = (
        "🤖 Invite Link Management Bot\n\n"
        "🔹 *User Commands*\n"
        "/start – Get your personal invite link (single‑use, with expiry).\n"
        "          If you are already a member, you will see a welcome message.\n"
        "/help – Show this message.\n\n"
        "🔹 *How It Works*\n"
        "• When you send /start, the bot checks if you are already a member.\n"
        "• If not, it creates a unique invite link just for you.\n"
        "• Click the link → join request → bot auto‑approves → welcome message.\n"
        "• After joining, /start will show a welcome message instead of a new link.\n\n"
        "📌 *Rules*\n"
        "• Do not share your personal invite link with others.\n"
        "• Expired or revoked links cannot be reused.\n"
        "• Contact an admin if you have any issues.\n\n"
        "Created by @TeamJB_bot"
    )

    owner_text = (
        "\n\n👑 *Owner Commands & Two Systems*\n\n"
        "The bot has TWO independent invite link systems. Only one is active for /start.\n\n"
        "───────────────────────────────────────────\n"
        "🔹 SYSTEM 1 – DEFAULT AUTO-LINK (always available)\n"
        "/setdefaultlink <chat_id> <expiry_seconds> <max_uses>\n"
        "   Example: /setdefaultlink -1001234567890 604800 1 (7 days, single‑use)\n"
        "   When this system is ACTIVE (Create‑Link Mode OFF), each user gets a unique link on /start.\n"
        "   To use it, make sure Create‑Link Mode is OFF: /activelinkmode off\n\n"
        "───────────────────────────────────────────\n"
        "🔹 SYSTEM 2 – CREATE-LINK MODE (shared link for all users)\n"
        "   Owner creates one custom link, then all users receive the SAME link on /start.\n"
        "   No new links are generated automatically.\n\n"
        "   Step‑by‑step:\n"
        "   1. /create_link – create a custom link (choose group, expiry, max uses)\n"
        "   2. /active_links or /listlinks – see all your links and copy the ID (e.g., +ABCD123)\n"
        "   3. /setactivelink +ABCD123 – set that link as the active one\n"
        "   4. /activelinkmode on – enable Create‑Link Mode\n"
        "   5. Now every /start sends the SAME link.\n"
        "   6. To switch back to System 1: /activelinkmode off\n"
        "   7. Check current status: /defaultlinkstatus\n\n"
        "───────────────────────────────────────────\n"
        "🔹 *Other Owner Commands*\n\n"
        "📌 *Group & Admin Management*\n"
        "/addgroup <group_id> <title> – add a single chat\n"
        "/addgroups <group_id:title> <group_id:title> … – add multiple chats\n"
        "/admins – list all admins and management menu\n"
        "/addadmin <user_id> <role> – add admin (role: admin, super_admin, owner)\n\n"
        "📌 *Welcome Messages & Log Channels*\n"
        "/settings – interactive menu per group\n"
        "/setwelcome <group_id> <message> – set welcome text (use {user} for name)\n"
        "/setlogchannel <group_id> <channel_id> – set where join logs are sent\n\n"
        "📌 *Link Management*\n"
        "/create_link – custom link creation\n"
        "/active_links – list your active links\n"
        "/listlinks – list ALL links (owner only)\n"
        "/revoke_link <link_id> – revoke a specific link\n"
        "/revoke_all – revoke every active link\n"
        "/setactivelink <link_id> – choose shared link for System 2\n"
        "/activelinkmode on/off – enable/disable System 2\n"
        "/defaultlinkstatus – show which system is active\n\n"
        "📌 *Database & Utilities*\n"
        "/backup – export all data as JSON\n"
        "/restore – restore from a backup file (send after command)\n"
        "/stats – bot statistics (links, joins, users)\n"
        "/dashboard – interactive admin panel (buttons)\n\n"
        "───────────────────────────────────────────\n"
        "⚠️ *Important Notes*\n"
        "• The bot must be an admin in each group/channel with rights:\n"
        "   - Create Invite Links\n"
        "   - Approve Join Requests (for groups)\n"
        "   - Send Messages (for welcome messages)\n"
        "• For channels, auto‑approval is not possible – users join directly.\n"
        "• All settings are stored in MongoDB and survive bot restarts.\n\n"
        "🔗 *Need help?* Contact @TeamJB_bot"
    )

    if is_owner:
        await update.message.reply_text(user_text + owner_text)
    else:
        await update.message.reply_text(user_text)
