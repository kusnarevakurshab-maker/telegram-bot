import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TOKEN:
    raise ValueError("TOKEN не задан")

ADMIN_IDS = [8372291148, 8139131694]

NAME, PHONE, CITY, SOURCE = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 Как тебя зовут?")
    return NAME


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    keyboard = [[KeyboardButton("📱 Отправить номер", request_contact=True)]]

    await update.message.reply_text(
        "📱 Отправь номер телефона:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = (
        update.message.contact.phone_number
        if update.message.contact
        else update.message.text
    )

    await update.message.reply_text("🏙 В каком ты городе?")
    return CITY


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text

    keyboard = [["Instagram", "TikTok"]]

    await update.message.reply_text(
        "📣 Откуда узнал?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return SOURCE


async def source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["source"] = update.message.text
    data = context.user_data

    text = (
        "🔥 Новая заявка\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🏙 Город: {data['city']}\n"
        f"📣 Источник: {data['source']}"
    )

    # user reply
    await update.message.reply_text(
        "✅ Спасибо! Мы свяжемся с вами",
        reply_markup=ReplyKeyboardRemove(),
    )

    # admins
    for admin in ADMIN_IDS:
        await context.bot.send_message(chat_id=admin, text=text)

    return ConversationHandler.END


def build_app():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT, name)],
            PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, phone)],
            CITY: [MessageHandler(filters.TEXT, city)],
            SOURCE: [MessageHandler(filters.TEXT, source)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    return app


# ---------------- MAIN ----------------
app = build_app()


async def on_startup(app):
    if not WEBHOOK_URL:
        raise ValueError("WEBHOOK_URL не задан")

    await app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")


async def on_shutdown(app):
    await app.bot.delete_webhook()


if __name__ == "__main__":
    app.post_init = on_startup
    app.post_shutdown = on_shutdown

    print("BOT STARTED (WEBHOOK MODE)")
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        url_path="webhook",
    )
