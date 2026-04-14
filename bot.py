import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN не задан в Environment Variables")

ADMIN_IDS = [8372291148, 8139131694]
NAME, PHONE, CITY, SOURCE = range(4)


# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 Как вас зовут?")
    return NAME


# ---------------- NAME ----------------
async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    keyboard = [[KeyboardButton("📱 Отправить номер", request_contact=True)]]

    await update.message.reply_text(
        "📱 Отправь номер телефона:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return PHONE


# ---------------- PHONE ----------------
async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        context.user_data["phone"] = update.message.contact.phone_number

    elif update.message.text and update.message.text.isdigit():
        context.user_data["phone"] = update.message.text

    else:
        await update.message.reply_text(
            "📵 Отправьте номер кнопкой или введите только цифры"
        )
        return PHONE

    await update.message.reply_text("🏙 Место вашего нахождения?")
    return CITY


# ---------------- CITY ----------------
async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text

    keyboard = [["Instagram", "TikTok"]]

    await update.message.reply_text(
        "📣 Откуда вы про нас узнали?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return SOURCE


# ---------------- SOURCE ----------------
async def source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text not in ["Instagram", "TikTok"]:
        await update.message.reply_text("Выбери кнопку 👇")
        return SOURCE

    context.user_data["source"] = update.message.text
    data = context.user_data

    text = (
        "🔥 Новая заявка!\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🏙 Город: {data['city']}\n"
        f"📣 Источник: {data['source']}"
    )

    await update.message.reply_text(
        "✅ Спасибо! Мы скоро с вами свяжемся",
        reply_markup=ReplyKeyboardRemove()
    )

    for admin_id in ADMIN_IDS:
        await context.bot.send_message(chat_id=admin_id, text=text)

    return ConversationHandler.END


# ---------------- CANCEL ----------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Диалог отменён",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, phone)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city)],
            SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, source)],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("cancel", cancel),
        ]
    )

    app.add_handler(conv)

    print("BOT STARTED")
    app.run_polling()


# ---------------- RUN ----------------
import asyncio

if __name__ == "__main__":
    asyncio.set_event_loop(asyncio.new_event_loop())
    main()
