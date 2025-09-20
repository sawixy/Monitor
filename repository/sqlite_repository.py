from aiosqlite import connect
from typing import override, Optional, Tuple, List
from .repository import RepositorySystem

class SqliteRepository(RepositorySystem):
    """SQLite implementation"""

    @override
    async def init(self, path) -> None:
        self.conn = await connect(path)
        cursor = await self.conn.cursor()
        
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS sites(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                alias TEXT UNIQUE
            )
        """)
        
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS checks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alias TEXT,
                status INTEGER,
                error TEXT,
                time INTEGER,
                ssl_term BOOLEAN
            )
        """)
        
        await self.conn.commit()

    @override
    async def add_site(self, url: str, alias: str) -> None:
        cursor = await self.conn.cursor()
        if alias == None: alias = ""
        await cursor.execute(
            "INSERT INTO sites (url, alias) VALUES (?, ?)",
    (url, alias)
        )
        await self.conn.commit()

    @override
    async def add_check(self, alias: str, status: int, 
                      error: Optional[str], time: int, ssl_term: bool) -> None:
        cursor = await self.conn.cursor()
        await cursor.execute(
            "INSERT INTO checks (alias, status, error, time, ssl_term) VALUES (?, ?, ?, ?, ?)",
            (alias, status, error, time, ssl_term)
        )
        await self.conn.commit()

    @override
    async def delete_site(self, url: str) -> None:
        cursor = await self.conn.cursor()
        await cursor.execute("DELETE FROM sites WHERE url = ?", (url,))
        await self.conn.commit()

    @override
    async def delete_checks(self) -> None:
        cursor = await self.conn.cursor()
        await cursor.execute(
            "DELETE FROM checks",
        )
        await self.conn.commit()

    @override
    async def get_url(self, alias: str) -> str:
        cursor = await self.conn.cursor()
        await cursor.execute(
            "SELECT url FROM sites WHERE alias = ?",
            (alias,)
        )
        result = await cursor.fetchone()
        return result[0] if result else None

    @override
    async def get_check(self, check_id: int) -> Optional[Tuple]:
        cursor = await self.conn.cursor()
        await cursor.execute(
            "SELECT alias, status, error, time, ssl_term FROM checks WHERE id = ?",
            (check_id,)
        )
        return await cursor.fetchone()

    @override
    async def set_site(self, alias: str, new_url: str) -> None:
        cursor = await self.conn.cursor()
        await cursor.execute(
            "UPDATE sites SET url = ? WHERE alias = ?",
            (new_url, alias)
        )
        await self.conn.commit()

    @override
    async def get_all_sites(self) -> List[Tuple[str, str]]:
        cursor = await self.conn.cursor()
        await cursor.execute("SELECT url, alias FROM sites")
        return await cursor.fetchall()

    @override
    async def get_all_checks(self, alias: str) -> List[Tuple]:
        cursor = await self.conn.cursor()
        await cursor.execute(
            "SELECT id, status, error, time, ssl_term FROM checks WHERE alias = ?",
            (alias,)
        )
        return await cursor.fetchall()

    @override
    async def close(self) -> None:
        await self.conn.close()