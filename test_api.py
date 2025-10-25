from config import get_binance_client

client = get_binance_client()

try:
    cuenta = client.get_account()
    print("✅ Conexión OK. Datos de cuenta:")
    print(cuenta)
except Exception as e:
    print(f"❌ Error: {e}")
