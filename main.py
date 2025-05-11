import tkinter as tk
import threading
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv
import os
from datetime import datetime
from telegram import Bot
import asyncio  # IMPORTANTE para Telegram
import requests

# Cargar claves desde .env
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Cliente de Binance
client = Client(API_KEY, API_SECRET)

# Instancia del bot de Telegram
bot_telegram = Bot(token=TELEGRAM_TOKEN)

# Lista de activos a mostrar aunque tengan saldo 0 "WIF", "USDT", "FLOKI", "DOGE", "SHIB"
ACTIVOS_RELEVANTES = ["PEPE", "USDT"]

# Ventana principal de Tkinter
root = tk.Tk()
root.title("Bot de Trading Binance")

label = tk.Label(root, text="Tiempo restante: 00:00:00", font=("Arial", 24))
label.pack()

conexion_label = tk.Label(root, text="Conexión con Binance: Desconectado", font=("Arial", 16))
conexion_label.pack()

# Función asíncrona para enviar mensaje por Telegram
def enviar_reporte_telegram(mensaje):
    async def enviar():
        try:
            await bot_telegram.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode="Markdown")
        except Exception as e:
            print(f"❌ Error al enviar mensaje a Telegram: {e}")
    asyncio.run(enviar())

# Verifica API y saldos y los envía por Telegram
def verificar_api_y_enviar_info():
    try:
        cuenta = client.get_account()
        mensaje = [
            "✅ *API conectada correctamente.*",
            f"📊 Tipo de cuenta: {cuenta['accountType']}",
            f"💸 Comisiones maker/taker: {cuenta['makerCommission']}/{cuenta['takerCommission']}",
            "\n📦 *Saldos relevantes:*"
        ]
        for activo in ACTIVOS_RELEVANTES:
            saldo = client.get_asset_balance(asset=activo)
            mensaje.append(f"   - {activo}: {saldo['free']}")

        mensaje_final = "\n".join(mensaje)
        print(mensaje_final)
        enviar_reporte_telegram(mensaje_final)
        conexion_label.config(text="✅ Conexión y verificación completadas")
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Verificación API:\n{mensaje_final}\n\n")

    except Exception as e:
        mensaje_error = f"❌ Error al verificar la API: {e}"
        print(mensaje_error)
        enviar_reporte_telegram(mensaje_error)
        conexion_label.config(text="❌ Error en verificación API")
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Error verificación API: {e}\n")

# Ejecutar la estrategia real
def ejecutar_estrategia():
    print("💰 Ejecutando estrategia de trading...")
    try:
        balance = client.get_asset_balance(asset="USDT")
        disponible = float(balance["free"])
        print(f"💸 Saldo disponible: {disponible} USDT")

        if disponible < 15:
            raise Exception("Saldo insuficiente para realizar la compra mínima.")

        orden = client.order_market_buy(symbol="BTCUSDT", quantity=0.001)
        mensaje = f"✅ *Orden ejecutada correctamente*\n{orden}\n🕒 {datetime.now()}"
        enviar_reporte_telegram(mensaje)
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Orden ejecutada: {orden}\n")

    except BinanceAPIException as e:
        mensaje = f"❌ *Error en orden de compra (Binance)*:\n{e}\n🕒 {datetime.now()}"
        print(mensaje)
        enviar_reporte_telegram(mensaje)
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Error Binance: {e}\n")

    except Exception as e:
        mensaje = f"⚠️ *Error general en la estrategia*:\n{e}\n🕒 {datetime.now()}"
        print(mensaje)
        enviar_reporte_telegram(mensaje)
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Error general: {e}\n")

# Contador de 5 minutos
def actualizar_contador():
    tiempo_restante = 300
    while tiempo_restante > 0:
        horas, resto = divmod(tiempo_restante, 3600)
        minutos, seg = divmod(resto, 60)
        label.after(0, lambda h=horas, m=minutos, s=seg: label.config(text=f"Tiempo restante: {h:02}:{m:02}:{s:02}"))
        time.sleep(1)
        tiempo_restante -= 1

    label.after(0, lambda: label.config(text="¡Tiempo agotado!"))
    ejecutar_estrategia()

# Iniciar el bot (verifica API primero)
def iniciar_bot():
    verificar_api_y_enviar_info()
    nuevo_hilo = threading.Thread(target=actualizar_contador)
    nuevo_hilo.start()

boton_iniciar = tk.Button(root, text="Iniciar Bot de Trading", command=iniciar_bot)
boton_iniciar.pack()

# Lanzar la interfaz
root.mainloop()

