# /home/edwin/proyectos/bot_trading.py

# ==========================
# IMPORTACIONES PRINCIPALES
# ==========================
import tkinter as tk             # Interfaz gráfica nativa de Python (para ventanas, botones, etc.)
import threading                 # Permite ejecutar funciones en paralelo sin bloquear la interfaz
import time                      # Para pausas, timestamps, etc. (no usado directamente aquí)
from binance.exceptions import BinanceAPIException  # Captura errores específicos de Binance
from datetime import datetime    # Para registrar fecha y hora en logs
from telegram import Bot          # Cliente Telegram para enviar mensajes
import asyncio                   # Necesario para ejecutar funciones async de Telegram
import tkinter.messagebox as messagebox  # Para mostrar mensajes de error en ventanas emergentes
from config import get_settings, get_binance_client, get_telegram_config
# ^ Importa funciones desde tu archivo config.py para traer configuración, cliente Binance y Telegram

# ==========================
# CONFIGURACIÓN INICIAL
# ==========================
settings = get_settings()                       # Carga la configuración general (API keys, etc.)
client = get_binance_client(settings)           # Crea el cliente Binance
TELEGRAM_TOKEN, CHAT_ID = get_telegram_config(settings)  # Token y chat ID de Telegram
bot_telegram = Bot(token=TELEGRAM_TOKEN)        # Inicializa el bot de Telegram

# Lista de activos que se mostrarán incluso con saldo 0
ACTIVOS_RELEVANTES = ["DOGE", "WIF", "PEPE", "FLOKI", "SHIB", "USDT", "BNB"]

# Función para validar la conexión a Binance antes de iniciar
def validar_conexion_binance():
    try:
        # Intenta una operación simple para verificar la API
        client.get_system_status()
        return True, "Conexión a Binance establecida correctamente"
    except BinanceAPIException as e:
        if e.code == -2015:
            return False, f"Error de autenticación en Binance (código -2015):\n\n" \
                   f"1. Verifica que BINANCE_ENV en .env sea 'mainnet' o 'testnet' según tus claves\n" \
                   f"2. Asegúrate que tu IP esté autorizada en la configuración de la API\n" \
                   f"3. Verifica que la API tenga permisos de 'Spot & Margin Trading'\n\n" \
                   f"Ejecuta 'python diagnostico_binance.py' para más detalles."
        else:
            return False, f"Error de Binance: {e}"
    except Exception as e:
        return False, f"Error de conexión: {e}"

# ==========================
# INTERFAZ GRÁFICA (TKINTER)
# ==========================
root = tk.Tk()                                 # Crea la ventana principal
root.title("Bot de Trading Binance")           # Título de la ventana

# Etiqueta principal para mostrar estado o tiempo
label = tk.Label(root, text="Tiempo restante: 00:00:00", font=("Arial", 24))
label.pack()

# Etiqueta secundaria: estado de conexión con Binance
conexion_label = tk.Label(root, text="Conexión con Binance: Desconectado", font=("Arial", 16))
conexion_label.pack()

# ==========================
# FUNCIONES DE TELEGRAM
# ==========================
def enviar_reporte_telegram(mensaje):
    """Envía un mensaje a Telegram manejando correctamente el loop asyncio."""
    async def enviar():
        try:
            await bot_telegram.send_message(
                chat_id=CHAT_ID,
                text=mensaje,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"❌ Error al enviar mensaje a Telegram: {e}")

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Si ya hay un loop (por ejemplo, Tkinter o threading), usamos este
            asyncio.run_coroutine_threadsafe(enviar(), loop)
        else:
            # Si no hay loop activo, lo ejecutamos normalmente
            loop.run_until_complete(enviar())
    except RuntimeError:
        # Si el loop está cerrado, creamos uno nuevo (previene el error "Event loop is closed")
        asyncio.run(enviar())

# ==========================
# FUNCIÓN: VERIFICAR API
# ==========================
def verificar_api_y_enviar_info():
    """Verifica conexión con Binance y envía balances relevantes a Telegram."""
    try:
        cuenta = client.get_account()  # Llama a la API para obtener info de cuenta

        mensaje = [
            "✅ *API conectada correctamente.*",
            f"📊 Tipo de cuenta: {cuenta['accountType']}",
            f"💸 Comisiones maker/taker: {cuenta['makerCommission']}/{cuenta['takerCommission']}",
            "\n📦 *Saldos relevantes:*"
        ]

        # Recorre los activos definidos y obtiene su balance
        for activo in ACTIVOS_RELEVANTES:
            saldo = client.get_asset_balance(asset=activo)
            mensaje.append(f"   - {activo}: {saldo['free']}")

        # Une el mensaje en un solo texto
        mensaje_final = "\n".join(mensaje)

        print(mensaje_final)                              # Muestra en consola
        enviar_reporte_telegram(mensaje_final)            # Envía por Telegram
        conexion_label.config(text="✅ Conexión y verificación completadas")  # Actualiza GUI

        # Registra el resultado en un log
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Verificación API:\n{mensaje_final}\n\n")

    except Exception as e:
        mensaje_error = f"❌ Error al verificar la API: {e}"
        print(mensaje_error)
        enviar_reporte_telegram(mensaje_error)
        conexion_label.config(text="❌ Error en verificación API")

        # Log del error
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Error verificación API: {e}\n")

# ==========================
# FUNCIÓN: ESTRATEGIA DE TRADING
# ==========================
def ejecutar_estrategia():
    """Ejecuta la estrategia: compra BTC con USDT si hay saldo suficiente."""
    print("💰 Ejecutando estrategia de trading...")

    try:
        balance = client.get_asset_balance(asset="USDT")     # Obtiene saldo USDT
        disponible = float(balance["free"])
        print(f"💸 Saldo disponible: {disponible} USDT")

        if disponible < 15:                                  # Monto mínimo
            raise Exception("Saldo insuficiente para realizar la compra mínima.")

        # ⚠️ Aquí se ejecuta una orden REAL si las API keys son live
        orden = client.order_market_buy(symbol="BTCUSDT", quantity=0.001)

        mensaje = f"✅ *Orden ejecutada correctamente*\n{orden}\n🕒 {datetime.now()}"
        enviar_reporte_telegram(mensaje)

        # Guarda registro de la orden
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Orden ejecutada: {orden}\n")

    # Error específico de Binance
    except BinanceAPIException as e:
        mensaje = f"❌ *Error en orden de compra (Binance)*:\n{e}\n🕒 {datetime.now()}"
        print(mensaje)
        enviar_reporte_telegram(mensaje)
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Error Binance: {e}\n")

    # Cualquier otro error general
    except Exception as e:
        mensaje = f"⚠️ *Error general en la estrategia*:\n{e}\n🕒 {datetime.now()}"
        print(mensaje)
        enviar_reporte_telegram(mensaje)
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} - Error general: {e}\n")

# ==========================
# FUNCIÓN: TEST TELEGRAM
# ==========================
def test_telegram():
    """Envía un mensaje de prueba para comprobar la conexión con Telegram."""
    mensaje = f"🚀 *Prueba de Telegram completada correctamente.*\n🕒 {datetime.now()}"
    enviar_reporte_telegram(mensaje)
    print("📨 Mensaje de prueba enviado a Telegram.")

# ==========================
# FUNCIÓN: INICIAR BOT
# ==========================
def iniciar_bot():
    """Lanza la verificación y luego ejecuta la estrategia en otro hilo."""
    # Validar conexión a Binance antes de iniciar
    conexion_ok, mensaje = validar_conexion_binance()
    if not conexion_ok:
        messagebox.showerror("Error de conexión", mensaje)
        conexion_label.config(text="❌ Error de conexión con Binance")
        return
        
    verificar_api_y_enviar_info()              # Verifica API primero
    label.config(text="Ejecutando estrategia...")  # Actualiza texto en GUI

    # Crea hilo para ejecutar la estrategia sin bloquear interfaz
    nuevo_hilo = threading.Thread(target=ejecutar_estrategia)
    nuevo_hilo.start()

# ==========================
# BOTONES PRINCIPALES
# ==========================
boton_iniciar = tk.Button(root, text="Iniciar Bot de Trading", command=iniciar_bot)
boton_iniciar.pack(pady=10)

boton_test = tk.Button(root, text="Probar Telegram 📡", command=test_telegram)
boton_test.pack(pady=5)

# ==========================
# LOOP PRINCIPAL DE LA INTERFAZ
# ==========================
root.mainloop()  # Mantiene la ventana abierta y en escucha de eventos
