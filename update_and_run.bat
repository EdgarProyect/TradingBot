@echo off
echo [>-] Instalando dependencias necesarias para el bot...
pip install -r requirements.txt

echo [>-] Ejecutando bot de trading...
python bot.py

pause