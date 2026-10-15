import os
import uuid
import logging
from pathlib import Path
from telethon import events
from config import DOWNLOADS_DIR
from core.ai_engine import ai_engine
from core.ffmpeg_utils import ffmpeg_utils
from handlers.output_handler import OutputHandler

logger = logging.getLogger(__name__)


class MediaHandler:
    """Ovozli, video va boshqa multimedia xabarlarini qayta ishlash."""

    def __init__(self, output_handler: OutputHandler):
        self.output_handler = output_handler

    async def handle_media(self, event: events.NewMessage.Event, is_stt_only: bool = False):
        """Media faylni yuklab olish, FFmpeg orqali tayyorlash va AI ga yuborish."""
        chat_id = event.chat_id
        temp_file_path: Path | None = None
        converted_audio_path: Path | None = None

        try:
            # Fayl nomini generatsiya qilish
            unique_name = f"media_{uuid.uuid4().hex[:8]}"
            
            # Yuklab olinayotganini bildirish
            async with self.output_handler.client.action(chat_id, "record-audio" if event.voice else "typing"):
                download_target = DOWNLOADS_DIR / unique_name
                downloaded = await event.download_media(file=download_target)
                if not downloaded:
                    await self.output_handler.send_response(event, "⚠️ Media faylni yuklab olishda xatolik yuz berdi.")
                    return

                temp_file_path = Path(downloaded)

                # Agar video yoki dumaloq video (video_note) bo'lsa, audiosini ajratishimiz mumkin
                if event.video or event.video_note:
                    logger.info("Videodan audio ajratib olinmoqda...")
                    converted_audio_path = await ffmpeg_utils.extract_audio_from_video(temp_file_path)
                    media_for_ai = converted_audio_path
                    mime_type = "audio/mp3"
                elif event.voice or event.audio:
                    # Ovozli xabarni mp3 ga o'tkazish
                    converted_audio_path = await ffmpeg_utils.convert_to_mp3(temp_file_path)
                    media_for_ai = converted_audio_path
                    mime_type = "audio/mp3"
                else:
                    # Rasm yoki boshqa fayl
                    media_for_ai = temp_file_path
                    mime_type = None

                # Agar faqat ovozni matnga aylantirish (.stt) so'ralgan bo'lsa
                if is_stt_only:
                    transcript = await ai_engine.speech_to_text(media_for_ai)
                    await self.output_handler.send_response(
                        event,
                        f"🎙 **Ovozli xabar matni (STT):**\n\n_{transcript}_"
                    )
                    return

                # Qo'shimcha matn (caption yoki xabar matni)
                caption = event.text or "Iltimos, ushbu ovozli/media xabarni tinglab, to'liq javob bering."

                # AI dan javob generatsiya qilish
                response_text = await ai_engine.generate_multimodal_response(
                    chat_id=chat_id,
                    media_path=media_for_ai,
                    prompt=caption,
                    mime_type=mime_type
                )

            # Javobni yuborish
            await self.output_handler.send_response(event, response_text)

        except Exception as e:
            logger.error(f"Media qayta ishlashda xatolik: {e}", exc_info=True)
            await self.output_handler.send_response(event, f"⚠️ Media faylni tahlil qilishda xatolik: {str(e)}")

        finally:
            # Vaqtinchalik fayllarni tozalash (diskni to'ldirmaslik uchun)
            self._cleanup_files([temp_file_path, converted_audio_path])

    @staticmethod
    def _cleanup_files(paths: list[Path | None]):
        """Vaqtinchalik yuklangan va konvertatsiya qilingan fayllarni o'chirish."""
        for p in paths:
            if p and p.exists():
                try:
                    p.unlink()
                except Exception as err:
                    logger.debug(f"Faylni o'chirishda ogohlantirish: {err}")
