import os
import sys
import requests

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("TELEGRAM_TOKEN no configurado")
        sys.exit(1)

    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=8)
        if r.status_code == 200 and r.json().get("ok"):
            sys.exit(0)
        else:
            print(f"Healthcheck Telegram falló: status={r.status_code}, body={r.text[:200]}")
            sys.exit(1)
    except Exception as e:
        print(f"Healthcheck Telegram error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()