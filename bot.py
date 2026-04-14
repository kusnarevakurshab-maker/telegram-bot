import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ TOKEN не задан в Environment Variables")

# этапы анкеты
NAME, CITY, PHONE, SOURCE = range(4)

user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Напиши своё имя:")
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"name": update.message.text}

    await update.message.reply_text("🏙 Теперь напиши свой город:")
    return CITY


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]["city"] = update.message.text

    # кнопка для отправки телефона
    keyboard = [
        [KeyboardButton("📱 Отправить номер", request_contact=True)]
    ]

    await update.message.reply_text(
        "📞 Отправь свой номер телефона:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )

    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    phone = update.message.contact.phone_number if update.message.contact else update.message.text
    user_data[user_id]["phone"] = phone

    await update.message.reply_text("📢 Откуда ты узнал о нас?")
    return SOURCE



async def get_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id]["phone"] = update.message.contact.phone_number if update.message.contact else update.message.text

    keyboard = [
        [
            InlineKeyboardButton("📸 Instagram", callback_data="instagram"),
            InlineKeyboardButton("🎵 TikTok", callback_data="tiktok"),
        ]
    ]

    await update.message.reply_text(
        "📢 Откуда ты узнал о нас?",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    return SOURCE
    await update.message.reply_text(
        "✅ Спасибо! Вот твои данные:\n\n"
        f"👤 Имя: {data['name']}\n"
        f"🏙 Город: {data['city']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"📢 Источник: {data['source']}"
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Опрос отменён")
    return ConversationHandler.END


def main():
    print("🚀 Бот запущен...")

    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            PHONE: [MessageHandler(filters.ALL, get_phone)],
            SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_source)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
