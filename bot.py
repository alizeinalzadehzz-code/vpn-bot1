import os
import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8537532580:AAEHXHa9a_oS5-iPYdx-KEk6boD4Mea5UH4")
ADMIN_ID = int(os.getenv("ADMIN_ID", "474098524"))
SUPPORT_USERNAME = "ali_turk_z"
CARD_NUMBER = "6219-8618-9208-9466"
CARD_OWNER = "علی زینال‌زاده"

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

# state: user_id -> {"step": "waiting_receipt"/"waiting_config", "pkg_id": ..., "order_id": ...}
user_state = {}
pending_orders = {}
order_counter = [1000]

def next_order_id():
    order_counter[0] += 1
    return f"ORD{order_counter[0]}"

def main_kb():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("🛒 خرید سرویس"), KeyboardButton("📦 سرویس‌های من")],
            [KeyboardButton("🆘 پشتیبانی"),   KeyboardButton("ℹ️ راهنما")],
        ],
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder="یک گزینه انتخاب کنید..."
    )

# ─── /start ───────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_state.pop(user.id, None)
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
        reply_markup=main_kb()
    )

# ─── خرید سرویس ───────────────────────────────────────────────────────────────
async def show_buy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for pkg_id, pkg in PACKAGES.items():
        keyboard.append([InlineKeyboardButton(
            f"{pkg['name']}  —  {pkg['price']}", callback_data=f"pkg_{pkg_id}"
        )])
    await update.message.reply_text(
        "🛒 *انتخاب پکیج:*\n\nیکی از پکیج‌های زیر رو انتخاب کن:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ─── انتخاب پکیج (callback) ───────────────────────────────────────────────────
async def cb_select_pkg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pkg_id = query.data.replace("pkg_", "")
    pkg = PACKAGES.get(pkg_id)
    if not pkg:
        return

    user_state[query.from_user.id] = {"step": "waiting_receipt", "pkg_id": pkg_id}

    await query.edit_message_text(
        f"✅ *پکیج انتخابی:* {pkg['name']}\n\n"
        f"{pkg['description']}\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "💳 *اطلاعات پرداخت:*\n\n"
        f"🏦 شماره کارت:\n`{CARD_NUMBER}`\n\n"
        f"👤 به نام: *{CARD_OWNER}*\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "📸 بعد از واریز، *عکس رسید* رو همین‌جا بفرست 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ انصراف", callback_data="cancel_buy")]
        ])
    )

async def cb_cancel_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_state.pop(query.from_user.id, None)
    await query.edit_message_text("❌ خرید لغو شد.\n\nهر وقت خواستی دوباره از منو اقدام کن.")

# ─── سرویس‌های من ─────────────────────────────────────────────────────────────
async def show_my_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚠️ شما هنوز هیچ سرویسی ندارید\n\n"
        "برای خرید سرویس از دکمه 🛒 *خرید سرویس* استفاده کنید.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 جستجوی سرویس", callback_data="search_svc")],
            [InlineKeyboardButton("🔗 لینک کردن سرویس", callback_data="link_svc")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_main")],
        ])
    )

async def cb_svc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "search_svc":
        await query.edit_message_text(
            "🔍 *جستجوی سرویس*\n\nشماره سفارش خود را وارد کنید:",
            parse_mode="Markdown"
        )
    elif query.data == "link_svc":
        await query.edit_message_text(
            "🔗 *لینک کردن سرویس*\n\nکانفیگ دریافتی را وارد کنید:",
            parse_mode="Markdown"
        )
    elif query.data == "back_main":
        await query.edit_message_text("🏠 از منوی پایین انتخاب کن 👇")

# ─── پشتیبانی ─────────────────────────────────────────────────────────────────
async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 *پشتیبانی TurkNet*\n\n"
        f"👤 آیدی: @{SUPPORT_USERNAME}\n"
        "🕐 ساعت کاری: ۸ صبح تا ۱۲ شب\n\n"
        "برای ارتباط مستقیم دکمه زیر رو بزن 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 پیام به پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]
        ])
    )

# ─── راهنما ───────────────────────────────────────────────────────────────────
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *راهنمای استفاده:*\n\n"
        "1️⃣ روی 🛒 *خرید سرویس* بزن\n"
        "2️⃣ پکیج موردنظر رو انتخاب کن\n"
        "3️⃣ مبلغ رو به کارت واریز کن\n"
        "4️⃣ *عکس رسید* رو بفرست\n"
        "5️⃣ بعد از تایید ادمین، کانفیگ برات ارسال میشه\n\n"
        f"❓ سوال داری؟\n👤 @{SUPPORT_USERNAME}",
        parse_mode="Markdown"
    )

# ─── هندلر عکس (رسید) ─────────────────────────────────────────────────────────
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    state = user_state.get(user.id)

    if not state or state.get("step") != "waiting_receipt":
        await update.message.reply_text("برای خرید از منو، 🛒 *خرید سرویس* رو بزن.", parse_mode="Markdown")
        return

    pkg = PACKAGES.get(state["pkg_id"])
    if not pkg:
        await update.message.reply_text("❌ خطا! دوباره /start بزن.")
        user_state.pop(user.id, None)
        return

    order_id = next_order_id()
    file_id = update.message.photo[-1].file_id

    pending_orders[order_id] = {
        "user_id": user.id,
        "username": user.username or user.first_name,
        "package": pkg,
    }
    user_state.pop(user.id, None)

    # نوتیف ادمین
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=file_id,
        caption=(
            f"🔔 *سفارش جدید!*\n\n"
            f"🆔 سفارش: `{order_id}`\n"
            f"👤 کاربر: @{user.username or '—'}\n"
            f"🔢 آیدی: `{user.id}`\n"
            f"📦 پکیج: {pkg['name']}\n"
            f"💰 مبلغ: {pkg['price']}\n\n"
            f"📸 رسید پرداخت 👆"
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ تایید — ارسال کانفیگ", callback_data=f"approve_{order_id}")],
            [InlineKeyboardButton("❌ رد سفارش", callback_data=f"reject_{order_id}")],
        ])
    )

    await update.message.reply_text(
        f"✅ *رسید دریافت شد!*\n\n"
        f"🔢 شماره سفارش: `{order_id}`\n"
        f"⏳ در حال بررسی توسط ادمین...\n\n"
        f"📞 پشتیبانی: @{SUPPORT_USERNAME}",
        parse_mode="Markdown",
        reply_markup=main_kb()
    )

# ─── ادمین: تایید ─────────────────────────────────────────────────────────────
async def cb_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ فقط ادمین!", show_alert=True)
        return

    order_id = query.data.replace("approve_", "")
    if order_id not in pending_orders:
        await query.edit_message_caption("⚠️ این سفارش قبلاً پردازش شده.", parse_mode="Markdown")
        return

    # ست کردن state ادمین برای دریافت کانفیگ
    user_state[ADMIN_ID] = {"step": "waiting_config", "order_id": order_id}

    await query.edit_message_caption(
        query.message.caption + f"\n\n✅ *تایید شد*\n\nکانفیگ سفارش `{order_id}` رو بفرست:",
        parse_mode="Markdown"
    )

# ─── ادمین: رد ────────────────────────────────────────────────────────────────
async def cb_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ فقط ادمین!", show_alert=True)
        return

    order_id = query.data.replace("reject_", "")
    order = pending_orders.pop(order_id, None)
    if not order:
        await query.edit_message_caption("⚠️ این سفارش قبلاً پردازش شده.", parse_mode="Markdown")
        return

    await context.bot.send_message(
        chat_id=order["user_id"],
        text=(
            f"❌ *سفارش رد شد!*\n\n"
            f"🆔 سفارش: `{order_id}`\n\n"
            f"⚠️ رسید تایید نشد.\n"
            f"برای پیگیری: @{SUPPORT_USERNAME}"
        ),
        parse_mode="Markdown"
    )
    await query.edit_message_caption(
        query.message.caption + "\n\n❌ *رد شد*",
        parse_mode="Markdown"
    )

# ─── هندلر متن ────────────────────────────────────────────────────────────────
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    # ادمین داره کانفیگ می‌فرسته
    if user.id == ADMIN_ID:
        state = user_state.get(ADMIN_ID)
        if state and state.get("step") == "waiting_config":
            order_id = state["order_id"]
            order = pending_orders.pop(order_id, None)
            user_state.pop(ADMIN_ID, None)

            if not order:
                await update.message.reply_text("⚠️ سفارش پیدا نشد.")
                return

            await context.bot.send_message(
                chat_id=order["user_id"],
                text=(
                    f"🎉 *سفارش تایید شد!*\n\n"
                    f"📦 پکیج: {order['package']['name']}\n"
                    f"🆔 سفارش: `{order_id}`\n\n"
                    "━━━━━━━━━━━━━━━━\n"
                    f"🔑 *کانفیگ شما:*\n\n"
                    f"`{text}`\n"
                    "━━━━━━━━━━━━━━━━\n\n"
                    f"✅ ممنون از خریدت!\n"
                    f"📞 پشتیبانی: @{SUPPORT_USERNAME}"
                ),
                parse_mode="Markdown"
            )
            await update.message.reply_text(f"✅ کانفیگ برای `{order_id}` ارسال شد.", parse_mode="Markdown")
            return

    # منوی کاربر
    if text == "🛒 خرید سرویس":
        await show_buy_menu(update, context)
    elif text == "📦 سرویس‌های من":
        await show_my_services(update, context)
    elif text == "🆘 پشتیبانی":
        await show_support(update, context)
    elif text == "ℹ️ راهنما":
        await show_help(update, context)
    else:
        await update.message.reply_text("از منوی پایین یه گزینه انتخاب کن 👇", reply_markup=main_kb())

# ─── post init ────────────────────────────────────────────────────────────────
async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "شروع / منوی اصلی"),
    ])

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(cb_select_pkg,  pattern="^pkg_"))
    app.add_handler(CallbackQueryHandler(cb_cancel_buy,  pattern="^cancel_buy$"))
    app.add_handler(CallbackQueryHandler(cb_approve,     pattern="^approve_"))
    app.add_handler(CallbackQueryHandler(cb_reject,      pattern="^reject_"))
    app.add_handler(CallbackQueryHandler(cb_svc,         pattern="^(search_svc|link_svc|back_main)$"))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot started...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
