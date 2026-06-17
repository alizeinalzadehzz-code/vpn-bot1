import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8537532580:AAEHXHa9a_oS5-iPYdx-KEk6boD4Mea5UH4")
ADMIN_ID = int(os.getenv("ADMIN_ID", "474098524"))
SUPPORT_USERNAME = "@ali_turk_z"
CARD_NUMBER = "6219-8618-9208-9466"
CARD_OWNER = "علی زینال‌زاده"

# Conversation states
WAITING_RECEIPT, WAITING_CONFIG = range(2)

# Packages
PACKAGES = {
    "pkg_10g_100k": {
        "name": "10 گیگ",
        "price": "100,000 تومان",
        "duration": "نامحدود",
        "description": "🔹 حجم: 10 گیگابایت\n⏳ مدت: نامحدود\n💰 قیمت: 100,000 تومان"
    },
    "pkg_20g_180k": {
        "name": "20 گیگ",
        "price": "180,000 تومان",
        "duration": "نامحدود",
        "description": "🔹 حجم: 20 گیگابایت\n⏳ مدت: نامحدود\n💰 قیمت: 180,000 تومان"
    },
    "pkg_50g_400k": {
        "name": "50 گیگ",
        "price": "400,000 تومان",
        "duration": "نامحدود",
        "description": "🔹 حجم: 50 گیگابایت\n⏳ مدت: نامحدود\n💰 قیمت: 400,000 تومان"
    },
    "pkg_100g_700k": {
        "name": "100 گیگ",
        "price": "700,000 تومان",
        "duration": "نامحدود",
        "description": "🔹 حجم: 100 گیگابایت\n⏳ مدت: نامحدود\n💰 قیمت: 700,000 تومان"
    },
}

# Pending orders: {order_id: {user_id, username, package, receipt_file_id}}
pending_orders = {}
order_counter = [1000]


def next_order_id():
    order_counter[0] += 1
    return f"ORD{order_counter[0]}"


# ─── /start ───────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🛒 خرید کانفیگ", callback_data="buy")],
        [InlineKeyboardButton("📦 پکیج‌های موجود", callback_data="packages")],
        [InlineKeyboardButton("🆘 پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME.lstrip('@')}")],
    ]
    await update.message.reply_text(
        f"👋 سلام {user.first_name}!\n\n"
        "به ربات فروش VPN خوش اومدی 🚀\n\n"
        "📌 کانفیگ‌های ما:\n"
        "• حجمی — مدت نامحدود\n"
        "• سرعت بالا\n"
        "• پشتیبانی ۲۴/۷\n\n"
        "از منو پایین انتخاب کن 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ─── Show packages ────────────────────────────────────────────────────────────
async def show_packages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = "📦 *پکیج‌های موجود:*\n\n"
    for pkg in PACKAGES.values():
        text += f"{pkg['description']}\n➖➖➖➖➖➖➖\n"

    keyboard = [
        [InlineKeyboardButton("🛒 خرید", callback_data="buy")],
        [InlineKeyboardButton("🏠 بازگشت", callback_data="home")],
    ]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))


# ─── Buy flow ─────────────────────────────────────────────────────────────────
async def buy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = []
    for pkg_id, pkg in PACKAGES.items():
        keyboard.append([InlineKeyboardButton(
            f"{pkg['name']} — {pkg['price']}", callback_data=f"select_{pkg_id}"
        )])
    keyboard.append([InlineKeyboardButton("🏠 بازگشت", callback_data="home")])

    await query.edit_message_text(
        "🛒 *انتخاب پکیج:*\nیکی از پکیج‌های زیر رو انتخاب کن:",
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
        return

    context.user_data["selected_package"] = pkg_id

    text = (
        f"✅ پکیج انتخابی: *{pkg['name']}*\n\n"
        f"{pkg['description']}\n\n"
        f"💳 *اطلاعات پرداخت:*\n"
        f"شماره کارت: `{CARD_NUMBER}`\n"
        f"به نام: {CARD_OWNER}\n\n"
        f"⚠️ بعد از واریز، *عکس رسید* رو اینجا ارسال کن تا بررسی بشه."
    )
    keyboard = [[InlineKeyboardButton("❌ انصراف", callback_data="buy")]]
    await query.edit_message_text(text, parse_mode="Markdown",
                                  reply_markup=InlineKeyboardMarkup(keyboard))

    return WAITING_RECEIPT


async def receive_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("❌ لطفاً *عکس* رسید رو بفرست (نه فایل یا متن).",
                                        parse_mode="Markdown")
        return WAITING_RECEIPT

    pkg_id = context.user_data.get("selected_package")
    pkg = PACKAGES.get(pkg_id)
    if not pkg:
        await update.message.reply_text("❌ خطا! دوباره از /start شروع کن.")
        return ConversationHandler.END

    user = update.effective_user
    order_id = next_order_id()
    file_id = update.message.photo[-1].file_id

    pending_orders[order_id] = {
        "user_id": user.id,
        "username": user.username or user.first_name,
        "package": pkg,
        "pkg_id": pkg_id,
        "receipt_file_id": file_id,
    }

    # Notify admin
    admin_keyboard = [
        [
            InlineKeyboardButton("✅ تایید", callback_data=f"approve_{order_id}"),
            InlineKeyboardButton("❌ رد", callback_data=f"reject_{order_id}"),
        ]
    ]
    caption = (
        f"🔔 *سفارش جدید!*\n\n"
        f"🆔 شماره سفارش: `{order_id}`\n"
        f"👤 کاربر: @{user.username or 'بدون یوزرنیم'} (ID: `{user.id}`)\n"
        f"📦 پکیج: {pkg['name']} — {pkg['price']}\n\n"
        f"رسید پرداخت 👆"
    )
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=file_id,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(admin_keyboard)
    )

    await update.message.reply_text(
        f"✅ رسید دریافت شد!\n\n"
        f"🔢 شماره سفارش: `{order_id}`\n"
        f"⏳ ادمین داره بررسی می‌کنه، کمی صبر کن...\n\n"
        f"📞 پشتیبانی: {SUPPORT_USERNAME}",
        parse_mode="Markdown"
    )
    return ConversationHandler.END


# ─── Admin: approve ───────────────────────────────────────────────────────────
async def admin_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        await query.answer("⛔ فقط ادمین!", show_alert=True)
        return

    order_id = query.data.replace("approve_", "")
    order = pending_orders.get(order_id)
    if not order:
        await query.edit_message_caption("⚠️ این سفارش قبلاً پردازش شده.")
        return

    # Ask admin to send config
    context.bot_data[f"pending_config_{update.effective_user.id}"] = order_id
    await query.edit_message_caption(
        query.message.caption + "\n\n✅ *تایید شد* — حالا کانفیگ رو بفرست (متن):",
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

    # Send config to user
    await context.bot.send_message(
        chat_id=order["user_id"],
        text=(
            f"🎉 *سفارش تایید شد!*\n\n"
            f"📦 پکیج: {pkg['name']}\n"
            f"🆔 شماره سفارش: `{order_id}`\n\n"
            f"🔑 *کانفیگ شما:*\n"
            f"`{config_text}`\n\n"
            f"📞 پشتیبانی: {SUPPORT_USERNAME}\n"
            f"✅ ممنون از خریدت!"
        ),
        parse_mode="Markdown"
    )

    del pending_orders[order_id]
    context.bot_data.pop(f"pending_config_{ADMIN_ID}", None)

    await update.message.reply_text(f"✅ کانفیگ برای سفارش `{order_id}` ارسال شد.", parse_mode="Markdown")


# ─── Admin: reject ────────────────────────────────────────────────────────────
async def admin_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        await query.answer("⛔ فقط ادمین!", show_alert=True)
        return

    order_id = query.data.replace("reject_", "")
    order = pending_orders.get(order_id)
    if not order:
        await query.edit_message_caption("⚠️ این سفارش قبلاً پردازش شده.")
        return

    await context.bot.send_message(
        chat_id=order["user_id"],
        text=(
            f"❌ *سفارش رد شد!*\n\n"
            f"🆔 شماره سفارش: `{order_id}`\n\n"
            f"⚠️ رسید تایید نشد. اگر مشکلی هست با پشتیبانی تماس بگیر:\n"
            f"{SUPPORT_USERNAME}"
        ),
        parse_mode="Markdown"
    )

    del pending_orders[order_id]
    await query.edit_message_caption(query.message.caption + "\n\n❌ *رد شد*", parse_mode="Markdown")


# ─── Home / callback router ───────────────────────────────────────────────────
async def home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🛒 خرید کانفیگ", callback_data="buy")],
        [InlineKeyboardButton("📦 پکیج‌های موجود", callback_data="packages")],
        [InlineKeyboardButton("🆘 پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME.lstrip('@')}")],
    ]
    await query.edit_message_text(
        "🏠 منوی اصلی — از گزینه‌های زیر انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ لغو شد. برای شروع دوباره /start بزن.")
    return ConversationHandler.END


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation for buying
    buy_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_package, pattern="^select_")],
        states={
            WAITING_RECEIPT: [MessageHandler(filters.PHOTO, receive_receipt)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )

    # Conversation for admin sending config
    admin_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_approve, pattern="^approve_")],
        states={
            WAITING_CONFIG: [MessageHandler(
                filters.TEXT & filters.User(ADMIN_ID), receive_config_from_admin
            )],
        },
        fallbacks=[],
        per_message=False,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_packages, pattern="^packages$"))
    app.add_handler(CallbackQueryHandler(buy_menu, pattern="^buy$"))
    app.add_handler(CallbackQueryHandler(home, pattern="^home$"))
    app.add_handler(CallbackQueryHandler(admin_reject, pattern="^reject_"))
    app.add_handler(buy_conv)
    app.add_handler(admin_conv)

    logger.info("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
