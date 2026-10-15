import os
from pathlib import Path
from dotenv import load_dotenv

# Asosiy yo'l
BASE_DIR = Path(__file__).resolve().parent

# .env faylini yuklash
load_dotenv(BASE_DIR / ".env")

# Telegram API sozlamalari
API_ID_RAW = os.getenv("API_ID", "").strip()
API_ID = int(API_ID_RAW) if API_ID_RAW.isdigit() else None
API_HASH = os.getenv("API_HASH", "").strip()
SESSION_NAME = os.getenv("SESSION_NAME", "ai_userbot").strip()
STRING_SESSION = os.getenv("STRING_SESSION", "").strip()
PORT = int(os.getenv("PORT", "0"))

# Gemini API sozlamalari
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()

# Kontekst va xatti-harakat (Akkaunt egasining shaxsiy profili va qat'iy qoidalari)
DEFAULT_SYSTEM_INSTRUCTION = (
    "Sen ushbu Telegram akkaunt egasisan — tirik inson. Band odamsan va Telegramda qisqa, lo'nda va amaliy yozishasan. "
    "Yozish uslubing: o'zbek tili (kundalik Telegram yozishuv uslubi, lotin alifbosi). "
    "Ohanging: qisqa, aniq, amaliy, norasmiy, ortiqcha lutf-xushomadsiz (no fluff). Katta harflar va qat'iy tinish belgilariga qarab o'tirmaysan. "
    "Odatiy so'zlaring: 'hullas', 'bo'ldi', 'ko'ramiz', 'ishdaman', 'gaplashamiz', 'yokida'. "
    "QAT'IY QOIDALAR: "
    "1) 'Sizga qanday yordam bera olaman?', 'Hurmatli...' kabi robot yoki mijozlarga xizmat ko'rsatish uslubidagi gaplar QAT'IYAN TAQIQLANADI. "
    "2) Hech qanday kirish yoki xotima so'zlarsiz to'g'ridan-to'g'ri savolga javob ber. "
    "3) Javoblar juda qisqa bo'lsin (ko'pi bilan 1-2 gap), xuddi ish bilan band odam tezda yozgandek. "
    "4) Moliyaviy masalalar, qarz, jiddiy qarorlar yoki murakkab va'dalar haqida gap ketganda: "
    "'Hozir band edim, keyinroq o'zim yozvoraman' yoki 'Ko'rib chiqib o'zim javob beraman' deb javob ber."
)
SYSTEM_INSTRUCTION = os.getenv("SYSTEM_INSTRUCTION", DEFAULT_SYSTEM_INSTRUCTION)
MAX_HISTORY_LIMIT = int(os.getenv("MAX_HISTORY_LIMIT", "15"))

# Papkalar
DOWNLOADS_DIR = BASE_DIR / "downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = BASE_DIR / "database" / "chat_history.db"

# Boshlang'ich Whitelist chatlar
_initial_whitelist = set()
raw_whitelist = os.getenv("WHITELIST_CHATS", "me").strip()
for item in raw_whitelist.split(","):
    item = item.strip()
    if not item:
        continue
    if item.lower() == "me":
        _initial_whitelist.add("me")
    else:
        try:
            _initial_whitelist.add(int(item))
        except ValueError:
            _initial_whitelist.add(item)

WHITELIST_CHATS = _initial_whitelist


def is_chat_whitelisted(chat_id: int | str, my_id: int | None = None) -> bool:
    """Chat whitelistda bor-yo'qligini tekshiradi."""
    if "me" in WHITELIST_CHATS and my_id is not None and chat_id == my_id:
        return True
    if chat_id in WHITELIST_CHATS or str(chat_id) in WHITELIST_CHATS:
        return True
    try:
        if int(chat_id) in WHITELIST_CHATS:
            return True
    except (ValueError, TypeError):
        pass
    return False


def add_to_whitelist(chat_id: int | str) -> None:
    """Whitelistga yangi chat qo'shadi."""
    try:
        WHITELIST_CHATS.add(int(chat_id))
    except (ValueError, TypeError):
        WHITELIST_CHATS.add(str(chat_id))


def remove_from_whitelist(chat_id: int | str) -> bool:
    """Whitelistdan chatni o'chiradi."""
    removed = False
    try:
        cid_int = int(chat_id)
        if cid_int in WHITELIST_CHATS:
            WHITELIST_CHATS.remove(cid_int)
            removed = True
    except (ValueError, TypeError):
        pass
    if str(chat_id) in WHITELIST_CHATS:
        WHITELIST_CHATS.remove(str(chat_id))
        removed = True
    return removed
