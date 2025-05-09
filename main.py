import tkinter as tk
import threading
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv
import os
from datetime import datetime
from telegram import Bot

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Cliente de Binance
client = Client(API_KEY, API_SECRET)
bot_telegram = Bot(token=TELEGRAM_TOKEN)

# Ventana Tkinter
root = tk.Tk()
root.title("Bot de Trading Binance")
root.geometry("500x250")

label = tk.Label(root, text="Tiempo restante: 00:00:00", font=("Arial", 24))
label.pack(pady=10)

conexion_label = tk.Label(root, text="Conexión con Binance: Desconectado", font=("Arial", 16))
conexion_label.pack(pady=5)

estado_label = tk.Label(root, text="Estado del bot: En espera", font=("Arial", 14))
estado_label.pack(pady=5)

def verificar_conexion():
    try:
        cuenta = client.get_account()
        conexion_label.config(text="✅ Conectado correctamente a Binance REAL")
    except BinanceAPIException as e:
        conexion_label.config(text=f"❌ Error al conectar: {e.message}")

def enviar_reporte_telegram(mensaje):
    try:
        bot_telegram.send_message(chat_id=CHAT_ID, text=mensaje)
    except Exception as e:
        print(f"❌ Error al enviar mensaje a Telegram: {e}")

def ejecutar_estrategia():
    try:
        estado_label.config(text="💰 Ejecutando estrategia...")
        print("💰 Ejecutando estrategia de trading...")

        # Verificar saldo
        balances = client.get_asset_balance(asset='USDT')
        saldo_usdt = float(balances['free'])
        print(f"💸 Saldo disponible: {saldo_usdt} USDT")

        if saldo_usdt < 10:
            raise Exception("Saldo insuficiente para realizar la compra mínima.")

        ticker = client.get_symbol_ticker(symbol="BTCUSDT")
        precio_btc = float(ticker["price"])
        cantidad_btc = round((saldo_usdt / precio_btc) * 0.98, 6)

        orden = client.order_market_buy(
            symbol="BTCUSDT",
            quantity=cantidad_btc
        )

        mensaje = f"✅ Orden ejecutada:\n{orden}\n🕒 {datetime.now()}"
        enviar_reporte_telegram(mensaje)
        print(mensaje)

        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Orden ejecutada: {orden}\n")

    except BinanceAPIException as e:
        mensaje = f"❌ Error en orden de compra: {e.message}\n🕒 {datetime.now()}"
        enviar_reporte_telegram(mensaje)
        print(mensaje)

        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Error en orden: {e.message}\n")

    except Exception as e:
        mensaje = f"⚠️ Error general: {e}\n🕒 {datetime.now()}"
        enviar_reporte_telegram(mensaje)
        print(mensaje)

        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Error general: {e}\n")

    estado_label.config(text="⏹️ Bot detenido")

def actualizar_contador():
    tiempo_restante = 300  # 5 minutos
    while tiempo_restante > 0:
        horas, resto = divmod(tiempo_restante, 3600)
        minutos, seg = divmod(resto, 60)
        label.after(0, lambda h=horas, m=minutos, s=seg: label.config(text=f"Tiempo restante: {h:02}:{m:02}:{s:02}"))
        time.sleep(1)
        tiempo_restante -= 1

    label.after(0, lambda: label.config(text="¡Tiempo agotado!"))
    ejecutar_estrategia()

# Iniciar el contador desde cero cada vez
def iniciar_bot():
    verificar_conexion()
    estado_label.config(text="⏳ Bot en ejecución")
    hilo = threading.Thread(target=actualizar_contador)
    hilo.start()

boton_iniciar = tk.Button(root, text="▶️ Iniciar Bot de Trading", font=("Arial", 14), command=iniciar_bot)
boton_iniciar.pack(pady=15)

# Iniciar interfaz
root.mainloop()
