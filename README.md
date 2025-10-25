# Bot de Trading Automático para Binance

Bot de trading automático que opera en la plataforma Binance utilizando su API oficial. El bot está diseñado para ejecutar estrategias de trading en criptomonedas de bajo precio con alto potencial de rentabilidad.

## Características

- Conexión segura a la API de Binance
- Interfaz gráfica para control y monitoreo
- Notificaciones por Telegram
- Selección automática de pares de criptomonedas
- Gestión de riesgos con stop-loss y take-profit
- Registro detallado de operaciones

## Requisitos

- Python 3.6+
- Cuenta en Binance con API Key y Secret
- Bot de Telegram (opcional para notificaciones)

## Instalación

1. Clona este repositorio:
```
git clone https://github.com/tu-usuario/bot-trae.git
cd bot-trae
```

2. Instala las dependencias:
```
pip install -r requirements.txt
```

3. Crea un archivo `.env` con tus credenciales:
```
BINANCE_API_KEY=tu_api_key
BINANCE_API_SECRET=tu_api_secret
TELEGRAM_TOKEN=token_de_tu_bot
TELEGRAM_CHAT_ID=tu_chat_id
BINANCE_ENV=testnet  # Cambia a 'mainnet' para operar con dinero real
```

## Uso

Para iniciar el bot con interfaz gráfica:
```
python main.py
```

Para verificar la conexión con la API de Binance:
```
python v_api.py
```

## Archivos principales

- `main.py`: Interfaz gráfica y punto de entrada principal
- `binance_api.py`: Funciones para interactuar con la API de Binance
- `binance_bot.py`: Implementación de estrategias de trading
- `config.py`: Gestión de configuración y credenciales
- `v_api.py`: Herramienta para verificar la conexión con Binance

## Seguridad

⚠️ **IMPORTANTE**: Nunca compartas tus claves API. Se recomienda:
- Usar restricciones por IP en la configuración de la API de Binance
- Desactivar los permisos de retiro de fondos
- Probar primero en el entorno de pruebas (testnet)

## Descargo de responsabilidad

Este software se proporciona "tal cual", sin garantías de ningún tipo. El trading de criptomonedas implica riesgos significativos y podrías perder tu inversión. Este bot es una herramienta educativa y no constituye asesoramiento financiero.

## Licencia

[MIT](LICENSE)