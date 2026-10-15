import os
import logging
from pathlib import Path
from typing import Optional, List
from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL, SYSTEM_INSTRUCTION
from database.context_manager import context_manager

logger = logging.getLogger(__name__)


class AIEngine:
    """Google Gemini asosidagi sun'iy intellekt dvigateli."""

    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model_name = GEMINI_MODEL or "gemini-3.5-flash-lite"
        self.client: Optional[genai.Client] = None
        if self.api_key:
            self._init_client()

    def _init_client(self):
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Google GenAI client muvaffaqiyatli ishga tushirildi.")
        except Exception as e:
            logger.error(f"GenAI mijozini yaratishda xatolik: {e}")
            self.client = None

    def reload_api_key(self, api_key: str):
        """Yangi API kalit o'rnatish."""
        self.api_key = api_key
        self._init_client()

    async def _generate_content_with_fallback(self, contents, config: types.GenerateContentConfig):
        """Asosiy model band yoki eskirgan bo'lsa, muqobil modellardan avtomatik foydalanish."""
        candidates = [self.model_name]
        for fallback in ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"]:
            if fallback not in candidates:
                candidates.append(fallback)

        last_error = None
        for model in candidates:
            try:
                response = await self.client.aio.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )
                if model != self.model_name:
                    logger.info(f"Model avtomatik ravishda '{model}' ga o'zgartirildi.")
                    self.model_name = model
                return response
            except Exception as e:
                last_error = e
                err_text = str(e).lower()
                if "404" in err_text or "503" in err_text or "not found" in err_text or "unavailable" in err_text:
                    logger.warning(f"Model '{model}' muammo berdi ({e}). Keyingi model sinab ko'rilmoqda...")
                    continue
                raise e

        raise last_error

    async def generate_text_response(self, chat_id: int | str, prompt: str) -> str:
        """Matnli so'rov uchun kontekstni hisobga olgan holda javob yaratish."""
        if not self.client:
            return "❌ Xatolik: GEMINI_API_KEY sozlanmagan. Iltimos, .env faylida API kalitni kiriting."

        try:
            # SQLite dan oldingi suhbat tarixini olish
            history_rows = await context_manager.get_history(chat_id)
            
            contents = []
            for item in history_rows:
                parts = [types.Part.from_text(text=p) for p in item["parts"]]
                contents.append(types.Content(role=item["role"], parts=parts))

            # Joriy yangi xabarni qo'shish
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            )

            # Gemini dan javob olish
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            )

            response = await self._generate_content_with_fallback(contents, config)

            reply_text = response.text or "Kechirasiz, javob generatsiya qilinmadi."

            # Xabarlarni tarixga saqlash
            await context_manager.add_message(chat_id, "user", prompt)
            await context_manager.add_message(chat_id, "model", reply_text)

            return reply_text

        except Exception as e:
            logger.error(f"AI javob yaratishda xatolik: {e}", exc_info=True)
            return f"⚠️ AI xatoligi: {str(e)}"

    async def generate_multimodal_response(
        self,
        chat_id: int | str,
        media_path: Path,
        prompt: Optional[str] = None,
        mime_type: Optional[str] = None
    ) -> str:
        """Ovoz, video yoki rasm fayli bilan ishlash va javob qaytarish."""
        if not self.client:
            return "❌ Xatolik: GEMINI_API_KEY sozlanmagan."

        uploaded_file = None
        try:
            # Faylni Gemini serveriga yuklash
            logger.info(f"Fayl Gemini serveriga yuklanmoqda: {media_path.name}")
            uploaded_file = await self.client.aio.files.upload(
                file=str(media_path),
                config=types.UploadFileConfig(mime_type=mime_type) if mime_type else None
            )

            # Tarixni olish
            history_rows = await context_manager.get_history(chat_id)
            contents = []
            for item in history_rows:
                parts = [types.Part.from_text(text=p) for p in item["parts"]]
                contents.append(types.Content(role=item["role"], parts=parts))

            user_prompt = prompt or "Ushbu media xabarni tahlil qiling va foydalanuvchiga to'liq javob bering."

            # Fayl va matnni birlashtirish
            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(
                            file_uri=uploaded_file.uri,
                            mime_type=uploaded_file.mime_type
                        ),
                        types.Part.from_text(text=user_prompt)
                    ]
                )
            )

            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
            )

            response = await self._generate_content_with_fallback(contents, config)

            reply_text = response.text or "Media tahlil qilindi, biroq javob bo'sh qaytdi."

            # Tarixga qo'shish
            log_prompt = f"[Media: {media_path.name}] {user_prompt}"
            await context_manager.add_message(chat_id, "user", log_prompt)
            await context_manager.add_message(chat_id, "model", reply_text)

            return reply_text

        except Exception as e:
            logger.error(f"Multimodal xatolik: {e}", exc_info=True)
            return f"⚠️ Media tahlilida xatolik: {str(e)}"
        finally:
            # Serverdagi vaqtinchalik yuklangan faylni o'chirish
            if uploaded_file and hasattr(uploaded_file, "name"):
                try:
                    await self.client.aio.files.delete(name=uploaded_file.name)
                except Exception as del_err:
                    logger.debug(f"Vaqtinchalik faylni o'chirishda ogohlantirish: {del_err}")

    async def speech_to_text(self, audio_path: Path) -> str:
        """Ovozli xabarni matnga o'girish (STT)."""
        if not self.client:
            return "❌ Xatolik: GEMINI_API_KEY sozlanmagan."

        uploaded_file = None
        try:
            uploaded_file = await self.client.aio.files.upload(file=str(audio_path))
            
            prompt = (
                "Ushbu audio yozuvdagi nutqni so'zma-so'z matnga o'giring (STT). "
                "Faqat va faqat eshitilgan matnni yozing, hech qanday qo'shimcha sharh yoki tushuntirish qo'shmang."
            )

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(file_uri=uploaded_file.uri, mime_type=uploaded_file.mime_type),
                        types.Part.from_text(text=prompt)
                    ]
                )
            ]
            config = types.GenerateContentConfig(temperature=0.2)

            response = await self._generate_content_with_fallback(contents, config)
            return response.text.strip() if response.text else "(Nutq aniqlanmadi)"

        except Exception as e:
            logger.error(f"STT xatolik: {e}", exc_info=True)
            return f"⚠️ Ovozni matnga o'girishda xatolik: {str(e)}"
        finally:
            if uploaded_file and hasattr(uploaded_file, "name"):
                try:
                    await self.client.aio.files.delete(name=uploaded_file.name)
                except Exception:
                    pass


ai_engine = AIEngine()
