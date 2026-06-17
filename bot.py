import os
import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, MenuButtonCommands, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8537532580:AAEHXHa9a_oS5-iPYdx-KEk6boD4Mea5UH4")
ADMIN_ID = int(os.getenv("ADMIN_ID", "474098524"))
SUPPORT_USERNAME = "ali_turk_z"
CARD_NUMBER = "6219-8618-9208-9466"
CARD_OWNER = "علی زینال‌زاده"

WAITING_RECEIPT, WAITING_CONFIG = range(2)

PACKAGES = {
    "pkg_10g": {
        "name": "🔹 10 گیگابایت",
        "price": "100,000 تومان",
        "description": "📦 حجم: 10 گیگابایت\n⏳ مدت: نامحدود\n💰 قیمت: 100,000 تومان"
    },
    "pkg_20g": {
        "name": "🔸 20 گیگابایت",
        "price": "180,000 تومان",
        "description": "📦 حجم: 20 گیگابایت\n⏳ مدت: نامحدود\n💰 قیمت: 180,000 تومان"
    },
    "pkg_50g": {
        "name": "💎 50 گیگابایت",
        "price": "400,000 تومان",
        "description": "📦 حجم: 50 گیگابایت\n⏳ مدت: نامحدود\n💰 قیمت: 400,000 تومان"
    },
    "pkg_100g": {
        "name": "👑 100 گیگابایت",
        "price": "700,000 تومان",
        "description": "📦 حجم: 100 گیگابایت\n⏳ مدت: نامحدود\n💰 قیمت: 700,000 تومان"
    },
}

pending_orders = {}
order_counter = [1000]

def next_order_id():
    order_counter[0] += 1
    return f"ORD{order_counter[0]}"

def main_reply_keyboard():
    """منوی دکمه‌های بزرگ پایین صفحه"""
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🛒 خرید سرویس"), KeyboardButton("📦 سرویس‌های من")],
            [KeyboardButton("🆘 پشتیبانی"), KeyboardButton("ℹ️ راهنما")],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="یک گزینه انتخاب کنید..."
    )

# ─── /start ───────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 سلام *{user.first_name}* عزیز!\n\n"
        "🚀 به ربات فروش VPN *TurkNet* خوش اومدی\n\n"
        "✨ ویژگی‌های ما:\n"
        "• ⚡️ سرعت بالا و پایدار\n"
        "• ♾️ مدت نامحدود\n"
        "• 🔒 امن و خصوصی\n"
        "• 🛠 پشتیبانی ۲۴ ساعته\n\n"
        "از منوی پایین انتخاب کن 👇",
        parse_mode="Markdown",
        reply_markup=main_reply_keyboard()
    )

# ─── سرویس‌های من ─────────────────────────────────────────────────────────────
async def my_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 جستجوی سرویس", callback_data="search_service")],
        [InlineKeyboardButton("🔗 لینک کردن سرویس", callback_data="link_service")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="back_home")],
    ])
    await update.message.reply_text(
        "⚠️ شما هنوز هیچ سرویسی ندارید\n"
        "برای خرید سرویس از دکمه 🛒 *خرید سرویس* استفاده کنید.",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def service_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "search_service":
        await query.edit_message_text(
            "🔍 *جستجوی سرویس*\n\nشماره سفارش یا آیدی سرویس خود را وارد کنید:",
            parse_mode="Markdown"
        )
    elif query.data == "link_service":
        await query.edit_message_text(
            "🔗 *لینک کردن سرویس*\n\nکانفیگ دریافتی را اینجا وارد کنید:",
            parse_mode="Markdown"
        )
    elif query.data == "back_home":
        await query.edit_message_text("🏠 به منوی اصلی برگشتی.")

# ─── پکیج‌ها ──────────────────────────────────────────────────────────────────
async def show_packages_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📦 *پکیج‌های موجود:*\n\n"
    for pkg in PACKAGES.values():
        text += f"{pkg['description']}\n➖➖➖➖➖➖\n\n"
    text += "برای خرید دکمه 🛒 *خرید سرویس* رو بزن"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_reply_keyboard())

# ─── راهنما ───────────────────────────────────────────────────────────────────
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *راهنمای استفاده:*\n\n"
        "1️⃣ روی 🛒 *خرید سرویس* بزن\n"
        "2️⃣ پکیج موردنظر رو انتخاب کن\n"
        "3️⃣ مبلغ رو به کارت واریز کن\n"
        "4️⃣ *عکس رسید* رو بفرست\n"
        "5️⃣ بعد از تایید ادمین، کانفیگ برات ارسال میشه\n\n"
        f"❓ سوال داری؟ با پشتیبانی تماس بگیر:\n👤 @{SUPPORT_USERNAME}",
        parse_mode="Markdown",
        reply_markup=main_reply_keyboard()
    )

# ─── پشتیبانی ─────────────────────────────────────────────────────────────────
async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 پیام به پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]
    ])
    await update.message.reply_text(
        "🆘 *پشتیبانی TurkNet*\n\n"
        f"👤 آیدی: @{SUPPORT_USERNAME}\n"
        "🕐 ساعت کاری: ۸ صبح تا ۱۲ شب\n\n"
        "برای ارتباط مستقیم دکمه زیر رو بزن 👇",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# ─── خرید ─────────────────────────────────────────────────────────────────────
async def buy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for pkg_id, pkg in PACKAGES.items():
        keyboard.append([InlineKeyboardButton(
            f"{pkg['name']} — {pkg['price']}", callback_data=f"select_{pkg_id}"
        )])

    await update.message.reply_text(
        "🛒 *انتخاب پکیج:*\n\nیکی از پکیج‌های زیر رو انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def select_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pkg_id = query.data.replace("select_", "")
    pkg = PACKAGES.get(pkg_id)
    if not pkg:
        await query.answer("پکیج پیدا نشد!", show_alert=True)
        return ConversationHandler.END

    context.user_data["selected_package"] = pkg_id

    text = (
        f"✅ *پکیج انتخابی:* {pkg['name']}\n\n"
        f"{pkg['description']}\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "💳 *اطلاعات پرداخت:*\n\n"
        f"🏦 شماره کارت:\n`{CARD_NUMBER}`\n\n"
        f"👤 به نام: *{CARD_OWNER}*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "📸 بعد از واریز، *عکس رسید* رو اینجا بفرست"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ انصراف", callback_data="cancel_buy")]
    ])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
    return WAITING_RECEIPT

async def cancel_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ خرید لغو شد.")
    return ConversationHandler.END

async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text(
            "⚠️ لطفاً *عکس* رسید رو بفرست (نه فایل یا متن).",
            parse_mode="Markdown"
        )
        return WAITING_RECEIPT

    pkg_id = context.user_data.get("selected_package")
    pkg = PACKAGES.get(pkg_id)
    if not pkg:
        await update.message.reply_text("❌ خطا! دوباره /start بزن.")
        return ConversationHandler.END

    user = update.effective_user
    order_id = next_order_id()
    file_id = update.message.photo[-1].file_id

    pending_orders[order_id] = {
        "user_id": user.id,
        "username": user.username or user.first_name,
        "package": pkg,
        "receipt_file_id": file_id,
    }

    admin_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تایید و ارسال کانفیگ", callback_data=f"approve_{order_id}")],
        [InlineKeyboardButton("❌ رد سفارش", callback_data=f"reject_{order_id}")],
    ])
    caption = (
        f"🔔 *سفارش جدید!*\n\n"
        f"🆔 سفارش: `{order_id}`\n"
        f"👤 کاربر: @{user.username or '—'}\n"
        f"🔢 آیدی: `{user.id}`\n"
        f"📦 پکیج: {pkg['name']}\n"
        f"💰 مبلغ: {pkg['price']}\n\n"
        f"📸 رسید پرداخت 👆"
    )
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=file_id,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=admin_keyboard
    )

    await update.message.reply_text(
        f"✅ *رسید دریافت شد!*\n\n"
        f"🔢 شماره سفارش: `{order_id}`\n"
        f"⏳ در حال بررسی توسط ادمین...\n\n"
        f"📞 پشتیبانی: @{SUPPORT_USERNAME}",
        parse_mode="Markdown",
        reply_markup=main_reply_keyboard()
    )
    return ConversationHandler.END

# ─── ادمین: تایید ─────────────────────────────────────────────────────────────
async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        await query.answer("⛔ فقط ادمین!", show_alert=True)
        return

    order_id = query.data.replace("approve_", "")
    order = pending_orders.get(order_id)
    if not order:
        await query.edit_message_caption("⚠️ این سفارش قبلاً پردازش شده.", parse_mode="Markdown")
        return

    context.bot_data[f"pending_config_{ADMIN_ID}"] = order_id
    await query.edit_message_caption(
        query.message.caption + f"\n\n✅ *تایید شد*\n\nحالا کانفیگ سفارش `{order_id}` رو بفرست:",
        parse_mode="Markdown"
    )
    return WAITING_CONFIG

async def receive_config_from_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    order_id = context.bot_data.get(f"pending_config_{ADMIN_ID}")
    if not order_id:
        return

    order = pending_orders.get(order_id)
    if not order:
        await update.message.reply_text("⚠️ سفارش پیدا نشد.")
        return

    config_text = update.message.text
    pkg = order["package"]

    await context.bot.send_message(
        chat_id=order["user_id"],
        text=(
            f"🎉 *سفارش تایید شد!*\n\n"
            f"📦 پکیج: {pkg['name']}\n"
            f"🆔 سفارش: `{order_id}`\n\n"
            "━━━━━━━━━━━━━━━━\n"
            f"🔑 *کانفیگ شما:*\n\n"
            f"`{config_text}`\n"
            "━━━━━━━━━━━━━━━━\n\n"
            f"✅ ممنون از خریدت!\n"
            f"📞 پشتیبانی: @{SUPPORT_USERNAME}"
        ),
        parse_mode="Markdown"
    )

    del pending_orders[order_id]
    context.bot_data.pop(f"pending_config_{ADMIN_ID}", None)
    await update.message.reply_text(
        f"✅ کانفیگ برای سفارش `{order_id}` ارسال شد.",
        parse_mode="Markdown"
    )

# ─── ادمین: رد ────────────────────────────────────────────────────────────────
async def admin_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        await query.answer("⛔ فقط ادمین!", show_alert=True)
        return

    order_id = query.data.replace("reject_", "")
    order = pending_orders.get(order_id)
    if not order:
        await query.edit_message_caption("⚠️ این سفارش قبلاً پردازش شده.", parse_mode="Markdown")
        return

    await context.bot.send_message(
        chat_id=order["user_id"],
        text=(
            f"❌ *سفارش رد شد!*\n\n"
            f"🆔 سفارش: `{order_id}`\n\n"
            f"⚠️ رسید تایید نشد.\n"
            f"برای پیگیری با پشتیبانی تماس بگیر:\n"
            f"👤 @{SUPPORT_USERNAME}"
        ),
        parse_mode="Markdown"
    )

    del pending_orders[order_id]
    await query.edit_message_caption(
        query.message.caption + "\n\n❌ *رد شد*",
        parse_mode="Markdown"
    )

# ─── هندلر متن‌های منو ────────────────────────────────────────────────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🛒 خرید سرویس":
        await buy_menu(update, context)
    elif text == "📦 سرویس‌های من":
        await my_services(update, context)
    elif text == "🆘 پشتیبانی":
        await show_support(update, context)
    elif text == "ℹ️ راهنما":
        await show_help(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ لغو شد.", reply_markup=main_reply_keyboard())
    return ConversationHandler.END

# ─── Post init: تنظیم دکمه‌های کامند ─────────────────────────────────────────
async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "شروع / منوی اصلی"),
        BotCommand("buy", "خرید سرویس"),
        BotCommand("support", "پشتیبانی"),
    ])

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    buy_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_package, pattern="^select_")],
        states={
            WAITING_RECEIPT: [MessageHandler(filters.PHOTO, receive_receipt)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CallbackQueryHandler(cancel_buy, pattern="^cancel_buy$"),
        ],
        per_chat=True,
        per_user=True,
        per_message=False,
    )

    admin_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_approve, pattern="^approve_")],
        states={
            WAITING_CONFIG: [MessageHandler(
                filters.TEXT & ~filters.COMMAND & filters.User(ADMIN_ID),
                receive_config_from_admin
            )],
        },
        fallbacks=[],
        per_chat=True,
        per_user=True,
        per_message=False,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy_menu))
    app.add_handler(CommandHandler("support", show_support))
    app.add_handler(buy_conv)
    app.add_handler(admin_conv)
    app.add_handler(CallbackQueryHandler(admin_reject, pattern="^reject_"))
    app.add_handler(CallbackQueryHandler(service_callbacks, pattern="^(search_service|link_service|back_home)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot started...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
