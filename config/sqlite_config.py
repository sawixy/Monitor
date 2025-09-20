from aiosqlite import connect, Connection
from typing import override, Any, Optional
from .config import ConfigSystem

class SqliteConfig(ConfigSystem):
    def __init__(self):
        self.conn: Connection = None
        self.path: str = None
    
    @override
    async def load(self, path: str) -> None:
        self.path = path
        self.conn = await connect(path)
        cursor = await self.conn.cursor()
        await cursor.execute("""CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        await self.conn.commit()

    @override
    async def get(self, key: str) -> Optional[Any]:
        if not self.conn:
            raise ConnectionError("Database not connected. Call load() first.")
        
        cursor = await self.conn.cursor()
        await cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = await cursor.fetchone()
        return result[0] if result else None

    @override
    async def set(self, key: str, value: Any) -> None:
        if not self.conn:
            raise ConnectionError("Database not connected. Call load() first.")
        
        cursor = await self.conn.cursor()
        await cursor.execute(
            """INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)""",
            (key, str(value))
        )
        await self.conn.commit()

    @override
    async def close(self) -> None:
        if self.conn:
            await self.conn.close()
            self.conn = None