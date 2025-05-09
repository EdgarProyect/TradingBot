import tkinter as tk
import threading
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv
import os
from datetime import datetime
from telegram import Bot

# Cargar claves reales desde .env
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Token de tu bot de Telegram
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Tu chat ID o el ID de tu grupo

# Instancia del cliente de Binance
client = Client(API_KEY, API_SECRET)

# Crear la ventana principal de Tkinter
root = tk.Tk()

# Crear una etiqueta para mostrar el tiempo restante
label = tk.Label(root, text="Tiempo restante: 00:00:00", font=("Arial", 24))
label.pack()

# Etiqueta de estado de la conexión con Binance
conexion_label = tk.Label(root, text="Conexión con Binance: Desconectado", font=("Arial", 16))
conexion_label.pack()

# Función de verificación de conexión con Binance
def verificar_conexion():
    try:
        cuenta = client.get_account()
        conexion_label.config(text="✅ Conectado correctamente a Binance REAL")
    except BinanceAPIException as e:
        conexion_label.config(text=f"❌ Error al conectar a Binance: {e}")

# Función para enviar un reporte a Telegram
def enviar_reporte_telegram(mensaje):
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=mensaje)

# Función de trading real (simplificada)
def ejecutar_estrategia():
    try:
        print("💰 Ejecutando estrategia de trading...")
        orden = client.order_market_buy(
            symbol="BTCUSDT",
            quantity=0.001
        )
        print("✅ Orden ejecutada:", orden)
        
        # Crear mensaje para el reporte
        mensaje = f"✅ Orden ejecutada: {orden}\nFecha: {datetime.now()}"
        enviar_reporte_telegram(mensaje)  # Enviar reporte a Telegram

        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Orden ejecutada: {orden}\n")
    except BinanceAPIException as e:
        print(f"❌ Error en orden de compra: {e}")
        
        # Crear mensaje para el reporte de error
        mensaje = f"❌ Error en orden de compra: {e}\nFecha: {datetime.now()}"
        enviar_reporte_telegram(mensaje)  # Enviar reporte a Telegram

        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Error en orden: {e}\n")

# Función que actualiza el contador (5 minutos en segundos)
def actualizar_contador():
    tiempo_restante = 300  # 5 minutos en segundos
    while tiempo_restante > 0:
        horas, resto = divmod(tiempo_restante, 3600)
        minutos, seg = divmod(resto, 60)
        
        # Actualizar la etiqueta con la cuenta regresiva
        label.after(0, lambda: label.config(text=f"Tiempo restante: {horas:02}:{minutos:02}:{seg:02}"))
        
        time.sleep(1)
        tiempo_restante -= 1

    # Cuando el contador termine
    label.after(0, lambda: label.config(text="¡Tiempo agotado!"))
    ejecutar_estrategia()

# Crear un hilo para ejecutar el contador en segundo plano
contador_thread = threading.Thread(target=actualizar_contador)

# Función para iniciar la ejecución del bot
def iniciar_bot():
    # Verificar la conexión con Binance
    verificar_conexion()
    # Iniciar el contador y la estrategia de trading
    contador_thread.start()

# Botón para iniciar el bot de trading
boton_iniciar = tk.Button(root, text="Iniciar Bot de Trading", command=iniciar_bot)
boton_iniciar.pack()

# Ejecutar la ventana de Tkinter
root.mainloop()
