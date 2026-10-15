import logging
from telethon import TelegramClient, events
from config import is_chat_whitelisted
from handlers.output_handler import OutputHandler
from handlers.text_handler import TextHandler
from handlers.media_handler import MediaHandler

logger = logging.getLogger(__name__)


class MessageHandler:
    """Telethon xabarlarini qabul qiluvchi va kerakli handlerlarga yo'naltiruvchi markaziy router."""

    def __init__(self, client: TelegramClient):
        self.client = client
        self.output_handler = OutputHandler(client)
        self.text_handler = TextHandler(self.output_handler)
        self.media_handler = MediaHandler(self.output_handler)
        self.me_id = None

    async def init_me(self):
        """Userbot hisob egasining Telegram ID sini aniqlash."""
        me = await self.client.get_me()
        if me:
            self.me_id = me.id
            logger.info(f"Userbot hisobi aniqlandi: @{me.username or me.first_name} (ID: {self.me_id})")

    async def route_message(self, event: events.NewMessage.Event):
        """Kelgan xabarni tahlil qilish va yo'naltirish."""
        # O'zimiz yuborgan buyruqlarni (.clear, .whitelist va hk.) qo'llab-quvvatlash
        is_my_outgoing = event.out and self.me_id and event.sender_id == self.me_id
        chat_id = event.chat_id

        # Whitelist tekshiruvi
        if not is_my_outgoing and not is_chat_whitelisted(chat_id, self.me_id):
            # Whitelistda bo'lmagan chatlarni e'tiborsiz qoldiramiz
            return

        # Agar xabar reply bo'lib, .stt buyrug'i yozilgan bo'lsa
        message_text = (event.raw_text or "").strip()
        if message_text.lower() == ".stt" and event.is_reply:
            reply_msg = await event.get_reply_message()
            if reply_msg and (reply_msg.voice or reply_msg.audio or reply_msg.video or reply_msg.video_note):
                await self.media_handler.handle_media(reply_msg, is_stt_only=True)
                return

        # Ovozli yoki media xabarlar (Voice / Audio / Video / Video Note / Photo)
        if event.voice or event.audio or event.video or event.video_note or event.photo:
            # Agar rasm yoki video bo'lib, matni bo'lsa ham media sifatida yuboramiz
            await self.media_handler.handle_media(event)
            return

        # Matnli xabar
        if message_text:
            await self.text_handler.handle_message(event, message_text)
