from abc import ABC, abstractmethod

class ConfigFactory:
    REGISTRY = {
        "json": "systems.config.json_config.Json"
    }

    def __init__(self):
        self.config = Config

    def load_config(self, config_path):
        config_ext = config_path.split(".")[-1].lower()

        if config_ext not in self.REGISTRY:
            raise ValueError(f"Unsupported config format: {config_ext}")

        module_path, class_name = self.REGISTRY[config_ext].rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        config_class = getattr(module, class_name)

        self.config: Config = config_class(config_path)

    def get_config(self):
        return self.config

class Config(ABC):
    CONFIG_TYPE: str = ""

    @abstractmethod
    async def load(self, path): pass

    @abstractmethod
    async def get(self, name): pass

    @abstractmethod
    async def save(self, path: str): pass