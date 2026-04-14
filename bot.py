import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# Состояния
NAME, PHONE, SERVICE, SOURCE, CITY = range(5)

# Переменные окружения
TOKEN = os.getenv("TOKEN")

MANAGERS = []
if os.getenv("MANAGERS"):
    MANAGERS = [int(x) for x in os.getenv("MANAGERS").split(",") if x]


# Проверка токена
if not TOKEN:
    raise ValueError("❌ TOKEN не задан в Environment Variables")


# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Как вас зовут?")
    return NAME


# Имя
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Введите телефон:")
    return PHONE


# Телефон
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Какая услуга интересует?")
    return SERVICE


# Услуга
async def get_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["service"] = update.message.text
    await update.message.reply_text("Откуда вы о нас узнали?")
    return SOURCE


# Источник
async def get_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["source"] = update.message.text
    await update.message.reply_text("Введите город:")
    return CITY


# Город
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text

    text = (
        f"📩 Новая заявка:\n\n"
        f"👤 Имя: {context.user_data['name']}\n"
        f"📞 Телефон: {context.user_data['phone']}\n"
        f"🛠 Услуга: {context.user_data['service']}\n"
        f"📢 Источник: {context.user_data['source']}\n"
        f"📍 Город: {context.user_data['city']}"
    )

    if MANAGERS:
        for manager in MANAGERS:
            await context.bot.send_message(chat_id=manager, text=text)

    await update.message.reply_text("✅ Спасибо! Мы с вами свяжемся.")
    return ConversationHandler.END


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_service)],
            SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_source)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)

    print("🚀 Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()



  

