import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
import os
import threading
import time
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables del entorno (.env)
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Constantes de trading , "WIFUSDT", "PEPEUSDT", "FLOKIUSDT", "SHIBUSDT"
PARES = ["PEPEFLOKI"] 
CANTIDAD_POR_ORDEN = 1

# Datos por usuario y threads
user_data = {}
bot_threads = {}

# --- Comandos ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ¡Bienvenido al Bot de Trading!\n\n"
        "Comandos disponibles:\n"
        "/setapikeys <APIKEY> <SECRETKEY> - Configura tus claves API\n"
        "/status - Ver estado actual\n"
        "/runbot - Iniciar bot de trading\n"
        "/report - Ver últimos 5 reportes"
    )

async def setapikeys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("❌ Uso correcto: /setapikeys <APIKEY> <SECRETKEY>")
        return

    user_id = update.effective_user.id
    api_key = context.args[0]
    secret_key = context.args[1]

    await update.message.reply_text("🔄 Verificando las claves API...")

    try:
        client = Client(api_key, secret_key)
        # Probar las claves obteniendo la cuenta
        account = client.get_account()
        
        # Verificar que podemos obtener el balance
        balance = client.get_asset_balance(asset='USDT')
        
        user_data[user_id] = {
            "api_key": api_key,
            "secret_key": secret_key,
            "status": "ready",
            "client": client,
            "last_report": f"✅ Balance USDT: {balance['free']}",
            "report_history": []  # Lista para almacenar historial de reportes
        }

        await update.message.reply_text(
            "✅ Claves API configuradas correctamente\n"
            f"💰 Balance USDT: {balance['free']}\n"
            "🚀 Usa /runbot para comenzar el trading"
        )
    except BinanceAPIException as e:
        await update.message.reply_text(f"❌ Error de Binance: {e.message}\n⚠️ Verifica tus claves API")
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error inesperado: {str(e)}\n"
            "⚠️ Asegúrate de que:\n"
            "1. Las claves API son correctas\n"
            "2. Tienes permisos de trading habilitados\n"
            "3. La IP está permitida en Binance"
        )

async def runbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_data:
        await update.message.reply_text("❌ Primero configura tus claves con /setapikeys")
        return

    if user_data[user_id]["status"] == "running":
        await update.message.reply_text("⚠️ El bot ya está en ejecución.")
        return

    thread = threading.Thread(target=ejecutar_trading, args=(user_id,))
    bot_threads[user_id] = thread
    thread.start()

    await update.message.reply_text("🚀 Bot iniciado. Usa /status para ver el estado.")

def ejecutar_trading(user_id):
    user = user_data[user_id]
    client = user["client"]
    user["status"] = "running"
    start_time = time.time()

    try:
        while time.time() - start_time < 300 and user["status"] == "running":
            for par in PARES:
                try:
                    balance = client.get_asset_balance(asset="USDT")
                    disponible = float(balance["free"])

                    if disponible < 15:
                        nuevo_reporte = f"❌ Saldo insuficiente en {par}"
                        user["last_report"] = nuevo_reporte
                        user["report_history"].insert(0, f"{datetime.now().strftime('%H:%M:%S')} - {nuevo_reporte}")
                        user["report_history"] = user["report_history"][:5]
                        continue

                    # Compra
                    client.order_market_buy(symbol=par, quantity=CANTIDAD_POR_ORDEN)
                    time.sleep(2)

                    # Venta
                    client.order_market_sell(symbol=par, quantity=CANTIDAD_POR_ORDEN)
                    time.sleep(2)

                    nuevo_reporte = f"✅ Trade completado en {par}"
                    user["last_report"] = nuevo_reporte
                    user["report_history"].insert(0, f"{datetime.now().strftime('%H:%M:%S')} - {nuevo_reporte}")
                    user["report_history"] = user["report_history"][:5]

                except Exception as e:
                    nuevo_reporte = f"❌ Error en {par}: {str(e)}"
                    user["last_report"] = nuevo_reporte
                    user["report_history"].insert(0, f"{datetime.now().strftime('%H:%M:%S')} - {nuevo_reporte}")
                    user["report_history"] = user["report_history"][:5]
                    logger.error(f"Error en trading para {user_id}: {e}")
    finally:
        user["status"] = "finished"

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_data:
        await update.message.reply_text("❌ No has configurado tus claves.")
        return

    estado = user_data[user_id]["status"]
    historial = user_data[user_id].get("report_history", [])
    
    mensaje = f"📊 Estado: {estado}\n\n📝 Últimos reportes:\n"
    if historial:
        mensaje += "\n".join(historial)
    else:
        mensaje += "No hay reportes disponibles."
    
    await update.message.reply_text(mensaje)

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        await update.message.reply_text("❌ No hay datos para mostrar. Usa /setapikeys primero.")
        return
        
    historial = user_data[user_id].get("report_history", [])
    if historial:
        mensaje = "📝 Últimos 5 reportes:\n" + "\n".join(historial)
    else:
        mensaje = "📝 No hay reportes disponibles."
    
    await update.message.reply_text(mensaje)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setapikeys", setapikeys))
    app.add_handler(CommandHandler("runbot", runbot))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("report", report))

    logger.info("🤖 Bot de Telegram en marcha")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()