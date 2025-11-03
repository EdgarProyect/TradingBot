#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de diagnóstico para problemas de conexión con Binance API
Detecta problemas comunes como:
- Credenciales incorrectas
- Restricciones de IP
- Permisos insuficientes
- Configuración incorrecta de testnet/mainnet
"""

import os
import sys
import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException
from config import get_settings, get_binance_client
from dotenv import load_dotenv

# Asegurar que se cargan las variables de entorno
load_dotenv()

# Colores para la salida
VERDE = '\033[92m'
AMARILLO = '\033[93m'
ROJO = '\033[91m'
RESET = '\033[0m'
AZUL = '\033[94m'

def print_ok(mensaje):
    print(f"{VERDE}✓ {mensaje}{RESET}")

def print_warning(mensaje):
    print(f"{AMARILLO}⚠ {mensaje}{RESET}")

def print_error(mensaje):
    print(f"{ROJO}✗ {mensaje}{RESET}")

def print_info(mensaje):
    print(f"{AZUL}ℹ {mensaje}{RESET}")

def verificar_variables_entorno():
    """Verifica que las variables de entorno necesarias estén configuradas"""
    print_info("Verificando variables de entorno...")
    
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    binance_env = os.getenv("BINANCE_ENV", "testnet")
    
    if not api_key or not api_secret:
        print_error("No se encontraron las credenciales de Binance en el archivo .env")
        print_info("Asegúrate de tener BINANCE_API_KEY y BINANCE_API_SECRET en tu archivo .env")
        return False
    
    print_ok(f"API KEY encontrada: {api_key[:4]}...{api_key[-4:]}")
    print_ok(f"API SECRET encontrada: {api_secret[:4]}...{api_secret[-4:]}")
    print_ok(f"BINANCE_ENV configurado como: {binance_env}")
    
    if binance_env == "testnet":
        print_warning("Estás usando el entorno de TESTNET. Asegúrate de que tus claves sean de testnet.")
        print_info("Si tus claves son de producción, cambia BINANCE_ENV=mainnet en tu archivo .env")
    else:
        print_info("Estás usando el entorno de PRODUCCIÓN (mainnet).")
    
    return True

def verificar_ip_publica():
    """Verifica la IP pública desde la que se está haciendo la conexión"""
    print_info("\nVerificando IP pública...")
    
    try:
        response = requests.get("https://api.ipify.org")
        if response.status_code == 200:
            ip = response.text
            print_ok(f"Tu IP pública es: {ip}")
            print_info("Asegúrate de que esta IP esté autorizada en tu cuenta de Binance")
            return ip
        else:
            print_warning("No se pudo determinar tu IP pública")
            return None
    except Exception as e:
        print_error(f"Error al verificar IP: {e}")
        return None

def probar_ping_binance(binance_env):
    """Prueba un simple ping a la API de Binance"""
    print_info("\nProbando conexión básica a Binance (ping)...")
    
    # URL base según el entorno
    base_url = "https://testnet.binance.vision" if binance_env == "testnet" else "https://api.binance.com"
    
    try:
        response = requests.get(f"{base_url}/api/v3/ping")
        if response.status_code == 200:
            print_ok(f"Conexión básica a Binance ({binance_env}) exitosa")
            return True
        else:
            print_error(f"Error en ping a Binance: Status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error de conexión a Binance: {e}")
        return False

def probar_tiempo_servidor(binance_env):
    """Prueba la sincronización de tiempo con el servidor de Binance"""
    print_info("\nVerificando sincronización de tiempo con servidor Binance...")
    
    # URL base según el entorno
    base_url = "https://testnet.binance.vision" if binance_env == "testnet" else "https://api.binance.com"
    
    try:
        response = requests.get(f"{base_url}/api/v3/time")
        if response.status_code == 200:
            server_time = response.json()["serverTime"]
            print_ok(f"Tiempo del servidor Binance: {server_time}")
            return True
        else:
            print_error(f"Error al obtener tiempo del servidor: Status code {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error de conexión a Binance: {e}")
        return False

def probar_api_key():
    """Prueba la API key intentando obtener información de la cuenta"""
    print_info("\nProbando API KEY con get_account()...")
    
    settings = get_settings()
    client = get_binance_client(settings)
    
    try:
        account = client.get_account()
        print_ok("API KEY válida - Conexión exitosa")
        print_info(f"Tipo de cuenta: {account['accountType']}")
        print_info(f"Puede operar: {account['canTrade']}")
        print_info(f"Nivel de comisión maker: {account['makerCommission']}")
        print_info(f"Nivel de comisión taker: {account['takerCommission']}")
        return True
    except BinanceAPIException as e:
        print_error(f"Error de API Binance: {e}")
        
        if e.code == -2015:
            print_info("\nEl error -2015 puede deberse a:")
            print_info("1. API KEY o SECRET incorrectos")
            print_info("2. Tu IP no está autorizada en la configuración de la API")
            print_info("3. La API KEY no tiene los permisos necesarios (necesita 'Enable Reading' como mínimo)")
            print_info("4. Estás usando claves de mainnet en testnet o viceversa")
        
        return False
    except Exception as e:
        print_error(f"Error desconocido: {e}")
        return False

def probar_permisos_trading():
    """Prueba si la API tiene permisos para trading"""
    print_info("\nProbando permisos de trading (consulta de precio)...")
    
    settings = get_settings()
    client = get_binance_client(settings)
    
    try:
        # Intenta obtener el precio de BTC (operación que requiere permisos básicos)
        ticker = client.get_symbol_ticker(symbol="BTCUSDT")
        print_ok(f"Permiso de lectura OK - Precio de BTCUSDT: {ticker['price']}")
        
        # Si llegamos aquí, intentemos ver el balance (requiere permisos de cuenta)
        try:
            balance = client.get_asset_balance(asset='USDT')
            print_ok(f"Permiso de cuenta OK - Balance de USDT: {balance['free']}")
        except BinanceAPIException as e:
            if e.code == -2015:
                print_warning("No tienes permisos para ver balances (necesitas 'Enable Spot & Margin Trading')")
            else:
                print_error(f"Error al verificar balance: {e}")
        
        return True
    except BinanceAPIException as e:
        print_error(f"Error de API Binance: {e}")
        return False
    except Exception as e:
        print_error(f"Error desconocido: {e}")
        return False

def main():
    """Función principal que ejecuta todas las verificaciones"""
    print_info("=== DIAGNÓSTICO DE CONEXIÓN A BINANCE API ===\n")
    
    # Verificar variables de entorno
    if not verificar_variables_entorno():
        return
    
    # Obtener el entorno configurado
    binance_env = os.getenv("BINANCE_ENV", "testnet")
    
    # Verificar IP pública
    ip = verificar_ip_publica()
    
    # Probar ping básico a Binance
    if not probar_ping_binance(binance_env):
        print_error("No se pudo conectar al servidor de Binance. Verifica tu conexión a internet.")
        return
    
    # Probar sincronización de tiempo
    probar_tiempo_servidor(binance_env)
    
    # Probar API key
    if not probar_api_key():
        print_info("\nRECOMENDACIONES:")
        print_info("1. Verifica que tus claves API sean correctas")
        print_info(f"2. Asegúrate de que tu IP ({ip}) esté autorizada en la configuración de la API en Binance")
        print_info("3. Verifica que BINANCE_ENV esté configurado correctamente (mainnet o testnet)")
        print_info("4. Asegúrate de que la API tenga los permisos necesarios (Enable Reading, Enable Spot & Margin Trading)")
        return
    
    # Probar permisos de trading
    probar_permisos_trading()
    
    print_info("\n=== DIAGNÓSTICO COMPLETADO ===")

if __name__ == "__main__":
    main()