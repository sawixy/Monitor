from abc import ABC, abstractmethod
import importlib

class ConfigFactory:
    REGISTRY = {
        "json": "config.json_config.JsonConfig",
        "db": "config.sqlite_config.SqliteConfig"
    }

    def __init__(self):
        self.config: ConfigSystem = None

    async def load_config(self, config_path: str):
        config_ext = config_path.split(".")[-1].lower()

        if config_ext not in self.REGISTRY:
            raise ValueError(f"Unsupported config format: {config_ext}")

        module_path, class_name = self.REGISTRY[config_ext].rsplit('.', 1)
        module = importlib.import_module(module_path)
        config_class = getattr(module, class_name)

        self.config = config_class()
        await self.config.load(config_path)

    def get_config(self) -> 'ConfigSystem':
        if self.config is None:
            raise ValueError("Config not loaded. Call load_config() first.")
        return self.config

class ConfigSystem(ABC):
    @abstractmethod
    async def load(self, path): pass

    @abstractmethod
    async def get(self, key): pass

    @abstractmethod
    async def set(self, key, value): pass

    @abstractmethod
    async def close(self): pass