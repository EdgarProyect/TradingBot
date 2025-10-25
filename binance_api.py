from config import get_binance_client
from datetime import datetime

client = get_binance_client()

def obtener_saldo(token):
    cuenta = client.get_account()
    for activo in cuenta['balances']:
        if activo['asset'] == token:
            return float(activo['free'])
    return 0.0

def realizar_orden_compra(par, cantidad):
    return client.order_market_buy(symbol=par, quantity=cantidad)

def realizar_orden_venta(par, cantidad):
    return client.order_market_sell(symbol=par, quantity=cantidad)

def colocar_orden_compra_con_stop_loss(par, cantidad, stop_loss_porcentaje, take_profit_porcentaje=None):
    """
    Coloca una orden de compra con stop-loss automático
    """
    # Obtener precio actual
    ticker = client.get_symbol_ticker(symbol=par)
    precio_actual = float(ticker['price'])
    
    # Calcular niveles de stop-loss y take-profit
    stop_loss_precio = precio_actual * (1 - stop_loss_porcentaje/100)
    
    # Realizar la compra
    orden_compra = client.order_market_buy(symbol=par, quantity=cantidad)
    
    # Colocar stop-loss
    client.create_order(
        symbol=par,
        side='SELL',
        type='STOP_LOSS_LIMIT',
        timeInForce='GTC',
        quantity=cantidad,
        price=round(stop_loss_precio * 0.99, 8),  # Precio ligeramente menor para asegurar ejecución
        stopPrice=round(stop_loss_precio, 8)
    )
    
    # Colocar take-profit si se especifica
    if take_profit_porcentaje:
        take_profit_precio = precio_actual * (1 + take_profit_porcentaje/100)
        client.create_order(
            symbol=par,
            side='SELL',
            type='TAKE_PROFIT_LIMIT',
            timeInForce='GTC',
            quantity=cantidad,
            price=round(take_profit_precio * 0.99, 8),  # Precio ligeramente menor para asegurar ejecución
            stopPrice=round(take_profit_precio, 8)
        )
    
    return orden_compra

def obtener_pares_baratos(base_asset='USDT', max_pares=5):
    """
    Obtiene los pares más baratos disponibles con la moneda base especificada
    """
    # Obtener información de todos los símbolos
    info = client.get_exchange_info()
    pares_con_base = []
    
    # Filtrar pares con la moneda base especificada
    for s in info['symbols']:
        if s['quoteAsset'] == base_asset and s['status'] == 'TRADING':
            try:
                # Obtener precio actual
                ticker = client.get_symbol_ticker(symbol=s['symbol'])
                precio = float(ticker['price'])
                
                # Obtener volumen de 24h para verificar liquidez
                stats = client.get_24hr_ticker(symbol=s['symbol'])
                volumen_24h = float(stats['quoteVolume'])
                
                # Solo considerar pares con suficiente liquidez
                if volumen_24h > 100000:  # Mínimo 100,000 USDT de volumen diario
                    pares_con_base.append({
                        'symbol': s['symbol'],
                        'price': precio,
                        'volume': volumen_24h
                    })
            except:
                continue
    
    # Ordenar por precio (de menor a mayor)
    pares_con_base.sort(key=lambda x: x['price'])
    
    # Devolver los N pares más baratos
    return pares_con_base[:max_pares]

def registrar_operacion(tipo, par, cantidad, precio, resultado=None):
    """
    Registra una operación en el archivo de log
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("operaciones.log", "a", encoding="utf-8") as log:
        log.write(f"{timestamp} | {tipo} | {par} | {cantidad} | {precio} | {resultado or 'N/A'}\n")
