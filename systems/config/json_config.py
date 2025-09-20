import aiofiles
import json
from typing import override, Any
import asyncio

from systems.config.config import Config


class Json(Config):
    CONFIG_TYPE = "json"

    def __init__(self):
        self.data = {}

    @override
    async def load(self, path: str) -> None:
        try:
            async with aiofiles.open(path, 'r', encoding='utf-8') as file:
                content = await file.read()
                self.data = json.loads(content)
        except FileNotFoundError:
            raise Exception(f"File {path} not found")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON in {path}")

    @override
    async def get(self, name: str) -> Any:
        return self.data.get(name)

    @override
    async def save(self, path: str) -> None:
        async with aiofiles.open(path, 'w', encoding='utf-8') as file:
            content = json.dumps(self.data, ensure_ascii=False, indent=4)
            await file.write(content)