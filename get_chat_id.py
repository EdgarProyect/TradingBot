from telegram import Update
from telegram.ext import Application, CommandHandler
from config import get_telegram_config

TOKEN, _ = get_telegram_config()

async def start(update: Update, context):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"✅ Tu chat_id es: {chat_id}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
print("📡 Ejecutando bot... Enviá /start desde Telegram para obtener tu chat_id.")
app.run_polling()
