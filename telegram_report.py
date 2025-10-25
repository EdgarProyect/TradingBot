import requests
from config import get_telegram_config

BOT_TOKEN, CHAT_ID = get_telegram_config()

def enviar_reporte_telegram(mensaje):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"❌ Error enviando mensaje a Telegram: {e}")
