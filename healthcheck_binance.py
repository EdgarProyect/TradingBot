import sys
import requests

def main():
    # Simple ping a la API pública de Binance
    try:
        r = requests.get("https://api.binance.com/api/v3/ping", timeout=8)
        if r.status_code == 200:
            sys.exit(0)
        else:
            print(f"Healthcheck Binance falló: status={r.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"Healthcheck Binance error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()