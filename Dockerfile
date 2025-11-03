FROM python:3.11-slim

# Evitar bytecode y habilitar salida sin buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Paquetes básicos (algunos libs pueden requerir build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar dependencias primero para aprovechar capa de cache
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copiar el resto del proyecto
COPY . .

# Preparar usuario no-root y directorio de logs
RUN useradd -m -u 1000 appuser \
    && mkdir -p /app/logs \
    && chown -R appuser:appuser /app

USER appuser

# Comando por defecto: bot de Telegram (se puede sobreescribir en compose)
CMD ["python", "bot_telegram.py"]