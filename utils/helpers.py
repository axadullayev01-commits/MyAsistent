import datetime


def print_banner():
    banner = """
==========================================================
        🤖 TELEGRAM AI ASSISTANT USERBOT 🤖
   - Engine: Google Gemini 1.5 (Multimodal & STT)
   - Client: Telethon (Async Userbot)
   - Database: SQLite Context Manager
==========================================================
    """
    print(banner)


def format_time(dt: datetime.datetime | None = None) -> str:
    """Vaqtni qulay formatda ko'rsatish."""
    if dt is None:
        dt = datetime.datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")
