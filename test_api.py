from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

client = Client(api_key, api_secret)

try:
    cuenta = client.get_account()
    print("✅ Conexión OK. Datos de cuenta:")
    print(cuenta)
except Exception as e:
    print(f"❌ Error: {e}")
