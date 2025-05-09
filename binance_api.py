import os
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

client = Client(api_key, api_secret)
client.API_URL = 'https://testnet.binance.vision/api'  # Testnet endpoint

def realizar_orden_compra(par, cantidad):
    orden = client.order_market_buy(symbol=par, quantity=cantidad)
    return orden

def realizar_orden_venta(par, cantidad):
    orden = client.order_market_sell(symbol=par, quantity=cantidad)
    return orden
