import aiofiles
import json
from typing import override, Any, Optional

from config.config import Config


class JsonConfig(Config):
    def __init__(self):
        self.data = {}
        self.path: Optional[str] = None

    @override
    async def load(self, path: str) -> None:
        try:
            async with aiofiles.open(path, 'r', encoding='utf-8') as file:
                content = await file.read()
                self.data = json.loads(content)
                self.path = path
        except FileNotFoundError:
            self.data = {}
            self.path = path
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON in {path}")

    @override
    async def get(self, key: str) -> Any:
        return self.data.get(key)

    @override
    async def set(self, key: str, value: Any) -> None:
        self.data[key] = value
        if self.path:
            await self.save(self.path)

    @override
    async def close(self) -> None:
        if self.path:
            await self.save(self.path)
        self.data = {}
        self.path = None

    async def save(self, path: str) -> None:
        async with aiofiles.open(path, 'w', encoding='utf-8') as file:
            content = json.dumps(self.data, ensure_ascii=False, indent=4)
            await file.write(content)