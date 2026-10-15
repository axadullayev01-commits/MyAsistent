import logging
from telethon import events
from config import WHITELIST_CHATS, GEMINI_MODEL
from database.context_manager import context_manager
from core.ai_engine import ai_engine
from handlers.output_handler import OutputHandler

logger = logging.getLogger(__name__)


class TextHandler:
    """Matnli xabarlar va userbot buyruqlarini qayta ishlash."""

    def __init__(self, output_handler: OutputHandler):
        self.output_handler = output_handler

    async def handle_message(self, event: events.NewMessage.Event, text: str):
        """Matnli xabarni tahlil qilish va tegishli javob qaytarish."""
        cleaned_text = text.strip()

        # Buyruqlarni tekshirish (.help, .clear, .whitelist va boshqalar)
        if cleaned_text.startswith("."):
            handled = await self._handle_commands(event, cleaned_text)
            if handled:
                return

        chat_id = event.chat_id

        # Chatda "yozmoqda..." statusini ishga tushirish
        async with self.output_handler.client.action(chat_id, "typing"):
            # AI dan javob generatsiya qilish
            response_text = await ai_engine.generate_text_response(
                chat_id=chat_id,
                prompt=cleaned_text
            )

        # Javobni yuborish
        await self.output_handler.send_response(event, response_text)

    async def _handle_commands(self, event: events.NewMessage.Event, command_text: str) -> bool:
        """Userbot boshqaruv buyruqlarini bajarish."""
        parts = command_text.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in (".help", ".yordam"):
            help_message = (
                "🤖 **AI Asistent Userbot Buyruqlari:**\n\n"
                "• `.help` — Barcha buyruqlar ro'yxati\n"
                "• `.clear` yoki `.reset` — Ushbu chatdagi AI xotirasini tozalash\n"
                "• `.ping` — Bot holati va aloqani tekshirish\n"
                "• `.whitelist list` — Ruxsat etilgan chatlar ro'yxati\n"
                "• `.whitelist add [id]` — Chatni ruxsatnomaga qo'shish\n"
                "• `.whitelist remove [id]` — Chatni ruxsatnomadan o'chirish\n"
                "• `.stt` (ovozli xabarga reply qilib) — Ovozni matnga o'girish\n\n"
                "💡 _Shunchaki istalgan matn, ovozli xabar yoki video yuborsangiz, AI avtomatik javob qaytaradi!_"
            )
            await self.output_handler.send_response(event, help_message)
            return True

        if cmd in (".clear", ".reset", ".tozala"):
            count = await context_manager.clear_history(event.chat_id)
            await self.output_handler.send_response(
                event,
                f"🧹 Ushbu chatdagi AI xotirasi muvaffaqiyatli tozalandi! ({count} ta xabar o'chirildi)"
            )
            return True

        if cmd == ".ping":
            await self.output_handler.send_response(event, "🏓 Pong! AI Userbot faol va ishlayapti.")
            return True

        if cmd == ".whitelist":
            if not args or args[0].lower() == "list":
                chats = list(WHITELIST_CHATS)
                chats_str = "\n".join([f"• `{c}`" for c in chats]) if chats else "Bo'sh"
                await self.output_handler.send_response(
                    event,
                    f"📋 **Ruxsat etilgan chatlar (Whitelist):**\n\n{chats_str}"
                )
                return True

            subcmd = args[0].lower()
            target_id = None
            target_name = ""

            # 1. Agar xabarga reply qilib .whitelist add/remove yozilgan bo'lsa
            if event.is_reply and len(args) == 1:
                reply_msg = await event.get_reply_message()
                if reply_msg and reply_msg.sender_id:
                    target_id = reply_msg.sender_id
                    sender = await reply_msg.get_sender()
                    target_name = getattr(sender, "first_name", "") or getattr(sender, "title", "")

            # 2. Agar argument sifatida username yoki ID berilgan bo'lsa (.whitelist add @username)
            elif len(args) > 1:
                raw_arg = args[1]
                try:
                    entity = await self.output_handler.client.get_entity(raw_arg)
                    target_id = entity.id
                    target_name = getattr(entity, "first_name", "") or getattr(entity, "title", "")
                except Exception:
                    target_id = raw_arg

            # 3. Argument bo'lmasa — joriy chatning o'zi
            else:
                target_id = event.chat_id
                try:
                    chat_entity = await event.get_chat()
                    target_name = getattr(chat_entity, "first_name", "") or getattr(chat_entity, "title", "")
                except Exception:
                    pass

            display_str = f"'{target_name}' (ID: `{target_id}`)" if target_name else f"`{target_id}`"

            if subcmd == "add":
                await context_manager.save_whitelisted_chat(target_id)
                await self.output_handler.send_response(
                    event,
                    f"✅ Chat/Foydalanuvchi {display_str} whitelistga muvaffaqiyatli qo'shildi!"
                )
                return True

            if subcmd in ("remove", "del"):
                removed = await context_manager.remove_whitelisted_chat(target_id)
                if removed:
                    await self.output_handler.send_response(
                        event,
                        f"🗑 Chat/Foydalanuvchi {display_str} whitelistdan o'chirildi."
                    )
                else:
                    await self.output_handler.send_response(
                        event,
                        f"⚠️ Chat {display_str} whitelistda topilmadi."
                    )
                return True

        return False
