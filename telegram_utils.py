# telegram_utils.py
import asyncio
from telegram import Bot
from telegram.error import TelegramError

async def _send_async(bot, chat_id, msg):
    await bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")

def send_telegram_message(bot, chat_id, msg):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(_send_async(bot, chat_id, msg), loop)
        else:
            loop.run_until_complete(_send_async(bot, chat_id, msg))
    except RuntimeError:
        # Si no hay loop o ya está cerrado, creamos uno nuevo
        asyncio.run(_send_async(bot, chat_id, msg))
    except TelegramError as e:
        print(f"❌ Error de Telegram: {e}")
