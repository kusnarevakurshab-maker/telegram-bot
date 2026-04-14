import os
from flask import Flask, request
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-service.onrender.com

if not TOKEN:
    raise ValueError("TOKEN не задан")

app = Flask(__name__)

NAME, PHONE, CITY, SOURCE = range(4)

# ---------------- BOT LOGIC ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 Как тебя зовут?")
    return NAME


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    keyboard = [[KeyboardButton("📱 Отправить номер", request_contact=True)]]

    await update.message.reply_text(
        "📱 Отправь номер телефона:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        context.user_data["phone"] = update.message.contact.phone_number
    else:
        context.user_data["phone"] = update.message.text

    await update.message.reply_text("🏙 В каком ты городе?")
    return CITY


async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text

    keyboard = [["Instagram", "TikTok"]]

    await update.message.reply_text(
        "📣 Откуда узнал?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return SOURCE


async def source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["source"] = update.message.text
    data = context.user_data

    text = (
        "🔥 НОВАЯ ЗАЯВКА\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🏙 Город: {data['city']}\n"
        f"📣 Источник: {data['source']}"
    )

    await update.message.reply_text(
        "✅ Спасибо! Мы скоро с вами свяжемся",
        reply_markup=ReplyKeyboardRemove()
    )

    # отправка админу (вставь свой ID)
    ADMIN_IDS = [8372291148, 8139131694]

    for admin in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin, text=text)
        except Exception as e:
            print("ADMIN ERROR:", e)

    return ConversationHandler.END


# ---------------- SETUP BOT ----------------

application = Application.builder().token(TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
        PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, phone)],
        CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city)],
        SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, source)],
    },
    fallbacks=[],
)

application.add_handler(conv)


# ---------------- WEBHOOK ----------------

@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"


@app.route("/")
def home():
    return "Bot is running"


# ---------------- START ----------------

def run():
    import asyncio

    async def on_start():
        await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{TOKEN}")
        print("WEBHOOK SET")

    asyncio.get_event_loop().run_until_complete(on_start())

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


if __name__ == "__main__":
    run()
