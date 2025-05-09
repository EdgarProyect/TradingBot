import os
import requests
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

def obtener_ip_publica():
    try:
        ip = requests.get("https://api.ipify.org").text
        print(f"🌐 Tu IP pública es: {ip}")
        return ip
    except Exception as e:
        print(f"❌ No se pudo obtener la IP pública: {e}")
        return None

def probar_conexion_binance(api_key, api_secret):
    try:
        client = Client(api_key, api_secret)
        cuenta = client.get_account()
        print("✅ API conectada correctamente. Datos básicos de la cuenta:")
        print(f"   - ID Cuenta: {cuenta['accountType']}")
        print(f"   - Comisiones maker/taker: {cuenta['makerCommission']}/{cuenta['takerCommission']}")
    except Exception as e:
        print(f"❌ ERROR de conexión a Binance:\n{e}")
        if "Invalid API-key" in str(e) or "code=-2015" in str(e):
            print("""
🚨 Problemas comunes:
1. Revisá que tu API KEY y SECRET estén bien escritos en el archivo .env.
2. En Binance:
   🔧 Activá el permiso "Operaciones spot y margen".
   🔒 Si activaste restricción por IP, agregá esta IP pública que detectamos.
3. Verificá que tu clave esté habilitada y no vencida.
            """)
        elif "code=-2014" in str(e):
            print("⚠️ Parece que la API_KEY es válida, pero el SECRET es incorrecto.")
        elif "ConnectionError" in str(e):
            print("🔌 Error de red. ¿Tenés conexión a internet?")
        else:
            print("💡 Error desconocido. Copiá este mensaje y te ayudo a investigarlo.")

# 🚀 Ejecución
if __name__ == "__main__":
    print("🔍 Verificando conexión con Binance API...")
    obtener_ip_publica()
    probar_conexion_binance(api_key, api_secret)
