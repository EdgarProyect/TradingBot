import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import threading
import time

# Diccionario para almacenar claves API por usuario
user_data = {}
# Diccionario para almacenar los hilos de cada usuario
bot_threads = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Bienvenido al Trading Bot! Usa /setapikeys <APIKEY> <SECRETKEY> para comenzar.")

async def setapikeys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Uso: /setapikeys <APIKEY> <SECRETKEY>")
        return
    user_id = update.effective_user.id
    user_data[user_id] = {
        "api_key": context.args[0],
        "secret_key": context.args[1],
        "status": "ready"
    }
    await update.message.reply_text("Claves API configuradas. Usá /runbot para iniciar.")

def simulated_bot(user_id):
    logging.info(f"Iniciando simulación para usuario {user_id}")
    user_data[user_id]["status"] = "running"
    report = []
    start_time = time.time()
    while time.time() - start_time < 300:
        report.append("Operación simulada ejecutada.")
        time.sleep(10)
    user_data[user_id]["report"] = report
    user_data[user_id]["status"] = "finished"

async def runbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        await update.message.reply_text("Primero configurá tus claves API con /setapikeys.")
        return
    if user_data[user_id]["status"] == "running":
        await update.message.reply_text("Tu bot ya está en ejecución.")
        return
    thread = threading.Thread(target=simulated_bot, args=(user_id,))
    bot_threads[user_id] = thread
    thread.start()
    await update.message.reply_text("Bot iniciado por 5 minutos. Usá /status o /report.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    status = user_data.get(user_id, {}).get("status", "No configurado")
    await update.message.reply_text(f"Estado actual: {status}")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    report = user_data.get(user_id, {}).get("report", None)
    if report:
        await update.message.reply_text("\n".join(report))
    else:
        await update.message.reply_text("Todavía no hay reporte disponible.")

if __name__ == "__main__":
    import os
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "AQUI_TU_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setapikeys", setapikeys))
    app.add_handler(CommandHandler("runbot", runbot))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("report", report))
    app.run_polling()