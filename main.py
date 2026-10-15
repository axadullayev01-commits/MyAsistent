import sys
import os
import asyncio
import logging

# Windows konsolida UTF-8 ni to'liq qo'llab-quvvatlash
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from config import (
    API_ID,
    API_HASH,
    SESSION_NAME,
    STRING_SESSION,
    PORT,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    BASE_DIR
)
from database.context_manager import context_manager
from handlers.message_handler import MessageHandler
from utils.helpers import print_banner

# Loglarni sozlash
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("AI_Userbot")


async def main():
    print_banner()

    # Sozlamalarni tekshirish
    if not API_ID or not API_HASH:
        print("\n❌ XATOLIK: Telegram API_ID yoki API_HASH topilmadi!")
        print(f"Iltimos, '{BASE_DIR / '.env'}' faylini oching va my.telegram.org saytidan olingan qiymatlarni kiriting.\n")
        sys.exit(1)

    if not GEMINI_API_KEY:
        print("\n⚠️ DIQQAT: GEMINI_API_KEY kiritilmagan!")
        print("AI ishlashi uchun aistudio.google.com dan API kalit oling va .env fayliga kiriting.\n")

    # SQLite bazasini ishga tushirish
    logger.info("SQLite bazasi initsializatsiya qilinmoqda...")
    await context_manager.init_db()

    # Render yoki bulutli serverlar uchun Web Service Health Check
    web_server = None
    if PORT > 0:
        async def handle_health_check(reader, writer):
            try:
                await reader.read(1024)
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: application/json\r\n"
                    "Content-Length: 26\r\n"
                    "Connection: close\r\n\r\n"
                    '{"status":"ok","bot":"up"}'
                )
                writer.write(response.encode("utf-8"))
                await writer.drain()
            except Exception:
                pass
            finally:
                writer.close()
                try:
                    await writer.wait_closed()
                except Exception:
                    pass

        try:
            web_server = await asyncio.start_server(handle_health_check, "0.0.0.0", PORT)
            logger.info(f"Render Web Service salomatlik tekshiruvi (Health Check) {PORT}-portda ishga tushdi.")
        except Exception as e:
            logger.warning(f"Port {PORT} da web serverni ishga tushirishda xatolik: {e}")

    # Telethon mijozini yaratish (STRING_SESSION yoki fayl orqali)
    if STRING_SESSION:
        logger.info("Telethon StringSession orqali ishga tushirilmoqda...")
        client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
    else:
        session_path = BASE_DIR / SESSION_NAME
        client = TelegramClient(str(session_path), API_ID, API_HASH)

    # Message Handlerni sozlash
    msg_handler = MessageHandler(client)

    @client.on(events.NewMessage)
    async def incoming_message_listener(event):
        try:
            await msg_handler.route_message(event)
        except Exception as e:
            logger.error(f"Xabarni qayta ishlashda kutilmagan xatolik: {e}", exc_info=True)

    # Telethon hisobiga ulanish
    logger.info("Telegramga ulanilmoqda...")
    await client.start()
    await msg_handler.init_me()

    logger.info(f"AI Userbot muvaffaqiyatli ishga tushdi! Model: {GEMINI_MODEL}")
    logger.info("Telegramdagi xabarlar kutilmoqda. To'xtatish uchun: Ctrl + C")

    # Botni doimiy rejimda ushlab turish
    await client.run_until_disconnected()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 AI Userbot to'xtatildi.")
    except Exception as err:
        logger.error(f"Kutilmagan xatolik: {err}", exc_info=True)
