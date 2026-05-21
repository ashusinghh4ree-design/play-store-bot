from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    Update,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

import sqlite3

# ================= CONFIG =================

TOKEN = "8927974382:AAG6jx9Lm960xqUvaq8_tjjOzRxFI-Obl-A"

ADMIN_ID = 8575787439

BOT_USERNAME = "FreeRedeemCodez1Robot"

CHANNEL_1 = -1002490723980
CHANNEL_2 = -1003599814306

IMAGE_URL = "https://i.ibb.co/W4SpQX1C/IMG-20260521-090418-265.jpg"

POINTS_PER_REFERRAL = 20
MINIMUM_WITHDRAW = 100

# ================= GLOBAL MODES =================

BROADCAST_MODE = False
BAN_MODE = False
GIFT_MODE = False

# ================= DATABASE =================

db = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    referrals INTEGER DEFAULT 0,
    invited_by INTEGER,
    verified INTEGER DEFAULT 0,
    banned INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS withdraws (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    gmail TEXT,
    username TEXT,
    status TEXT
)
""")

db.commit()

# ================= CHECK BANNED =================

async def is_banned(user_id):

    cursor.execute(
        """
        SELECT banned
        FROM users
        WHERE user_id=?
        """,
        (user_id,)
    )

    data = cursor.fetchone()

    if data and data[0] == 1:
        return True

    return False

# ================= JOIN BUTTONS =================

def join_buttons():

    keyboard = [

        [
            InlineKeyboardButton(
                "📢 JOIN CHANNEL 1",
                url="https://t.me/+VqJTt74UgI4xOTI1",
            )
        ],

        [
            InlineKeyboardButton(
                "📢 JOIN CHANNEL 2",
                url="https://t.me/+f1s1iq_weZk5OGRl",
            )
        ],

        [
            InlineKeyboardButton(
                "✅ JOINED",
                callback_data="verify",
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

# ================= BOTTOM MENU =================

def bottom_menu():

    keyboard = [

        [
            KeyboardButton("💰 Wallet"),
            KeyboardButton("🎁 Gift Code")
        ],

        [
            KeyboardButton("👥 Referral Link"),
            KeyboardButton("💎 Withdraw")
        ],

        [
            KeyboardButton("☎️ Support"),
            KeyboardButton("🏠 Home")
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

# ================= ADMIN BUTTONS =================

def admin_buttons():

    keyboard = [

        [
            InlineKeyboardButton(
                "🎁 ISSUE CODE",
                callback_data="giftcode"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 BROADCAST",
                callback_data="broadcast"
            )
        ],

        [
            InlineKeyboardButton(
                "🚫 BAN USER",
                callback_data="banuser"
            )
        ],

        [
            InlineKeyboardButton(
                "👥 USERS",
                callback_data="users"
            )
        ],

        [
            InlineKeyboardButton(
                "📦 WITHDRAWS",
                callback_data="withdraws"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

# ================= CHECK JOIN =================

async def check_join(bot, user_id, channel_id):

    try:

        member = await bot.get_chat_member(
            channel_id,
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator",
        ]

    except:
        return False

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if await is_banned(user_id):
        return

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE user_id=?
        """,
        (user_id,)
    )

    data = cursor.fetchone()

    referrer = None

    if context.args:

        try:
            referrer = int(context.args[0])
        except:
            pass

    if not data:

        invited_by = None

        if referrer and referrer != user_id:
            invited_by = referrer

        cursor.execute(
            """
            INSERT OR IGNORE INTO users
            (user_id, invited_by)
            VALUES (?, ?)
            """,
            (
                user_id,
                invited_by
            )
        )

        db.commit()

    caption = """
💎 FREE PLAY STORE CODES

🔥 Premium Rewards
⚡ Instant Verification
📈 Daily Giveaways

━━━━━━━━━━━━━━

➊ Join Both Channels
➋ Click Joined
➌ Unlock Rewards
"""

    await context.bot.send_photo(
        chat_id=user_id,
        photo=IMAGE_URL,
        caption=caption,
        reply_markup=join_buttons(),
    )

# ================= VERIFY =================

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    if await is_banned(user_id):
        return

    joined1 = await check_join(
        context.bot,
        user_id,
        CHANNEL_1
    )

    joined2 = await check_join(
        context.bot,
        user_id,
        CHANNEL_2
    )

    if joined1 and joined2:

        cursor.execute(
            """
            SELECT verified, invited_by
            FROM users
            WHERE user_id=?
            """,
            (user_id,)
        )

        user_data = cursor.fetchone()

        if user_data and user_data[0] == 0:

            invited_by = user_data[1]

            cursor.execute(
                """
                UPDATE users
                SET verified=1
                WHERE user_id=?
                """,
                (user_id,)
            )

            if invited_by:

                cursor.execute(
                    """
                    UPDATE users
                    SET points = points + ?,
                    referrals = referrals + 1
                    WHERE user_id=?
                    """,
                    (
                        POINTS_PER_REFERRAL,
                        invited_by
                    )
                )

                try:

                    await context.bot.send_message(
                        invited_by,
                        f"""
🎉 NEW REFERRAL COMPLETED

👤 User ID: {user_id}

💰 +{POINTS_PER_REFERRAL} Points Added
"""
                    )

                except:
                    pass

            db.commit()

        await query.edit_message_caption(
            caption="""
✅ VERIFICATION SUCCESSFUL

💎 Reward Access Unlocked
"""
        )

        await query.message.reply_text(
            "🏠 MAIN MENU",
            reply_markup=bottom_menu()
        )

    else:

        await query.edit_message_caption(
            caption="""
❌ JOIN BOTH CHANNELS FIRST
""",
            reply_markup=join_buttons(),
        )

# ================= USER MESSAGES =================

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global BROADCAST_MODE
    global BAN_MODE
    global GIFT_MODE

    user_id = update.effective_user.id

    if await is_banned(user_id):
        return

    text = update.message.text

    # ================= BROADCAST =================

    if BROADCAST_MODE and user_id == ADMIN_ID:

        cursor.execute(
            "SELECT user_id FROM users"
        )

        users = cursor.fetchall()

        success = 0

        for user in users:

            try:

                await context.bot.send_message(
                    user[0],
                    text
                )

                success += 1

            except:
                pass

        await update.message.reply_text(
            f"✅ Broadcast Sent To {success} Users"
        )

        BROADCAST_MODE = False

        return

    # ================= BAN =================

    if BAN_MODE and user_id == ADMIN_ID:

        try:

            target = int(text)

            cursor.execute(
                """
                UPDATE users
                SET banned=1
                WHERE user_id=?
                """,
                (target,)
            )

            db.commit()

            try:

                await context.bot.send_message(
                    target,
                    """
🚫 YOU ARE BANNED

Reason:
Spam Referral Activity
"""
                )

            except:
                pass

            await update.message.reply_text(
                "✅ User Banned Successfully"
            )

        except:

            await update.message.reply_text(
                "❌ Invalid User ID"
            )

        BAN_MODE = False

        return

    # ================= GIFT =================

    if GIFT_MODE and user_id == ADMIN_ID:

        try:

            split = text.split()

            target = int(split[0])

            code = split[1]

            await context.bot.send_message(
                target,
                f"""
🎁 YOUR GIFT CODE

`{code}`
""",
                parse_mode="Markdown"
            )

            await update.message.reply_text(
                "✅ Gift Code Sent"
            )

        except:

            await update.message.reply_text(
                "❌ Invalid Format"
            )

        GIFT_MODE = False

        return

    # ================= WALLET =================

    if text == "💰 Wallet":

        cursor.execute(
            """
            SELECT points, referrals
            FROM users
            WHERE user_id=?
            """,
            (user_id,)
        )

        data = cursor.fetchone()

        if not data:

            await update.message.reply_text(
                "❌ Use /start First"
            )

            return

        points = data[0] or 0
        referrals = data[1] or 0

        await update.message.reply_text(
            f"""
💰 YOUR WALLET

👥 Referrals: {referrals}
⭐ Points: {points}

🎁 Per Referral: {POINTS_PER_REFERRAL}
💎 Minimum Withdraw: {MINIMUM_WITHDRAW}
"""
        )

    # ================= REFERRAL =================

    elif text == "👥 Referral Link":

        link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

        cursor.execute(
            """
            SELECT points, referrals
            FROM users
            WHERE user_id=?
            """,
            (user_id,)
        )

        data = cursor.fetchone()

        points = data[0] if data else 0
        referrals = data[1] if data else 0

        await update.message.reply_text(
            f"""
👥 YOUR REFERRAL LINK

{link}

👤 Referrals: {referrals}
⭐ Points: {points}
"""
        )

    # ================= SUPPORT =================

    elif text == "☎️ Support":

        await update.message.reply_text(
            "☎️ Support: @Genzayu"
        )

    # ================= HOME =================

    elif text == "🏠 Home":

        caption = """
💎 FREE PLAY STORE REDEEM CODES

🔥 Daily Premium Rewards
⚡ Instant Withdraw System
📈 Trusted Reward Community

━━━━━━━━━━━━━━

🎁 Available Rewards:

• Play Store Codes
• Premium Gift Codes
• Daily Giveaway Access
• Referral Rewards

━━━━━━━━━━━━━━

👥 Invite Friends & Earn More
"""

        await update.message.reply_photo(
            photo=IMAGE_URL,
            caption=caption,
            reply_markup=bottom_menu()
        )

    # ================= GIFT =================

    elif text == "🎁 Gift Code":

        await update.message.reply_text(
            "🎁 Gift Codes Will Be Sent By Admin"
        )

    # ================= WITHDRAW =================

    elif text == "💎 Withdraw":

        cursor.execute(
            """
            SELECT points
            FROM users
            WHERE user_id=?
            """,
            (user_id,)
        )

        data = cursor.fetchone()

        points = data[0] if data else 0

        if points < MINIMUM_WITHDRAW:

            await update.message.reply_text(
                f"❌ Need {MINIMUM_WITHDRAW} Points"
            )

            return

        context.user_data["withdraw"] = True

        await update.message.reply_text(
            "📧 Send Gmail Address"
        )

    # ================= WITHDRAW GMAIL =================

    elif context.user_data.get("withdraw"):

        gmail = text

        context.user_data["gmail"] = gmail

        context.user_data["withdraw"] = False
        context.user_data["username"] = True

        await update.message.reply_text(
            "👤 Send Telegram Username"
        )

    # ================= WITHDRAW USERNAME =================

    elif context.user_data.get("username"):

        username = text

        gmail = context.user_data["gmail"]

        cursor.execute(
            """
            INSERT INTO withdraws
            (user_id, gmail, username, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                user_id,
                gmail,
                username,
                "pending"
            )
        )

        cursor.execute(
            """
            UPDATE users
            SET points = points - ?
            WHERE user_id=?
            """,
            (
                MINIMUM_WITHDRAW,
                user_id
            )
        )

        db.commit()

        context.user_data["username"] = False

        await update.message.reply_text(
            "✅ Withdraw Request Submitted"
        )

        await context.bot.send_message(
            ADMIN_ID,
            f"""
🚨 NEW WITHDRAW REQUEST

👤 User ID: {user_id}
📧 Gmail: {gmail}
🔗 Username: {username}
"""
        )

# ================= ADMIN =================

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    users = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM withdraws
        WHERE status='pending'
        """
    )

    withdraws = cursor.fetchone()[0]

    text = f"""
⚙️ ADMIN PANEL

👥 USERS: {users}
📦 WITHDRAWS: {withdraws}
"""

    await update.message.reply_text(
        text,
        reply_markup=admin_buttons()
    )

# ================= ADMIN CALLBACKS =================

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global BROADCAST_MODE
    global BAN_MODE
    global GIFT_MODE

    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        return

    await query.answer()

    if query.data == "users":

        cursor.execute(
            "SELECT COUNT(*) FROM users"
        )

        users = cursor.fetchone()[0]

        await query.message.reply_text(
            f"👥 TOTAL USERS: {users}"
        )

    elif query.data == "withdraws":

        cursor.execute(
            """
            SELECT id, user_id, gmail, username
            FROM withdraws
            WHERE status='pending'
            """
        )

        data = cursor.fetchall()

        if not data:

            await query.message.reply_text(
                "❌ No Pending Withdraws"
            )

            return

        text = "📦 PENDING WITHDRAWS\n\n"

        for row in data:

            text += f"""
🆔 ID: {row[0]}
👤 USER: {row[1]}
📧 GMAIL: {row[2]}
🔗 USERNAME: {row[3]}

━━━━━━━━━━━━━━
"""

        await query.message.reply_text(text)

    elif query.data == "giftcode":

        GIFT_MODE = True

        await query.message.reply_text(
            "🎁 Send:\n\nuser_id code"
        )

    elif query.data == "broadcast":

        BROADCAST_MODE = True

        await query.message.reply_text(
            "📢 Send Broadcast Message"
        )

    elif query.data == "banuser":

        BAN_MODE = True

        await query.message.reply_text(
            "🚫 Send User ID"
        )

# ================= MAIN =================

app = Application.builder().token(TOKEN).build()

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    CommandHandler(
        "admin",
        admin
    )
)

app.add_handler(
    CallbackQueryHandler(
        verify,
        pattern="^verify$"
    )
)

app.add_handler(
    CallbackQueryHandler(
        admin_handler,
        pattern="^(giftcode|broadcast|banuser|users|withdraws)$"
    )
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        messages
    )
)

print("BOT RUNNING...")

app.run_polling()