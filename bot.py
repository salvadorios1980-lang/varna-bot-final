import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters, ConversationHandler

TOKEN = "8858289407:AAGs_2C2cetEdQz_36YaSMwo9uAkDicpwoE"
CHANNEL_ID = "@VarnaDobrichShumenSilistraObyavi"
ADMIN_ID = 123456789

IBAN = "BG04CECB97902094110801"
TITULAR = "Ahmed Ahmed"

PRICE_TEXT = f"""
💰 *ЦЕНОРАЗПИС - Обяви Варна Добрич Шумен Силистра*

🏠 Имоти | 🚗 Коли | 💼 Работа | 🔧 Авточасти | 📦 Всичко
📍 Варна | Добрич | Шумен | Силистра

⏱️ 24 часа - 5 лв
⏱️ 3 дни - 10 лв
⏱️ Седмица - 20 лв
⏱️ Месец - 50 лв

💳 *Плащане по IBAN:*
`{IBAN}`
Титуляр: {TITULAR}

📸 След плащане изпрати снимка на бележката!
"""

logging.basicConfig(level=logging.INFO)
CATEGORY, CITY, AD_CONTENT, DURATION = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏠 Имоти", callback_data="cat_Имоти"), InlineKeyboardButton("🚗 Коли", callback_data="cat_Коли")],
        [InlineKeyboardButton("💼 Работа", callback_data="cat_Работа"), InlineKeyboardButton("🔧 Авточасти", callback_data="cat_Авточасти")],
        [InlineKeyboardButton("📦 Всичко друго", callback_data="cat_Всичко")]
    ]
    await update.message.reply_text(PRICE_TEXT + "\n\n👇 *Какво искаш да пуснеш?*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return CATEGORY

async def category_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['category'] = query.data.replace("cat_", "")
    keyboard = [
        [InlineKeyboardButton("Варна", callback_data="city_Варна"), InlineKeyboardButton("Добрич", callback_data="city_Добрич")],
        [InlineKeyboardButton("Шумен", callback_data="city_Шумен"), InlineKeyboardButton("Силистра", callback_data="city_Силистра")],
        [InlineKeyboardButton("Целия регион", callback_data="city_Всички")]
    ]
    await query.edit_message_text(f"Избра: {context.user_data['category']}\n\n📍 *Избери град:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return CITY

async def city_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['city'] = query.data.replace("city_", "")
    await query.edit_message_text(f"Категория: {context.user_data['category']}\nГрад: {context.user_data['city']}\n\n📝 *Сега изпрати обявата си - текст + снимки + телефон:*", parse_mode="Markdown")
    return AD_CONTENT

async def ad_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ad_message_id'] = update.message.message_id
    context.user_data['ad_chat_id'] = update.effective_chat.id
    keyboard = [
        [InlineKeyboardButton("24 часа - 5 лв", callback_data="dur_24ч_5лв")],
        [InlineKeyboardButton("3 дни - 10 лв", callback_data="dur_3дни_10лв")],
        [InlineKeyboardButton("Седмица - 20 лв", callback_data="dur_седмица_20лв")],
        [InlineKeyboardButton("Месец - 50 лв", callback_data="dur_месец_50лв")],
        [InlineKeyboardButton("Безплатно", callback_data="dur_безплатно")]
    ]
    await update.message.reply_text("Супер! 👇\n\n*За колко време?*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return DURATION

async def duration_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    duration = query.data.replace("dur_", "")
    category = context.user_data['category']
    city = context.user_data['city']
    header = f"📢 *{category} | {city}* | ⏱️ {duration}\n\n"
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=header, parse_mode="Markdown")
        await context.bot.copy_message(chat_id=CHANNEL_ID, from_chat_id=context.user_data['ad_chat_id'], message_id=context.user_data['ad_message_id'])
        await query.edit_message_text(f"✅ *Обявата ти е пусната!*\n\n{PRICE_TEXT}", parse_mode="Markdown")
    except Exception as e:
        await query.edit_message_text(f"Грешка: {e}\nУвери се че бота е админ в канала!")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отказано. Пиши /start за нова обява.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CATEGORY: [CallbackQueryHandler(category_chosen, pattern="^cat_")],
            CITY: [CallbackQueryHandler(city_chosen, pattern="^city_")],
            AD_CONTENT: [MessageHandler(filters.ALL & ~filters.COMMAND, ad_received)],
            DURATION: [CallbackQueryHandler(duration_chosen, pattern="^dur_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(conv)
    print("Бота тръгна...")
    app.run_polling()

if __name__ == "__main__":
    main()
