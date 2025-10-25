import time
from binance_api import realizar_orden_compra, realizar_orden_venta

pares = ["DAIBNB"]
cantidad_por_orden = 0.01

def ejecutar_bot(callback_detener):
    while not callback_detener():
        for par in pares:
            if callback_detener(): break
            print(f"Comprando {par}")
            try:
                realizar_orden_compra(par, cantidad_por_orden)
                time.sleep(2)
                print(f"Vendiendo {par}")
                realizar_orden_venta(par, cantidad_por_orden)
                time.sleep(2)
            except Exception as e:
                print(f"Error con {par}: {e}")
        time.sleep(10)
