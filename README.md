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

## Ejecución con Docker

Requisitos previos:
- Instala Docker Desktop.
- Crea un archivo `.env` en la raíz con:
  - `BINANCE_API_KEY`, `BINANCE_API_SECRET`, `TELEGRAM_TOKEN` (y otros que uses).

Servicios disponibles:
- `telegram_bot`: ejecuta `bot_telegram.py` (principal).
- `v_api`: ejecuta `v_api.py` para verificar conexión con Binance.
- `get_chat_id`: ejecuta `get_chat_id.py` para obtener tu chat ID de Telegram.

Comandos básicos:
- Construir imagen y levantar el bot de Telegram:
  ```
  docker compose up -d --build telegram_bot
  ```
- Ver logs del bot de Telegram:
  ```
  docker compose logs -f telegram_bot
  ```
- Ejecutar el verificador de API de Binance:
  ```
  docker compose up --build v_api
  ```
- Ejecutar utilidad para obtener el chat ID de Telegram:
  ```
  docker compose up --build get_chat_id
  ```
- Detener y eliminar contenedores/red:
  ```
  docker compose down
  ```

Notas:
- La interfaz gráfica `tkinter` (`main.py`) no es compatible dentro del contenedor. Usa los scripts de línea de comandos o el bot de Telegram.
- Si tu API de Binance usa restricción por IP, recuerda autorizar la IP pública de tu host (el contenedor saldrá por esa misma IP).
- Las variables del `.env` se inyectan en los servicios mediante `env_file` de Compose; no se copia el archivo dentro de la imagen.

## Producción

- Imagen endurecida:
  - Se ejecuta como usuario no-root (`appuser`).
  - Certificados del sistema disponibles para requests.
- Healthchecks:
  - `telegram_bot` valida el token con `getMe` (via `healthcheck_telegram.py`).
  - `v_api` valida conectividad pública a Binance (`healthcheck_binance.py`).
  - Puedes ver el estado: `docker compose ps`.
- Logs persistentes:
  - Los servicios montan `./logs:/app/logs`.
  - El bot escribe en `logs/telegram_bot.log`.
- Operación:
  - Arranque: `docker compose up -d --build telegram_bot`.
  - Ver salud: `docker compose ps` (estado `healthy` tras pasar healthcheck).
  - Logs: `docker compose logs -f telegram_bot` o mirando archivos en `./logs`.
- Buenas prácticas:
  - Rotar tokens periódicamente y limitar permisos.
  - Restringir por IP en Binance cuando sea posible.
  - Backups del directorio `./logs` si necesitas auditoría.

## Observabilidad: Portainer y Watchtower

- Portainer (UI de Docker):
  - Levantar: `docker compose up -d --build portainer`.
  - Acceso: `https://localhost:9443` (crea el usuario admin al primer ingreso).
  - Gestión: contenedores, imágenes, volúmenes, y healthchecks desde la UI.

- Watchtower (actualizaciones automáticas):
  - Levantar: `docker compose up -d --build watchtower`.
  - Configuración:
    - Actualiza solo servicios etiquetados (`com.centurylinklabs.watchtower.enable=true`).
    - Limpia imágenes antiguas (`WATCHTOWER_CLEANUP=true`).
    - Intervalo de sondeo: `WATCHTOWER_POLL_INTERVAL=300` segundos.
    - Notificaciones Telegram con `.env`: `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID`.
  - Comprobar logs: `docker compose logs -f watchtower`.
  - Nota: si prefieres cron en vez de intervalo, ajusta `WATCHTOWER_SCHEDULE`, por ejemplo: `0 0 * * *` (todos los días a medianoche).

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