import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import threading
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
from datetime import datetime
from dotenv import load_dotenv

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Verificar que el token existe y es válido
if not TELEGRAM_TOKEN:
    raise ValueError("❌ Error: No se encontró TELEGRAM_TOKEN en el archivo .env")

if TELEGRAM_TOKEN == "AQUI_TU_TOKEN":
    raise ValueError("❌ Error: Por favor, reemplaza AQUI_TU_TOKEN con tu token real de Telegram")

# Configuración de trading
PARES = ["DOGEUSDT", "WIFUSDT", "PEPEUSDT", "FLOKIUSDT", "SHIBUSDT"]
CANTIDAD_POR_ORDEN = 1

# Diccionario para almacenar datos de usuarios
user_data = {}
bot_threads = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 ¡Bienvenido al Bot de Trading!\n\n"
        "Comandos disponibles:\n"
        "/setAPIKEY - Configura tu clave API de Binance\n"
        "/setSECRETKEY - Configura tu clave secreta de Binance\n"
        "/status - Ver estado actual\n"
        "/runbot - Iniciar bot de trading\n"
        "/report - Ver último reporte"
    )

async def setAPIKEY(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Uso: /setAPIKEY <APIKEY>")
        return
    
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {"status": "configuring"}
    
    user_data[user_id]["api_key"] = context.args[0]
    await update.message.reply_text("✅ API Key configurada. Ahora configura la Secret Key con /setSECRETKEY")

async def setSECRETKEY(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Uso: /setSECRETKEY <SECRETKEY>")
        return
    
    user_id = update.effective_user.id
    if user_id not in user_data or "api_key" not in user_data[user_id]:
        await update.message.reply_text("❌ Primero configura tu API Key con /setAPIKEY")
        return
    
    try:
        api_key = user_data[user_id]["api_key"]
        secret_key = context.args[0]
        client = Client(api_key, secret_key)
        # Verificar que las claves son válidas intentando obtener la cuenta
        client.get_account()
        
        user_data[user_id].update({
            "secret_key": secret_key,
            "status": "ready",
            "client": client
        })
        await update.message.reply_text("✅ Claves API configuradas correctamente. Usa /runbot para iniciar el trading.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al configurar las claves: {str(e)}")

def ejecutar_trading(user_id):
    user = user_data[user_id]
    client = user["client"]
    user["status"] = "running"
    start_time = time.time()
    
    while time.time() - start_time < 300 and user["status"] == "running":
        try:
            for par in PARES:
                balance = client.get_asset_balance(asset="USDT")
                disponible = float(balance["free"])
                
                if disponible < 15:
                    user["last_report"] = "❌ Saldo insuficiente para operar"
                    continue
                
                # Ejecutar orden de compra
                orden = client.order_market_buy(symbol=par, quantity=CANTIDAD_POR_ORDEN)
                time.sleep(2)
                
                # Ejecutar orden de venta
                orden_venta = client.order_market_sell(symbol=par, quantity=CANTIDAD_POR_ORDEN)
                time.sleep(2)
                
                user["last_report"] = f"✅ Operación completada en {par}"
                
        except Exception as e:
            user["last_report"] = f"❌ Error: {str(e)}"
            logger.error(f"Error en trading para usuario {user_id}: {e}")
            
    user["status"] = "finished"

async def runbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in user_data:
        await update.message.reply_text("❌ Primero configura tus claves API con /setAPIKEY")
        return
        
    if user_data[user_id]["status"] == "running":
        await update.message.reply_text("⚠️ El bot ya está en ejecución")
        return
        
    thread = threading.Thread(target=ejecutar_trading, args=(user_id,))
    bot_threads[user_id] = thread
    thread.start()
    await update.message.reply_text("🚀 Bot iniciado. Usa /status para ver el estado")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        await update.message.reply_text("❌ No has configurado tus claves API")
        return
        
    status = user_data[user_id]["status"]
    last_report = user_data[user_id].get("last_report", "Sin operaciones")
    await update.message.reply_text(f"📊 Estado: {status}\n📝 Último reporte: {last_report}")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setAPIKEY", setAPIKEY))
    app.add_handler(CommandHandler("setSECRETKEY", setSECRETKEY))
    app.add_handler(CommandHandler("runbot", runbot))
    app.add_handler(CommandHandler("status", status))
    
    logger.info("🤖 Bot de Telegram iniciado")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()