import os
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler

# Reemplazá esto por tu token real
TOKEN = 'TU_TELEGRAM_TOKEN'

async def start(update: Update, context):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"✅ Tu chat_id es: {chat_id}")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
print("📡 Ejecutando bot... Enviá /start desde Telegram para obtener tu chat_id.")
app.run_polling()
