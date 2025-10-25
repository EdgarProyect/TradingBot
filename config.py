import os
from dataclasses import dataclass
from dotenv import load_dotenv
from binance.client import Client

load_dotenv()


@dataclass(frozen=True)
class Settings:
    binance_api_key: str
    binance_api_secret: str
    telegram_token: str
    telegram_chat_id: str
    binance_env: str = "testnet"


def get_settings() -> Settings:
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    env = os.getenv("BINANCE_ENV", "testnet").lower()

    if not api_key or not api_secret:
        raise ValueError("BINANCE_API_KEY/BINANCE_API_SECRET faltantes en .env")
    if not telegram_token or not chat_id:
        raise ValueError("TELEGRAM_TOKEN/TELEGRAM_CHAT_ID faltantes en .env")
    if env not in ("testnet", "mainnet"):
        env = "testnet"

    return Settings(
        binance_api_key=api_key,
        binance_api_secret=api_secret,
        telegram_token=telegram_token,
        telegram_chat_id=chat_id,
        binance_env=env,
    )


def get_binance_client(settings: Settings | None = None) -> Client:
    s = settings or get_settings()
    client = Client(s.binance_api_key, s.binance_api_secret)
    if s.binance_env == "testnet":
        client.API_URL = "https://testnet.binance.vision/api"
    return client


def get_telegram_config(settings: Settings | None = None):
    s = settings or get_settings()
    return s.telegram_token, s.telegram_chat_id