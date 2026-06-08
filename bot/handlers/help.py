from telegram import Update
from telegram.ext import ContextTypes
from bot.config import OWNER_ID

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_owner = (user_id == OWNER_ID)

    user_text = (
        "🤖 <b>Invite Link Management Bot</b>\n\n"
        "<b>User Commands</b>\n"
        "• <code>/start</code> – Get your personal invite link (single‑use, with expiry).\n"
        "  If you are already a member, you will see a welcome message.\n"
        "• <code>/help</code> – Show this message.\n\n"
        "<b>How It Works</b>\n"
        "• When you send /start, the bot checks if you are already a member.\n"
        "• If not, it creates a unique invite link just for you.\n"
        "• Click the link → join request → bot auto‑approves → welcome message.\n"
        "• After joining, /start will show a welcome message instead of a new link.\n\n"
        "<b>📌 Rules</b>\n"
        "• Do not share your personal invite link with others.\n"
        "• Expired or revoked links cannot be reused.\n"
        "• Contact an admin if you have any issues.\n\n"
        "Created by @TeamJB_bot"
    )

    admin_text = (
        "\n\n👑 <b>Owner Commands & Features</b>\n\n"
        "The bot has <b>TWO independent invite link systems</b>. "
        "Only one is active for <code>/start</code> at a time.\n\n"
        "───────────────────────────────────────────\n"
        "<b>🔹 SYSTEM 1 – DEFAULT AUTO‑LINK (existing)</b>\n"
        "<code>/setdefaultlink &lt;chat_id&gt; &lt;expiry_seconds&gt; &lt;max_uses&gt;</code> – Configure the default template.\n"
        "   <i>Example:</i> <code>/setdefaultlink -1001234567890 604800 1</code> (7 days, single‑use)\n"
        "   When this system is active, each user gets a unique link on /start.\n"
        "   This system is always available. To use it, turn OFF Create‑Link Mode (see below).\n\n"
        "───────────────────────────────────────────\n"
        "<b>🔹 SYSTEM 2 – CREATE‑LINK MODE (new)</b>\n"
        "Owner creates a custom link, then shares the <b>same</b> link to all users.\n"
        "No new links are generated automatically. When the link expires, you must create a new one.\n\n"
        "• <code>/create_link</code> – Create a custom invite link (select group, expiry, max uses).\n"
        "• <code>/active_links</code> – List all links you have created (with their IDs).\n"
        "• <code>/revoke_link &lt;link_id&gt;</code> – Revoke a specific link.\n"
        "• <code>/setactivelink &lt;link_id&gt;</code> – Choose which link will be shared to users.\n"
        "• <code>/activelinkmode on</code> – Enable Create‑Link Mode. Users will get the active link on /start.\n"
        "• <code>/activelinkmode off</code> – Disable Create‑Link Mode. System 1 takes over.\n"
        "• <code>/defaultlinkstatus</code> – Show current mode, active link, and template status.\n\n"
        "───────────────────────────────────────────\n"
        "<b>🔹 Group & Admin Management</b>\n"
        "• <code>/addgroup &lt;group_id&gt; &lt;title&gt;</code> – Add a single chat to the database.\n"
        "• <code>/addgroups &lt;group_id:title&gt; &lt;group_id:title&gt; …</code> – Add multiple chats at once.\n"
        "• <code>/admins</code> – List all admins and open management menu.\n"
        "• <code>/addadmin &lt;user_id&gt; &lt;role&gt;</code> – Add an admin (role: <code>admin</code> or <code>super_admin</code>).\n\n"
        "───────────────────────────────────────────\n"
        "<b>🔹 Welcome Messages & Log Channels</b>\n"
        "• <code>/settings</code> – Interactive menu to set welcome message and log channel per chat.\n"
        "• <code>/setwelcome &lt;group_id&gt; &lt;message&gt;</code> – Set welcome message (use <code>{user}</code> for name).\n"
        "• <code>/setlogchannel &lt;group_id&gt; &lt;channel_id&gt;</code> – Set where join logs are sent.\n\n"
        "───────────────────────────────────────────\n"
        "<b>🔹 Database & Utilities</b>\n"
        "• <code>/backup</code> – Export all data as JSON file.\n"
        "• <code>/restore</code> – Restore database from a backup file (send the file after command).\n"
        "• <code>/revoke_all</code> – Revoke every active invite link (global).\n"
        "• <code>/stats</code> – View bot statistics (total links, joins, users).\n"
        "• <code>/dashboard</code> – Interactive admin panel with buttons.\n\n"
        "<b>📌 Important Notes</b>\n"
        "• The bot must be an admin in each group/channel with rights:\n"
        "  - <b>Create Invite Links</b>\n"
        "  - <b>Approve Join Requests</b> (for groups)\n"
        "  - <b>Send Messages</b> (for welcome messages)\n"
        "• For channels, auto‑approval is not possible – users join directly via the link.\n"
        "• Settings persist across bot restarts (stored in MongoDB).\n\n"
        "🔗 <b>Need help?</b> Contact @TeamJB_bot"
    )

    if is_owner:
        await update.message.reply_text(
            user_text + admin_text,
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            user_text,
            parse_mode="HTML"
        )
