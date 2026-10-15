import datetime
import aiosqlite
from typing import List, Dict, Any
from config import DATABASE_PATH, MAX_HISTORY_LIMIT, add_to_whitelist, remove_from_whitelist


class ContextManager:
    """Chat tarixi va sozlamalarni SQLite yordamida boshqaruvchi Context Manager."""

    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = str(db_path)

    async def init_db(self) -> None:
        """Jadvallarni yaratish va boshlang'ich sozlash."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_id ON messages (chat_id)
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS whitelist (
                    chat_id TEXT PRIMARY KEY,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()

        # Saqlangan whitelistni xotiraga yuklash
        await self.load_whitelist()

    async def add_message(self, chat_id: int | str, role: str, content: str) -> None:
        """Chat tarixiga yangi xabar qo'shish (role: 'user' yoki 'model')."""
        # role Gemini formati: 'user' yoki 'model'
        gemini_role = "user" if role.lower() in ("user", "human") else "model"
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO messages (chat_id, role, content) VALUES (?, ?, ?)",
                (str(chat_id), gemini_role, content.strip())
            )
            await db.commit()

    async def get_history(self, chat_id: int | str, limit: int = MAX_HISTORY_LIMIT) -> List[Dict[str, Any]]:
        """Gemini formati uchun chat tarixini olish."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT role, content FROM messages 
                WHERE chat_id = ? 
                ORDER BY id DESC 
                LIMIT ?
                """,
                (str(chat_id), limit)
            )
            rows = await cursor.fetchall()
            
            # Xabarlarni xronologik tartibga keltiramiz (eskilari oldin)
            history = []
            for row in reversed(rows):
                history.append({
                    "role": row["role"],
                    "parts": [row["content"]]
                })
            return history

    async def clear_history(self, chat_id: int | str) -> int:
        """Berilgan chatning barcha tarixini tozalash."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM messages WHERE chat_id = ?", (str(chat_id),))
            await db.commit()
            return cursor.rowcount

    async def save_whitelisted_chat(self, chat_id: int | str) -> None:
        """Whitelistga chat qo'shish va bazaga saqlash."""
        add_to_whitelist(chat_id)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO whitelist (chat_id) VALUES (?)",
                (str(chat_id),)
            )
            await db.commit()

    async def remove_whitelisted_chat(self, chat_id: int | str) -> bool:
        """Whitelistdan chatni o'chirish."""
        removed = remove_from_whitelist(chat_id)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM whitelist WHERE chat_id = ?", (str(chat_id),))
            await db.commit()
        return removed

    async def load_whitelist(self) -> None:
        """Bazadagi barcha whitelist chatlarini yuklash."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT chat_id FROM whitelist")
            rows = await cursor.fetchall()
            for row in rows:
                add_to_whitelist(row[0])


# Global obyekt
context_manager = ContextManager()
