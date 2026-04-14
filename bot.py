import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, ConversationHandler, filters

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN не задан в Environment Variables")

logging.basicConfig(level=logging.INFO)

# этапы анкеты
NAME, PHONE, CITY, SOURCE = range(4)

user_data_store = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("📱 Отправить номер", request_contact=True)]]
    await update.message.reply_text(
        "Привет! Давай заполним анкету.\n\nКак тебя зовут?",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    keyboard = [[KeyboardButton("📱 Отправить номер", request_contact=True)]]

    await update.message.reply_text(
        "Отправь номер телефона или нажми кнопку 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        context.user_data["phone"] = update.message.contact.phone_number
    else:
        context.user_data["phone"] = update.message.text

    await update.message.reply_text("Город?")
    return CITY


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text

    keyboard = [["Instagram", "TikTok"]]

    await update.message.reply_text(
        "Откуда узнал(а)?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return SOURCE


async def get_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["source"] = update.message.text

    data = context.user_data

    text = (
        "✅ Новая заявка:\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🏙 Город: {data['city']}\n"
        f"📣 Источник: {data['source']}"
    )

    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ок, отменено", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, get_phone)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_source)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)

    print("🚀 Bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
