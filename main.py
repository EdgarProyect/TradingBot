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

# Cargar claves reales desde .env
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Cliente de Binance
client = Client(API_KEY, API_SECRET)

# Instancia del bot de Telegram
bot_telegram = Bot(token=TELEGRAM_TOKEN)

# Ventana principal de Tkinter
root = tk.Tk()
root.title("Bot de Trading Binance")

label = tk.Label(root, text="Tiempo restante: 00:00:00", font=("Arial", 24))
label.pack()

conexion_label = tk.Label(root, text="Conexión con Binance: Desconectado", font=("Arial", 16))
conexion_label.pack()

# Verifica la conexión con Binance
def verificar_conexion():
    try:
        cuenta = client.get_account()
        conexion_label.config(text="✅ Conectado correctamente a Binance REAL")
    except BinanceAPIException as e:
        conexion_label.config(text=f"❌ Error al conectar a Binance: {e}")

# Función asíncrona para enviar el mensaje por Telegram
def enviar_reporte_telegram(mensaje):
    async def enviar():
        try:
            await bot_telegram.send_message(chat_id=CHAT_ID, text=mensaje)
        except Exception as e:
            print(f"❌ Error al enviar mensaje a Telegram: {e}")
    asyncio.run(enviar())

# Ejecutar la estrategia
def ejecutar_estrategia():
    print("💰 Ejecutando estrategia de trading...")
    try:
        balance = client.get_asset_balance(asset="USDT")
        disponible = float(balance["free"])
        print(f"💸 Saldo disponible: {disponible} USDT")

        if disponible < 15:  # Requiere al menos 15 USDT
            raise Exception("Saldo insuficiente para realizar la compra mínima.")

        orden = client.order_market_buy(symbol="BTCUSDT", quantity=0.001)
        mensaje = f"✅ Orden ejecutada:\n{orden}\n🕒 {datetime.now()}"
        enviar_reporte_telegram(mensaje)
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Orden ejecutada: {orden}\n")

    except BinanceAPIException as e:
        mensaje = f"❌ Error en orden de compra: {e}\n🕒 {datetime.now()}"
        print(mensaje)
        enviar_reporte_telegram(mensaje)
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Error Binance: {e}\n")

    except Exception as e:
        mensaje = f"⚠️ Error general: {e}\n🕒 {datetime.now()}"
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

# Crear un nuevo hilo cada vez que se inicia
def iniciar_bot():
    verificar_conexion()
    nuevo_hilo = threading.Thread(target=actualizar_contador)
    nuevo_hilo.start()

boton_iniciar = tk.Button(root, text="Iniciar Bot de Trading", command=iniciar_bot)
boton_iniciar.pack()

# Lanzar la interfaz
root.mainloop()

