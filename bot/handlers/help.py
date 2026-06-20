from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.config import OWNER_IDS

# Store help pages
HELP_PAGES = {}

def get_help_pages():
    """Return all help pages"""
    return {
        1: (
            "👑 OWNER HELP - PAGE 1/5\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 SYSTEM OVERVIEW\n"
            "The bot has TWO independent invite link systems.\n"
            "Only ONE system works at a time.\n\n"
            "• /activelinkmode on – Use System 2 (Shared Links)\n"
            "• /activelinkmode off – Use System 1 (Default Links)\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔹 SYSTEM 1 – DEFAULT AUTO-LINKS\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "What it does:\n"
            "Each user gets a UNIQUE invite link when they send /start\n\n"
            "Setup:\n"
            "1. /setdefaultlink chat_id expiry max_uses\n"
            "   Example: /setdefaultlink -1001234567890 86400 1\n\n"
            "   • chat_id – Group/channel ID (get from @get_id_bot)\n"
            "   • expiry – Link validity in seconds\n"
            "     3600=1h | 86400=1d | 604800=7d | 2592000=30d\n"
            "   • max_uses – How many times link can be used\n"
            "     1=once | 10=10 uses | 0=unlimited\n\n"
            "2. /setdefaultlink list – View all templates\n"
            "3. /setdefaultlink remove chat_id – Remove a template\n"
            "4. /activelinkmode off – Activate System 1\n\n"
            "Result: Each user gets their own unique link"
        ),
        2: (
            "👑 OWNER HELP - PAGE 2/5\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔹 SYSTEM 2 – SHARED LINKS\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "What it does:\n"
            "All users receive the SAME invite link when they send /start\n\n"
            "Setup:\n"
            "1. /create_link – Create a custom link (interactive menu)\n"
            "   • Select group/channel\n"
            "   • Choose expiry time\n"
            "   • Choose max uses\n\n"
            "2. Copy the link ID (e.g., +ABC123XYZ)\n\n"
            "3. /setactivelink +ABC123XYZ – Set as active link\n"
            "   • Can set multiple: /setactivelink +ABC +DEF\n"
            "   • Clear all: /setactivelink clear\n\n"
            "4. /activelinkmode on – Activate System 2\n\n"
            "Result: All users get the same link\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔹 LINK MANAGEMENT\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "/create_link – Create custom invite link (interactive)\n"
            "/active_links – View your active links\n"
            "/listlinks – View ALL links (owner only)\n"
            "/revoke_link +ID – Revoke a specific link\n"
            "/revoke_all – Revoke ALL active links\n"
            "/setactivelink +ID – Set active link(s) for System 2\n"
            "/setactivelink clear – Clear all active links\n"
            "/activelinkmode on/off – Switch between systems\n"
            "/defaultlinkstatus – Show current system status"
        ),
        3: (
            "👑 OWNER HELP - PAGE 3/5\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔹 GROUP MANAGEMENT\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "/addgroup group_id title – Register a group\n"
            "  Example: /addgroup -1001234567890 My Group\n\n"
            "/addgroups id1:title1 id2:title2 ... – Add multiple\n"
            "  Example: /addgroups -100111:Group1 -100222:Group2\n\n"
            "/settings – Interactive settings menu per group\n"
            "/setlogchannel group_id channel_id – Set log channel\n"
            "  Example: /setlogchannel -100123 -100456\n\n"
            "/setwelcome group_id message – Set welcome message\n"
            "  Use {user} for user name, {link_creator} for creator\n"
            "  Example: /setwelcome -100123 Welcome {user}!\n\n"
            "/togglewelcome on/off – Enable/disable welcome messages\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔹 ADMIN MANAGEMENT\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "/admins – View all admins with management menu\n"
            "/addadmin user_id role – Add a new admin\n"
            "  Roles: admin, super_admin, owner\n"
            "  Example: /addadmin 123456789 super_admin"
        ),
        4: (
            "👑 OWNER HELP - PAGE 4/5\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔹 DATABASE AND UTILITIES\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "/stats – View bot statistics\n"
            "  • Total links created\n"
            "  • Active links\n"
            "  • Total joins\n"
            "  • Registered users\n\n"
            "/backup – Generate full JSON backup\n"
            "/restore – Restore from backup (send JSON file)\n"
            "/dashboard – Interactive admin panel with buttons\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📊 EXPIRY TIME REFERENCE\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "• 3600     = 1 hour\n"
            "• 21600    = 6 hours\n"
            "• 43200    = 12 hours\n"
            "• 86400    = 24 hours (1 day)\n"
            "• 172800   = 48 hours (2 days)\n"
            "• 604800   = 7 days\n"
            "• 2592000  = 30 days\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔹 QUICK COMMANDS REFERENCE\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "System 1 (Default Links):\n"
            "  /setdefaultlink – Add template\n"
            "  /setdefaultlink list – View templates\n"
            "  /activelinkmode off – Activate\n\n"
            "System 2 (Shared Links):\n"
            "  /create_link – Create link\n"
            "  /setactivelink – Set active link\n"
            "  /activelinkmode on – Activate\n\n"
            "General:\n"
            "  /revoke_all – Clear all links\n"
            "  /defaultlinkstatus – Check status"
        ),
        5: (
            "👑 OWNER HELP - PAGE 5/5\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ IMPORTANT NOTES\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "• Bot MUST be admin in groups/channels with:\n"
            "  ✅ Create Invite Links\n"
            "  ✅ Send Messages (for logs)\n"
            "  ✅ Approve Join Requests (for groups)\n\n"
            "• System 1 vs System 2:\n"
            "  🔹 System 1 = Unique links per user\n"
            "  🔹 System 2 = Same link for all users\n\n"
            "• Only ONE system works at a time\n"
            "• Switch with /activelinkmode on/off\n\n"
            "• All settings stored in MongoDB\n"
            "• Settings survive bot restarts\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔧 TROUBLESHOOTING\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "❌ Bot not creating links\n"
            "→ Check bot is admin with Create Invite Links\n\n"
            "❌ Users not receiving links\n"
            "→ Check bot is admin in the group/channel\n\n"
            "❌ Wrong links showing\n"
            "→ Run /revoke_all to clear old links\n\n"
            "❌ Welcome message showing\n"
            "→ Run /togglewelcome off\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 NEED HELP?\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Contact @TeamJB_bot for support\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
    }

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help with pagination"""
    user_id = update.effective_user.id
    is_owner = (user_id in OWNER_IDS)

    # User help (non-owner) - Plain text
    user_text = (
        "🤖 Invite Link Management Bot\n\n"
        "🔹 User Commands\n"
        "/start – Get your personal invite link\n"
        "/help – Show this message\n\n"
        "🔹 How It Works\n"
        "• Send /start to get your unique invite link\n"
        "• Click the link to join the group/channel\n"
        "• Your link is single-use and expires automatically\n\n"
        "📌 Rules\n"
        "• Never share your personal invite link\n"
        "• Expired links cannot be reused\n"
        "• Contact an admin if you have issues\n\n"
        "Created by @TeamJB_bot"
    )

    if not is_owner:
        await update.message.reply_text(user_text)
        return

    # For owners, show first page with navigation
    pages = get_help_pages()
    keyboard = [
        [
            InlineKeyboardButton("2", callback_data="help_page_2"),
            InlineKeyboardButton("3", callback_data="help_page_3"),
            InlineKeyboardButton("4", callback_data="help_page_4"),
            InlineKeyboardButton("5", callback_data="help_page_5")
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data="help_close")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send user help first
    await update.message.reply_text(user_text)
    
    # Then send owner help page 1 with navigation
    await update.message.reply_text(
        pages[1],
        reply_markup=reply_markup
    )

async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help page navigation"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "help_close":
        await query.edit_message_text(
            "👋 Help closed. Send /help anytime to reopen."
        )
        return
    
    # Extract page number from callback data (help_page_2, help_page_3, etc.)
    page_num = int(data.split("_")[2])
    pages = get_help_pages()
    
    # Build navigation buttons
    keyboard = []
    
    # Page number buttons (1-5)
    row = []
    for i in range(1, 6):
        if i == page_num:
            row.append(InlineKeyboardButton(f"✅ {i}", callback_data=f"help_page_{i}"))
        else:
            row.append(InlineKeyboardButton(f"{i}", callback_data=f"help_page_{i}"))
    keyboard.append(row)
    
    # Close button
    keyboard.append([InlineKeyboardButton("❌ Close", callback_data="help_close")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        pages[page_num],
        reply_markup=reply_markup
    )
