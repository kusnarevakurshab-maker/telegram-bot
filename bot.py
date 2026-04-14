import os
from flask import Flask, request
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-service.onrender.com

if not TOKEN:
    raise ValueError("TOKEN не задан")

NAME, PHONE, CITY, SOURCE = range(4)

app = Flask(__name__)
tg_app = Application.builder().token(TOKEN).build()


# ---------------- HANDLERS ----------------

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
    context.user_data["phone"] = update.message.contact.phone_number if update.message.contact else update.message.text

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
        "🔥 Новая заявка\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🏙 Город: {data['city']}\n"
        f"📣 Источник: {data['source']}"
    )

    await update.message.reply_text("✅ Спасибо! Мы свяжемся с вами", reply_markup=ReplyKeyboardRemove())

    # сюда можно добавить CRM / админов
    await context.bot.send_message(chat_id=os.getenv("ADMIN_ID"), text=text)

    return ConversationHandler.END


# ---------------- CONVERSATION ----------------

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NAME: [MessageHandler(filters.TEXT, name)],
        PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, phone)],
        CITY: [MessageHandler(filters.TEXT, city)],
        SOURCE: [MessageHandler(filters.TEXT, source)],
    },
    fallbacks=[]
)

tg_app.add_handler(conv)


# ---------------- WEBHOOK ROUTE ----------------

@app.post("/")
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, tg_app.bot)

    await tg_app.process_update(update)
    return "ok"


# ---------------- STARTUP ----------------

@app.before_first_request
async def on_start():
    await tg_app.initialize()
    await tg_app.bot.set_webhook(WEBHOOK_URL)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

  
