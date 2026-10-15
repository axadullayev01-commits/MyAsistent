import asyncio
import logging
from telethon import TelegramClient
from telethon.tl.types import SendMessageTypingAction

logger = logging.getLogger(__name__)

# Telegram xabarlarining maksimal belgilar soni
MAX_MESSAGE_LENGTH = 4000


class OutputHandler:
    """Javobni Telegram chatiga yuborish va 'typing...' holatini ko'rsatish."""

    def __init__(self, client: TelegramClient):
        self.client = client

    async def show_typing(self, chat_id: int | str, duration: float = 3.0):
        """Chatda yozayotganlik (typing...) holatini ko'rsatish."""
        try:
            await self.client.send_read_acknowledge(chat_id)
            async with self.client.action(chat_id, "typing"):
                await asyncio.sleep(duration)
        except Exception as e:
            logger.debug(f"Typing action xatolik: {e}")

    async def send_response(self, event, text: str, reply_to: bool = True):
        """Xabarni chatga bo'lib-bo'lib (agar uzun bo'lsa) yuborish."""
        if not text:
            return

        chunks = self._split_text(text, MAX_MESSAGE_LENGTH)

        for i, chunk in enumerate(chunks):
            try:
                if reply_to and i == 0:
                    await event.reply(chunk)
                else:
                    await event.respond(chunk)
            except Exception as e:
                logger.warning(f"Formatlangan xabarni yuborishda xatolik: {e}. Oddiy matn sifatida qayta urinish...")
                try:
                    # Agar markdown xatolik bersa, oddiy matn tarzida yuboramiz
                    await self.client.send_message(
                        event.chat_id,
                        chunk,
                        parse_mode=None,
                        reply_to=event.id if (reply_to and i == 0) else None
                    )
                except Exception as ex:
                    logger.error(f"Xabarni yuborishda kritik xatolik: {ex}")

    @staticmethod
    def _split_text(text: str, limit: int = MAX_MESSAGE_LENGTH) -> list[str]:
        """Uzun matnni Telegram chekloviga mos bo'laklarga ajratish."""
        if len(text) <= limit:
            return [text]

        chunks = []
        while len(text) > limit:
            # So'nggi yangi qator yoki probeldan kesishga harakat qilamiz
            split_at = text.rfind("\n", 0, limit)
            if split_at == -1:
                split_at = text.rfind(" ", 0, limit)
            if split_at == -1:
                split_at = limit

            chunks.append(text[:split_at].strip())
            text = text[split_at:].strip()

        if text:
            chunks.append(text)
        return chunks
