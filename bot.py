import time
from binance_api import realizar_orden_compra, realizar_orden_venta
from telegram_report import enviar_reporte_telegram

pares = ["BTCUSDT", "BNBUSDT", "USDTBTC", "USDTBNB"]
cantidad_por_orden = 0.01

def ejecutar_bot_durante_5_minutos(callback_detener):
    inicio = time.time()
    total_compras = 0
    total_ventas = 0

    while not callback_detener() and (time.time() - inicio < 300):  # 5 minutos
        for par in pares:
            if callback_detener() or (time.time() - inicio > 300): break
            print(f"Comprando {par}")
            orden_compra = realizar_orden_compra(par, cantidad_por_orden)
            if orden_compra:
                total_compras += float(orden_compra['fills'][0]['price']) * cantidad_por_orden

            time.sleep(2)

            print(f"Vendiendo {par}")
            orden_venta = realizar_orden_venta(par, cantidad_por_orden)
            if orden_venta:
                total_ventas += float(orden_venta['fills'][0]['price']) * cantidad_por_orden

            time.sleep(2)

    ganancia = total_ventas - total_compras
    mensaje = f"🧾 Reporte final:\nComprado: ${total_compras:.2f}\nVendido: ${total_ventas:.2f}\nGanancia: ${ganancia:.2f}"
    print(mensaje)
    enviar_reporte_telegram(mensaje)

    import time
from binance_api import realizar_orden_compra, realizar_orden_venta

def ejecutar_bot(should_stop):
    with open("log.txt", "a", encoding="utf-8") as log:
        for _ in range(5):  # Simula 5 ciclos
            if should_stop():
                log.write("⛔ Bot detenido anticipadamente\n")
                break
            log.write("💰 Ejecutando estrategia de trading...\n")
            try:
                realizar_orden_compra("BTCUSDT", 0.0001)
                log.write("✔ Orden de compra realizada\n")
                time.sleep(1)
                realizar_orden_venta("BTCUSDT", 0.0001)
                log.write("✔ Orden de venta realizada\n")
            except Exception as e:
                log.write(f"❌ Error en orden: {e}\n")
            time.sleep(1)
