import time
from datetime import datetime
from binance_api import realizar_orden_compra, realizar_orden_venta, obtener_saldo
from telegram_report import enviar_reporte_telegram

pares = ["PEPEUSDT", "USDTPEPE"]
cantidad_por_orden = 1

def extraer_base(par):
    return par.replace("USDT", "")

def ejecutar_bot_durante_5_minutos(callback_detener):
    inicio = time.time()
    total_compras = 0.0
    total_ventas = 0.0
    saldos_iniciales = {}
    saldos_finales = {}
    reporte_detallado = "*📊 INFORME DETALLADO DE OPERACIONES*\n\n"

    tokens = set([extraer_base(par) for par in pares])
    tokens.add("USDT")

    for token in tokens:
        saldos_iniciales[token] = obtener_saldo(token)

    with open("log.txt", "a", encoding="utf-8") as log:
        log.write("🚀 Iniciando bot de trading por 5 minutos...\n")

        while not callback_detener() and (time.time() - inicio < 300):
            for par in pares:
                if callback_detener() or (time.time() - inicio > 300):
                    break

                base = extraer_base(par)
                quote = "USDT"

                saldo_base = obtener_saldo(base)
                saldo_usdt = obtener_saldo(quote)

                log.write(f"💰 Saldo actual {base}: {saldo_base:.6f}, USDT: {saldo_usdt:.2f}\n")
                print(f"💰 Saldo {base}: {saldo_base:.6f} | USDT: {saldo_usdt:.2f}")

                reporte_detallado += f"*🔁 {par}*\n"
                reporte_detallado += f"- Saldo inicial {base}: `{saldo_base:.6f}`\n"
                reporte_detallado += f"- Saldo inicial USDT: `{saldo_usdt:.2f}`\n"

                if saldo_usdt < 1:
                    log.write("❌ Saldo insuficiente en USDT para comprar\n")
                    reporte_detallado += "❌ _Saldo insuficiente para comprar_\n\n"
                    continue

                try:
                    orden_compra = realizar_orden_compra(par, cantidad_por_orden)
                    precio_compra = float(orden_compra['fills'][0]['price'])
                    total_compras += precio_compra * cantidad_por_orden
                    log.write(f"✔ Compra ejecutada a ${precio_compra:.6f}\n")
                    reporte_detallado += f"✅ Compra realizada a: `${precio_compra:.4f}`\n"
                except Exception as e:
                    log.write(f"❌ Error al comprar {par}: {e}\n")
                    reporte_detallado += f"❌ Error al comprar: `{e}`\n\n"
                    continue

                time.sleep(2)

                try:
                    orden_venta = realizar_orden_venta(par, cantidad_por_orden)
                    precio_venta = float(orden_venta['fills'][0]['price'])
                    total_ventas += precio_venta * cantidad_por_orden
                    log.write(f"✔ Venta ejecutada a ${precio_venta:.6f}\n")
                    reporte_detallado += f"✅ Venta realizada a: `${precio_venta:.4f}`\n"
                except Exception as e:
                    log.write(f"❌ Error al vender {par}: {e}\n")
                    reporte_detallado += f"❌ Error al vender: `{e}`\n"

                saldo_token_fin = obtener_saldo(base)
                saldo_usdt_fin = obtener_saldo("USDT")
                saldos_finales[base] = saldo_token_fin
                saldos_finales["USDT"] = saldo_usdt_fin

                reporte_detallado += f"- Saldo final {base}: `{saldo_token_fin:.6f}`\n"
                reporte_detallado += f"- Saldo final USDT: `{saldo_usdt_fin:.2f}`\n\n"

                time.sleep(2)

        ganancia = total_ventas - total_compras

        # Estimación total final en USDT
        total_final_estimado = saldos_finales.get("USDT", 0.0)
        for token in tokens:
            if token != "USDT":
                try:
                    par = token + "USDT"
                    precio_actual = float(realizar_orden_venta(par, 0.000001)['fills'][0]['price'])
                    total_final_estimado += saldos_finales.get(token, 0.0) * precio_actual
                except:
                    pass

        reporte_detallado += "-------------------------\n"
        reporte_detallado += f"*💸 Total Comprado:* `${total_compras:.2f}`\n"
        reporte_detallado += f"*💰 Total Vendido:* `${total_ventas:.2f}`\n"
        reporte_detallado += f"*📈 Ganancia:* `${ganancia:.2f}`\n"
        reporte_detallado += f"_🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n"
        reporte_detallado += f"\n💼 *Total estimado final:* `${total_final_estimado:.2f}`"

        print(reporte_detallado)
        log.write(reporte_detallado + "\n")
        enviar_reporte_telegram(reporte_detallado)
